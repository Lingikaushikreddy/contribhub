"""Tests for the IssueClassifier module."""

from __future__ import annotations

import json
import sys
from unittest.mock import MagicMock, patch

import pytest

from contribhub_ml.classifier.issue_classifier import (
    ClassificationResult,
    IssueCategory,
    IssuePriority,
    IssueClassifier,
    _infer_priority,
)


# ---------------------------------------------------------------------------
# Unit tests for _infer_priority helper
# ---------------------------------------------------------------------------


class TestInferPriority:
    """Tests for the keyword-based priority heuristic."""

    def test_p0_crash_keyword(self):
        assert _infer_priority("App crash on startup", "") == "P0"

    def test_p0_security_keyword(self):
        assert _infer_priority("", "Found a security vulnerability in auth") == "P0"

    def test_p0_cve_keyword(self):
        assert _infer_priority("CVE-2025-1234 disclosure", "") == "P0"

    def test_p1_error_keyword(self):
        assert _infer_priority("500 error on login", "") == "P1"

    def test_p1_regression_keyword(self):
        assert _infer_priority("", "This is a regression from v2.0") == "P1"

    def test_p2_enhancement_keyword(self):
        assert _infer_priority("enhancement: improve caching", "") == "P2"

    def test_p2_refactor_keyword(self):
        assert _infer_priority("", "We should refactor the auth module") == "P2"

    def test_p3_default(self):
        assert _infer_priority("Add a button", "Would be nice to have a dark mode") == "P3"

    def test_p0_takes_precedence_over_p1(self):
        """When both P0 and P1 keywords are present, P0 should win."""
        result = _infer_priority("crash with error on production", "")
        assert result == "P0"


# ---------------------------------------------------------------------------
# ClassificationResult dataclass
# ---------------------------------------------------------------------------


class TestClassificationResult:
    """Tests for the ClassificationResult data class."""

    def test_to_dict_round_trips(self):
        result = ClassificationResult(
            category="bug",
            priority="P1",
            confidence=0.87654,
            reasoning="Test reasoning",
            needs_review=False,
            raw_scores={"bug": 0.87654, "feature": 0.10001},
        )
        d = result.to_dict()
        assert d["category"] == "bug"
        assert d["priority"] == "P1"
        assert d["confidence"] == 0.8765
        assert d["needs_review"] is False
        assert d["raw_scores"]["bug"] == 0.8765
        assert d["raw_scores"]["feature"] == 0.1

    def test_default_needs_review_false(self):
        result = ClassificationResult(
            category="feature", priority="P2", confidence=0.9, reasoning="ok"
        )
        assert result.needs_review is False

    def test_default_raw_scores_empty(self):
        result = ClassificationResult(
            category="docs", priority="P3", confidence=0.5, reasoning="x"
        )
        assert result.raw_scores == {}


# ---------------------------------------------------------------------------
# IssueClassifier — API mode with OpenAI
# ---------------------------------------------------------------------------


