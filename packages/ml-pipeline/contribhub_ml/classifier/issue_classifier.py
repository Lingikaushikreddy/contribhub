"""
Issue classification using SetFit (few-shot) or LLM API fallback.

Classifies GitHub issues into category (bug, feature, question, docs, chore),
assigns priority P0-P3, and provides confidence + reasoning.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

logger = logging.getLogger(__name__)


class IssueCategory(str, Enum):
    """Supported issue categories."""

    BUG = "bug"
    FEATURE = "feature"
    QUESTION = "question"
    DOCS = "docs"
    CHORE = "chore"


class IssuePriority(str, Enum):
    """Supported priority levels."""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


@dataclass
class ClassificationResult:
    """Result returned by the issue classifier."""

    category: str
    priority: str
    confidence: float
    reasoning: str
    needs_review: bool = False
    raw_scores: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary."""
        return {
            "category": self.category,
            "priority": self.priority,
            "confidence": round(self.confidence, 4),
            "reasoning": self.reasoning,
            "needs_review": self.needs_review,
            "raw_scores": {k: round(v, 4) for k, v in self.raw_scores.items()},
        }


# ---------------------------------------------------------------------------
# Priority-inference keyword lists
# ---------------------------------------------------------------------------
_P0_KEYWORDS = frozenset([
    "crash", "data loss", "security", "vulnerability", "outage", "down",
    "production", "critical", "urgent", "broken", "cve",
])
_P1_KEYWORDS = frozenset([
    "error", "failure", "regression", "performance", "memory leak", "timeout",
    "500", "exception", "degraded",
])
_P2_KEYWORDS = frozenset([
    "enhancement", "improvement", "refactor", "update", "upgrade", "slow",
    "warning", "deprecation",
])

# ---------------------------------------------------------------------------
# System prompt used by the LLM-backed classifier
# ---------------------------------------------------------------------------
_CLASSIFICATION_SYSTEM_PROMPT = """\
You are an expert GitHub issue triaging system.  Classify the issue below into
exactly ONE of these categories: bug, feature, question, docs, chore.

Also assign a priority:
- P0: Critical — crashes, data loss, security issues, production outages
- P1: High    — errors, regressions, severe performance problems
- P2: Medium  — enhancements, moderate improvements, refactors
- P3: Low     — minor cosmetic, nice-to-haves, trivial chores

Return ONLY valid JSON (no markdown fences) with these keys:
{
  "category": "<bug|feature|question|docs|chore>",
  "priority": "<P0|P1|P2|P3>",
  "confidence": <float 0-1>,
  "reasoning": "<one sentence>"
}
"""


def _infer_priority(title: str, body: str) -> str:
    """Heuristic priority from keyword scanning."""
    combined = (title + " " + body).lower()
    for kw in _P0_KEYWORDS:
        if kw in combined:
            return IssuePriority.P0.value
    for kw in _P1_KEYWORDS:
        if kw in combined:
            return IssuePriority.P1.value
    for kw in _P2_KEYWORDS:
        if kw in combined:
            return IssuePriority.P2.value
    return IssuePriority.P3.value


