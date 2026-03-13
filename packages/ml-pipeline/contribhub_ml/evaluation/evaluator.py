"""
Model evaluation utilities for the issue classifier.

Loads a golden test set, runs model inference, and computes per-class
and macro metrics using scikit-learn.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

logger = logging.getLogger(__name__)

_DEFAULT_GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.json"


@dataclass
class EvalResult:
    """Evaluation metrics for a classification model."""

    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    per_class: dict[str, dict[str, float]] = field(default_factory=dict)
    confusion_matrix: list[list[int]] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    num_examples: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "accuracy": round(self.accuracy, 4),
            "precision_macro": round(self.precision_macro, 4),
            "recall_macro": round(self.recall_macro, 4),
            "f1_macro": round(self.f1_macro, 4),
            "per_class": {
                cls: {k: round(v, 4) for k, v in metrics.items()}
                for cls, metrics in self.per_class.items()
            },
            "confusion_matrix": self.confusion_matrix,
            "labels": self.labels,
            "num_examples": self.num_examples,
        }

    def to_mlflow_metrics(self) -> dict[str, float]:
        """Flatten metrics for MLflow logging."""
        metrics: dict[str, float] = {
            "accuracy": self.accuracy,
            "precision_macro": self.precision_macro,
            "recall_macro": self.recall_macro,
            "f1_macro": self.f1_macro,
        }
        for cls, cls_metrics in self.per_class.items():
            for metric_name, value in cls_metrics.items():
                metrics[f"{cls}_{metric_name}"] = value
        return metrics


class ModelEvaluator:
    """Evaluate an ``IssueClassifier`` against a golden test set.

    Parameters
    ----------
    golden_set_path : str | Path | None
        Path to the golden test set JSON file.  Uses the bundled
        ``golden_set.json`` by default.
    """

    def __init__(self, golden_set_path: str | Path | None = None) -> None:
        if golden_set_path is None:
            self.golden_set_path = _DEFAULT_GOLDEN_SET_PATH
        else:
            self.golden_set_path = Path(golden_set_path)

    def load_golden_set(self) -> list[dict[str, Any]]:
        """Load and return the golden test set."""
        with open(self.golden_set_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and "examples" in data:
            return data["examples"]
        if isinstance(data, list):
            return data
        raise ValueError(
            f"Unexpected golden set format in {self.golden_set_path}"
        )

    def evaluate(
        self,
        model: Any,
        test_set: list[dict[str, Any]] | None = None,
    ) -> EvalResult:
        """Run the model on every test example and compute metrics.

        Parameters
        ----------
        model : IssueClassifier
            A classifier instance with a ``classify(title, body)`` method.
        test_set : list[dict] | None
            Override test set.  Each dict must have ``title``, ``body``,
            and ``expected_category``.  If ``None``, loads the golden set.

        Returns
        -------
        EvalResult
        """
        if test_set is None:
            test_set = self.load_golden_set()

        y_true: list[str] = []
        y_pred: list[str] = []
        errors: list[dict[str, Any]] = []

        for example in test_set:
            title = example["title"]
            body = example["body"]
            expected = example["expected_category"]

            try:
                result = model.classify(title, body)
                predicted = result.category
            except Exception as exc:
                logger.error(
                    "Classifier error on '%s': %s", title[:60], exc
                )
                predicted = "error"
                errors.append({"title": title, "error": str(exc)})

            y_true.append(expected)
            y_pred.append(predicted)

        # Determine label set (sorted for deterministic order)
        labels = sorted(set(y_true) | set(y_pred))

        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)
        rec = recall_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)
        f1 = f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)

        cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()

        # Per-class metrics from classification_report
        report = classification_report(
            y_true, y_pred, labels=labels, output_dict=True, zero_division=0
        )
        per_class: dict[str, dict[str, float]] = {}
        for label in labels:
            if label in report:
                per_class[label] = {
                    "precision": report[label]["precision"],
                    "recall": report[label]["recall"],
                    "f1": report[label]["f1-score"],
                    "support": report[label]["support"],
                }

        if errors:
            logger.warning(
                "%d/%d examples caused classifier errors.", len(errors), len(test_set)
            )

        return EvalResult(
            accuracy=float(acc),
            precision_macro=float(prec),
            recall_macro=float(rec),
            f1_macro=float(f1),
            per_class=per_class,
            confusion_matrix=cm,
            labels=labels,
            num_examples=len(test_set),
        )