class TestIssueClassifierOpenAI:
    """Tests for IssueClassifier using mocked OpenAI API."""

    def test_classify_bug(self, bug_issue, mock_openai_classification_response):
        """A bug issue should be classified as 'bug'."""
        classifier = IssueClassifier(mode="api", api_provider="openai")

        mock_response = mock_openai_classification_response(
            category="bug", priority="P0", confidence=0.95,
            reasoning="Crash with segfault indicates a critical bug.",
        )
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        classifier._api_client = mock_client

        result = classifier.classify(bug_issue["title"], bug_issue["body"])

        assert result.category == "bug"
        assert result.priority == "P0"
        assert result.confidence == 0.95
        assert result.needs_review is False
        mock_client.chat.completions.create.assert_called_once()

    def test_classify_feature(self, feature_issue, mock_openai_classification_response):
        """A feature request should be classified as 'feature'."""
        classifier = IssueClassifier(mode="api", api_provider="openai")

        mock_response = mock_openai_classification_response(
            category="feature", priority="P2", confidence=0.92,
            reasoning="Dark mode is a feature enhancement request.",
        )
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        classifier._api_client = mock_client

        result = classifier.classify(feature_issue["title"], feature_issue["body"])

        assert result.category == "feature"
        assert result.priority == "P2"
        assert result.confidence == 0.92
        assert result.needs_review is False

    def test_classify_question(self, question_issue, mock_openai_classification_response):
        """A question should be classified as 'question'."""
        classifier = IssueClassifier(mode="api", api_provider="openai")

        mock_response = mock_openai_classification_response(
            category="question", priority="P3", confidence=0.88,
            reasoning="User is asking for configuration help.",
        )
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        classifier._api_client = mock_client

        result = classifier.classify(question_issue["title"], question_issue["body"])

        assert result.category == "question"
        assert result.priority == "P3"

    def test_low_confidence_flags_needs_review(
        self, bug_issue, mock_openai_classification_response
    ):
        """When confidence is below threshold, needs_review should be True."""
        classifier = IssueClassifier(
            mode="api", api_provider="openai", confidence_threshold=0.80
        )

        mock_response = mock_openai_classification_response(
            category="bug", priority="P2", confidence=0.55,
            reasoning="Unclear if this is a bug or a feature request.",
        )
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        classifier._api_client = mock_client

        result = classifier.classify(bug_issue["title"], bug_issue["body"])

        assert result.needs_review is True
        assert result.confidence == 0.55

    def test_exactly_at_threshold_not_flagged(
        self, bug_issue, mock_openai_classification_response
    ):
        """Confidence exactly at threshold should NOT be flagged for review."""
        classifier = IssueClassifier(
            mode="api", api_provider="openai", confidence_threshold=0.70
        )

        mock_response = mock_openai_classification_response(
            category="bug", priority="P1", confidence=0.70,
            reasoning="Likely a bug.",
        )
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        classifier._api_client = mock_client

        result = classifier.classify(bug_issue["title"], bug_issue["body"])

        assert result.needs_review is False

    def test_malformed_json_response_falls_back(self, bug_issue):
        """If the LLM returns non-JSON, classifier should return a safe fallback."""
        classifier = IssueClassifier(mode="api", api_provider="openai")

        class _Message:
            content = "I cannot classify this issue properly."

        class _Choice:
            message = _Message()

        class _Response:
            choices = [_Choice()]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = _Response()
        classifier._api_client = mock_client

        result = classifier.classify(bug_issue["title"], bug_issue["body"])

        assert result.category == "chore"  # fallback category
        assert result.confidence == 0.0
        assert result.needs_review is True

    def test_invalid_category_defaults_to_chore(
        self, bug_issue, mock_openai_classification_response
    ):
        """If the LLM returns an invalid category, it should default to 'chore'."""
        classifier = IssueClassifier(mode="api", api_provider="openai")

        class _Message:
            content = json.dumps({
                "category": "not_a_real_category",
                "priority": "P1",
                "confidence": 0.85,
                "reasoning": "test",
            })

        class _Choice:
            message = _Message()

        class _Response:
            choices = [_Choice()]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = _Response()
        classifier._api_client = mock_client

        result = classifier.classify(bug_issue["title"], bug_issue["body"])

        assert result.category == "chore"

    def test_invalid_priority_falls_back_to_heuristic(
        self, bug_issue, mock_openai_classification_response
    ):
        """If the LLM returns an invalid priority, keyword heuristic is used."""
        classifier = IssueClassifier(mode="api", api_provider="openai")

        class _Message:
            content = json.dumps({
                "category": "bug",
                "priority": "URGENT",  # not a valid priority
                "confidence": 0.90,
                "reasoning": "test",
            })

        class _Choice:
            message = _Message()

        class _Response:
            choices = [_Choice()]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = _Response()
        classifier._api_client = mock_client

        result = classifier.classify(bug_issue["title"], bug_issue["body"])

        # "crash" in title => P0
        assert result.priority == "P0"

    def test_confidence_clamped_to_0_1(self, bug_issue):
        """Confidence values outside [0, 1] should be clamped."""
        classifier = IssueClassifier(mode="api", api_provider="openai")

        class _Message:
            content = json.dumps({
                "category": "bug",
                "priority": "P1",
                "confidence": 1.5,  # out of range
                "reasoning": "test",
            })

        class _Choice:
            message = _Message()

        class _Response:
            choices = [_Choice()]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = _Response()
        classifier._api_client = mock_client

        result = classifier.classify(bug_issue["title"], bug_issue["body"])

        assert result.confidence == 1.0

    def test_json_with_markdown_fences_parsed(self, bug_issue):
        """LLM response wrapped in ```json ... ``` should be parsed correctly."""
        classifier = IssueClassifier(mode="api", api_provider="openai")

        fenced_json = '```json\n{"category":"bug","priority":"P1","confidence":0.9,"reasoning":"test"}\n```'

        class _Message:
            content = fenced_json

        class _Choice:
            message = _Message()

        class _Response:
            choices = [_Choice()]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = _Response()
        classifier._api_client = mock_client

        result = classifier.classify(bug_issue["title"], bug_issue["body"])

        assert result.category == "bug"
        assert result.confidence == 0.9