class IssueClassifier:
    """Classify GitHub issues via SetFit (few-shot) or LLM API.

    Parameters
    ----------
    mode : "setfit" | "api"
        Which backend to use for inference.
    model_path : str | None
        Path or HuggingFace hub id for the SetFit model (only used when mode="setfit").
    api_provider : "openai" | "anthropic"
        Which LLM provider to call when mode="api".
    api_model : str | None
        Specific model name override. Defaults are ``gpt-4o`` (OpenAI)
        and ``claude-haiku-4-5-20251001`` (Anthropic).
    confidence_threshold : float
        Below this threshold the result is flagged ``needs_review=True``.
    """

    # Label mapping for SetFit integer outputs
    _LABEL_MAP: dict[int, str] = {
        0: IssueCategory.BUG.value,
        1: IssueCategory.FEATURE.value,
        2: IssueCategory.QUESTION.value,
        3: IssueCategory.DOCS.value,
        4: IssueCategory.CHORE.value,
    }

    def __init__(
        self,
        mode: Literal["setfit", "api"] = "api",
        model_path: str | None = None,
        api_provider: Literal["openai", "anthropic"] = "openai",
        api_model: str | None = None,
        confidence_threshold: float = 0.70,
    ) -> None:
        self.mode = mode
        self.model_path = model_path or "contribhub/issue-classifier-setfit"
        self.api_provider = api_provider
        self.confidence_threshold = confidence_threshold

        if api_model is not None:
            self.api_model = api_model
        elif api_provider == "openai":
            self.api_model = "gpt-4o"
        else:
            self.api_model = "claude-haiku-4-5-20251001"

        self._setfit_model: Any = None
        self._api_client: Any = None

    # ------------------------------------------------------------------
    # Lazy initialisation helpers
    # ------------------------------------------------------------------
    def _load_setfit_model(self) -> Any:
        """Load the SetFit model on first use."""
        if self._setfit_model is None:
            from setfit import SetFitModel  # type: ignore[import-untyped]

            logger.info("Loading SetFit model from %s", self.model_path)
            self._setfit_model = SetFitModel.from_pretrained(self.model_path)
        return self._setfit_model

    def _get_openai_client(self) -> Any:
        """Return an OpenAI client, creating one on first call."""
        if self._api_client is None:
            import openai

            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise EnvironmentError("OPENAI_API_KEY is not set")
            self._api_client = openai.OpenAI(api_key=api_key)
        return self._api_client

    def _get_anthropic_client(self) -> Any:
        """Return an Anthropic client, creating one on first call."""
        if self._api_client is None:
            import anthropic

            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise EnvironmentError("ANTHROPIC_API_KEY is not set")
            self._api_client = anthropic.Anthropic(api_key=api_key)
        return self._api_client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def classify(self, title: str, body: str) -> ClassificationResult:
        """Classify a GitHub issue.

        Parameters
        ----------
        title : str
            The issue title.
        body : str
            The issue body / description (may contain Markdown).

        Returns
        -------
        ClassificationResult
        """
        if self.mode == "setfit":
            return self._classify_setfit(title, body)
        return self._classify_api(title, body)

    # ------------------------------------------------------------------
    # SetFit path
    # ------------------------------------------------------------------
    def _classify_setfit(self, title: str, body: str) -> ClassificationResult:
        """Run classification through the local SetFit model."""
        import torch
        import numpy as np

        model = self._load_setfit_model()
        input_text = f"{title}\n\n{body}"

        # SetFit predict_proba returns an ndarray of shape (n_classes,)
        proba: np.ndarray = model.predict_proba([input_text])[0]

        # If model returns a tensor, convert
        if isinstance(proba, torch.Tensor):
            proba = proba.cpu().numpy()

        predicted_idx = int(np.argmax(proba))
        confidence = float(proba[predicted_idx])
        category = self._LABEL_MAP.get(predicted_idx, IssueCategory.CHORE.value)

        raw_scores = {
            self._LABEL_MAP[i]: float(proba[i]) for i in range(len(proba))
        }

        priority = _infer_priority(title, body)
        needs_review = confidence < self.confidence_threshold

        return ClassificationResult(
            category=category,
            priority=priority,
            confidence=confidence,
            reasoning=(
                f"SetFit model predicted '{category}' with {confidence:.1%} confidence."
            ),
            needs_review=needs_review,
            raw_scores=raw_scores,
        )

    # ------------------------------------------------------------------
    # API path (OpenAI / Anthropic)
    # ------------------------------------------------------------------
    def _classify_api(self, title: str, body: str) -> ClassificationResult:
        """Run classification through an LLM API."""
        user_content = f"Issue Title: {title}\n\nIssue Body:\n{body}"

        if self.api_provider == "openai":
            raw_json = self._call_openai(user_content)
        else:
            raw_json = self._call_anthropic(user_content)

        return self._parse_api_response(raw_json, title, body)

    def _call_openai(self, user_content: str) -> str:
        """Call OpenAI chat completion and return the raw text."""
        client = self._get_openai_client()
        response = client.chat.completions.create(
            model=self.api_model,
            temperature=0.1,
            messages=[
                {"role": "system", "content": _CLASSIFICATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
        return response.choices[0].message.content or "{}"

    def _call_anthropic(self, user_content: str) -> str:
        """Call Anthropic messages API and return the raw text."""
        client = self._get_anthropic_client()
        response = client.messages.create(
            model=self.api_model,
            max_tokens=256,
            temperature=0.1,
            system=_CLASSIFICATION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
        # Anthropic returns a list of content blocks
        text_parts = [
            block.text for block in response.content if hasattr(block, "text")
        ]
        return "".join(text_parts) or "{}"

    def _parse_api_response(
        self, raw: str, title: str, body: str
    ) -> ClassificationResult:
        """Parse the JSON response from the LLM, falling back to defaults."""
        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM JSON response: %s", raw[:200])
            return ClassificationResult(
                category=IssueCategory.CHORE.value,
                priority=_infer_priority(title, body),
                confidence=0.0,
                reasoning="LLM response could not be parsed; flagged for manual review.",
                needs_review=True,
            )

        category = data.get("category", "chore")
        if category not in {c.value for c in IssueCategory}:
            category = IssueCategory.CHORE.value

        priority = data.get("priority", _infer_priority(title, body))
        if priority not in {p.value for p in IssuePriority}:
            priority = _infer_priority(title, body)

        confidence = float(data.get("confidence", 0.0))
        confidence = max(0.0, min(1.0, confidence))

        reasoning = data.get("reasoning", "No reasoning provided by LLM.")
        needs_review = confidence < self.confidence_threshold

        return ClassificationResult(
            category=category,
            priority=priority,
            confidence=confidence,
            reasoning=reasoning,
            needs_review=needs_review,
        )