# ---------------------------------------------------------------------------
# IssueClassifier — API mode with Anthropic
# ---------------------------------------------------------------------------


class TestIssueClassifierAnthropic:
    """Tests for IssueClassifier using mocked Anthropic API."""

    def test_classify_bug_anthropic(
        self, bug_issue, mock_anthropic_classification_response
    ):
        """Anthropic backend should classify bugs correctly."""
        classifier = IssueClassifier(mode="api", api_provider="anthropic")

        mock_response = mock_anthropic_classification_response(
            category="bug", priority="P0", confidence=0.93,
            reasoning="Segfault crash is a critical bug.",
        )
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        classifier._api_client = mock_client

        result = classifier.classify(bug_issue["title"], bug_issue["body"])

        assert result.category == "bug"
        assert result.priority == "P0"
        assert result.confidence == 0.93
        mock_client.messages.create.assert_called_once()

    def test_default_model_anthropic(self):
        """Default Anthropic model should be claude-haiku-4-5-20251001."""
        classifier = IssueClassifier(mode="api", api_provider="anthropic")
        assert classifier.api_model == "claude-haiku-4-5-20251001"

    def test_default_model_openai(self):
        """Default OpenAI model should be gpt-4o."""
        classifier = IssueClassifier(mode="api", api_provider="openai")
        assert classifier.api_model == "gpt-4o"

    def test_custom_model_override(self):
        """Explicit api_model overrides the default."""
        classifier = IssueClassifier(
            mode="api", api_provider="openai", api_model="gpt-4-turbo"
        )
        assert classifier.api_model == "gpt-4-turbo"


# ---------------------------------------------------------------------------
# IssueClassifier — constructor and lazy init
# ---------------------------------------------------------------------------


class TestIssueClassifierInit:
    """Tests for constructor defaults and lazy initialisation."""

    def test_default_mode_is_api(self):
        classifier = IssueClassifier()
        assert classifier.mode == "api"

    def test_default_confidence_threshold(self):
        classifier = IssueClassifier()
        assert classifier.confidence_threshold == 0.70

    def test_setfit_model_not_loaded_on_init(self):
        classifier = IssueClassifier(mode="setfit")
        assert classifier._setfit_model is None

    def test_api_client_not_created_on_init(self):
        classifier = IssueClassifier(mode="api")
        assert classifier._api_client is None

    def test_openai_key_required(self):
        """_get_openai_client should raise when OPENAI_API_KEY is unset."""
        classifier = IssueClassifier(mode="api", api_provider="openai")
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError, match="OPENAI_API_KEY"):
                classifier._get_openai_client()

    def test_anthropic_key_required(self):
        """_get_anthropic_client should raise when ANTHROPIC_API_KEY is unset."""
        classifier = IssueClassifier(mode="api", api_provider="anthropic")

        # Mock the anthropic module so the import succeeds even if not installed
        mock_anthropic_mod = MagicMock()
        with patch.dict("sys.modules", {"anthropic": mock_anthropic_mod}):
            with patch.dict("os.environ", {}, clear=True):
                with pytest.raises(EnvironmentError, match="ANTHROPIC_API_KEY"):
                    classifier._get_anthropic_client()


# ---------------------------------------------------------------------------
# Enum coverage
# ---------------------------------------------------------------------------


class TestEnums:
    """Tests for IssueCategory and IssuePriority enums."""

    def test_all_categories_exist(self):
        assert set(IssueCategory) == {
            IssueCategory.BUG,
            IssueCategory.FEATURE,
            IssueCategory.QUESTION,
            IssueCategory.DOCS,
            IssueCategory.CHORE,
        }

    def test_all_priorities_exist(self):
        assert set(IssuePriority) == {
            IssuePriority.P0,
            IssuePriority.P1,
            IssuePriority.P2,
            IssuePriority.P3,
        }

    def test_category_values(self):
        assert IssueCategory.BUG.value == "bug"
        assert IssueCategory.FEATURE.value == "feature"

    def test_priority_values(self):
        assert IssuePriority.P0.value == "P0"
        assert IssuePriority.P3.value == "P3"
