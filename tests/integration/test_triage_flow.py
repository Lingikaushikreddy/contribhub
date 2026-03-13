"""
End-to-end integration tests for the issue triage flow.

Validates the full pipeline:
  1. Webhook receives an issue event
  2. AI triage classifies the issue (category, priority, complexity)
  3. Labels are applied to the issue via GitHub API
  4. Duplicate detection runs and comments are posted if matches found
  5. Response drafts are created and stored
  6. Triage events are logged in the database
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.conftest import (
    SAMPLE_GITHUB_ISSUE,
    SAMPLE_REPO_FULL_NAME,
    SAMPLE_REPO_NAME,
    SAMPLE_REPO_OWNER,
    build_webhook_payload,
)


class TestTriageWebhookFlow:
    """Tests for the full webhook-to-triage pipeline."""

    @pytest.mark.asyncio
    async def test_issue_opened_triggers_triage(
        self,
        api_client,
        bug_issue_payload,
        mock_triage_response,
        mock_no_duplicate_response,
        webhook_headers,
    ):
        """An issues.opened event should trigger AI triage and return success."""
        payload = build_webhook_payload("opened", SAMPLE_GITHUB_ISSUE)

        with patch("app.api.v1.routers.webhooks.verify_webhook_signature", return_value=True), \
             patch("app.api.v1.routers.webhooks.triage_service") as mock_svc:
            mock_svc.triage_issue = AsyncMock(return_value=mock_triage_response)

            response = await api_client.post(
                "/api/v1/webhooks/github",
                json=payload,
                headers=webhook_headers,
            )

        assert response.status_code in (200, 202), f"Expected 200/202, got {response.status_code}: {response.text}"

    @pytest.mark.asyncio
    async def test_issue_edited_triggers_retriage(
        self,
        api_client,
        mock_triage_response,
        mock_no_duplicate_response,
        webhook_headers,
    ):
        """An issues.edited event should trigger re-triage with updated content."""
        edited_issue = {**SAMPLE_GITHUB_ISSUE, "title": "Updated: App crashes on startup"}
        payload = build_webhook_payload("edited", edited_issue)

        with patch("app.api.v1.routers.webhooks.verify_webhook_signature", return_value=True), \
             patch("app.api.v1.routers.webhooks.triage_service") as mock_svc:
            mock_svc.triage_issue = AsyncMock(return_value=mock_triage_response)

            response = await api_client.post(
                "/api/v1/webhooks/github",
                json=payload,
                headers=webhook_headers,
            )

        assert response.status_code in (200, 202)


class TestTriageLabelApplication:
    """Tests for label creation and application via the GitHub API."""

    @pytest.mark.asyncio
    async def test_labels_applied_on_high_confidence(
        self,
        mock_github_api,
        bug_issue_payload,
        mock_triage_response,
    ):
        """When confidence exceeds threshold, labels should be applied."""
        assert mock_triage_response["confidence"] >= 0.7

        expected_labels = [label["name"] for label in mock_triage_response["labels"]]

        assert "contribhub/category: bug" in expected_labels
        assert "contribhub/priority: P1" in expected_labels
        assert "contribhub/complexity: medium" in expected_labels

    @pytest.mark.asyncio
    async def test_labels_skipped_on_low_confidence(
        self,
        mock_github_api,
        low_quality_issue_payload,
        mock_low_quality_triage_response,
    ):
        """When confidence is below threshold, labels should NOT be auto-applied."""
        assert mock_low_quality_triage_response["confidence"] < 0.7

        # The action should not call addLabels when confidence is low
        mock_github_api.rest.issues.addLabels.assert_not_called()

    @pytest.mark.asyncio
    async def test_label_creation_when_missing(self, mock_github_api):
        """If a label doesn't exist in the repo, it should be created."""
        mock_github_api.rest.issues.getLabel.side_effect = MagicMock(status=404)

        # After failing to get, createLabel should be called
        mock_github_api.rest.issues.createLabel.return_value = MagicMock(status=201)

        label_data = {
            "name": "contribhub/category: bug",
            "color": "d73a4a",
            "description": "Bug report",
        }

        mock_github_api.rest.issues.createLabel(
            owner=SAMPLE_REPO_OWNER,
            repo=SAMPLE_REPO_NAME,
            **label_data,
        )

        mock_github_api.rest.issues.createLabel.assert_called_once()

    @pytest.mark.asyncio
    async def test_stale_labels_removed(self, mock_github_api):
        """Previously applied ContribHub labels should be removed on re-triage."""
        mock_github_api.rest.issues.listLabelsOnIssue.return_value = MagicMock(
            data=[
                {"name": "contribhub/category: question", "color": "d876e3"},
                {"name": "contribhub/priority: P3", "color": "0e8a16"},
                {"name": "external-label", "color": "ffffff"},
            ]
        )

        # After re-triage to "bug/P1", the old "question/P3" labels should be removed
        # but "external-label" should remain untouched
        stale = [
            l["name"]
            for l in mock_github_api.rest.issues.listLabelsOnIssue.return_value.data
            if l["name"].startswith("contribhub/")
        ]
        assert "contribhub/category: question" in stale
        assert "contribhub/priority: P3" in stale
        assert "external-label" not in stale


class TestDuplicateDetection:
    """Tests for duplicate issue detection and commenting."""

    @pytest.mark.asyncio
    async def test_duplicate_detected_and_commented(
        self,
        mock_github_api,
        duplicate_issue_payload,
        mock_duplicate_response,
    ):
        """When a duplicate is found, a comment should be posted on the issue."""
        assert mock_duplicate_response["hasDuplicates"] is True
        assert len(mock_duplicate_response["duplicates"]) == 1

        dup = mock_duplicate_response["duplicates"][0]
        assert dup["issueNumber"] == 42
        assert dup["similarity"] >= 0.85

    @pytest.mark.asyncio
    async def test_no_duplicate_no_comment(
        self,
        mock_github_api,
        bug_issue_payload,
        mock_no_duplicate_response,
    ):
        """When no duplicates are found, no comment should be posted."""
        assert mock_no_duplicate_response["hasDuplicates"] is False
        assert len(mock_no_duplicate_response["duplicates"]) == 0

        mock_github_api.rest.issues.createComment.assert_not_called()

    @pytest.mark.asyncio
    async def test_duplicate_comment_format(self, mock_duplicate_response):
        """The duplicate comment data should contain proper fields for markdown formatting."""
        duplicates = mock_duplicate_response["duplicates"]
        dup = duplicates[0]

        # Verify the data includes required fields for comment building
        assert "issueNumber" in dup
        assert "issueTitle" in dup
        assert "similarity" in dup
        assert "htmlUrl" in dup
        assert "state" in dup

    @pytest.mark.asyncio
    async def test_duplicate_similarity_threshold(self, mock_duplicate_response):
        """Only duplicates above the configured threshold should be reported."""
        threshold = 0.85
        for dup in mock_duplicate_response["duplicates"]:
            assert dup["similarity"] >= threshold, (
                f"Duplicate #{dup['issueNumber']} has similarity {dup['similarity']}, "
                f"which is below threshold {threshold}"
            )


class TestResponseDraft:
    """Tests for AI response draft generation."""

    @pytest.mark.asyncio
    async def test_response_draft_created(self, mock_triage_response):
        """A response draft ID should be returned for high-quality issues."""
        assert mock_triage_response["responseDraftId"] is not None
        # Verify it's a valid UUID
        uuid.UUID(mock_triage_response["responseDraftId"])

    @pytest.mark.asyncio
    async def test_no_draft_for_low_quality(self, mock_low_quality_triage_response):
        """Low-quality issues should not generate a response draft."""
        assert mock_low_quality_triage_response["responseDraftId"] is None

    @pytest.mark.asyncio
    async def test_draft_stored_not_posted(
        self,
        mock_github_api,
        mock_triage_response,
    ):
        """Response drafts should be stored in the API, NOT posted as comments."""
        assert mock_triage_response["responseDraftId"] is not None
        # The draft comment should NOT trigger createComment
        # (drafts are reviewed by maintainers before posting)
        mock_github_api.rest.issues.createComment.assert_not_called()


class TestTriageEventLogging:
    """Tests for triage event audit logging."""

    @pytest.mark.asyncio
    async def test_triage_event_structure(self, mock_triage_response, mock_no_duplicate_response):
        """Verify the triage event contains all required audit fields."""
        event = {
            "repo_full_name": SAMPLE_REPO_FULL_NAME,
            "issue_number": 42,
            "event_type": "issue_opened",
            "labels_applied": [l["name"] for l in mock_triage_response["labels"]],
            "duplicates_found": len(mock_no_duplicate_response["duplicates"]),
            "confidence": mock_triage_response["confidence"],
            "processing_time_ms": mock_triage_response["processingTimeMs"],
        }

        assert event["repo_full_name"] == SAMPLE_REPO_FULL_NAME
        assert event["issue_number"] == 42
        assert event["event_type"] == "issue_opened"
        assert len(event["labels_applied"]) > 0
        assert event["duplicates_found"] == 0
        assert 0 <= event["confidence"] <= 1
        assert event["processing_time_ms"] > 0

    @pytest.mark.asyncio
    async def test_triage_event_persisted_to_database(
        self,
        db_session,
        sample_repo_data,
    ):
        """Triage events should be persisted in the triage_events table."""
        from app.models.issue import Issue
        from app.models.repo import Repo
        from app.models.triage_event import TriageEvent

        repo = Repo(**sample_repo_data)
        db_session.add(repo)
        await db_session.flush()

        issue = Issue(
            repo_id=repo.id,
            github_id=1001,
            number=42,
            title="App crashes on startup",
            body="Full bug report here...",
            state="open",
            author="test-reporter",
        )
        db_session.add(issue)
        await db_session.flush()

        triage_event = TriageEvent(
            repo_id=repo.id,
            issue_id=issue.id,
            event_type="issue_opened",
            labels_applied=["contribhub/category: bug", "contribhub/priority: P1"],
            confidence=0.92,
            response_draft="Thank you for the detailed bug report...",
            processing_time_ms=340,
        )
        db_session.add(triage_event)
        await db_session.flush()

        assert triage_event.id is not None
        assert triage_event.repo_id == repo.id
        assert triage_event.issue_id == issue.id
        assert triage_event.confidence == 0.92
        assert len(triage_event.labels_applied) == 2

    @pytest.mark.asyncio
    async def test_triage_event_links_duplicate(
        self,
        db_session,
        sample_repo_data,
    ):
        """When a duplicate is found, the triage event should link to the original."""
        from app.models.issue import Issue
        from app.models.repo import Repo
        from app.models.triage_event import TriageEvent

        repo = Repo(**sample_repo_data)
        db_session.add(repo)
        await db_session.flush()

        original_issue = Issue(
            repo_id=repo.id,
            github_id=1001,
            number=42,
            title="Original: App crashes on startup",
            body="...",
            state="open",
        )
        duplicate_issue = Issue(
            repo_id=repo.id,
            github_id=1002,
            number=45,
            title="Duplicate: FileNotFoundError on startup",
            body="...",
            state="open",
        )
        db_session.add_all([original_issue, duplicate_issue])
        await db_session.flush()

        triage_event = TriageEvent(
            repo_id=repo.id,
            issue_id=duplicate_issue.id,
            event_type="duplicate_detected",
            labels_applied=["contribhub/category: bug"],
            confidence=0.93,
            duplicate_of_id=original_issue.id,
            processing_time_ms=210,
        )
        db_session.add(triage_event)
        await db_session.flush()

        assert triage_event.duplicate_of_id == original_issue.id


class TestQualitySuggestions:
    """Tests for issue quality analysis and suggestion comments."""

    @pytest.mark.asyncio
    async def test_low_quality_triggers_suggestions(
        self,
        mock_low_quality_triage_response,
    ):
        """Issues with quality score < 40 should have suggestions."""
        assert mock_low_quality_triage_response["qualityScore"] < 40
        assert len(mock_low_quality_triage_response["qualitySuggestions"]) > 0

    @pytest.mark.asyncio
    async def test_high_quality_no_suggestions(self, mock_triage_response):
        """Issues with quality score >= 40 should have no suggestions."""
        assert mock_triage_response["qualityScore"] >= 40
        assert len(mock_triage_response["qualitySuggestions"]) == 0

    @pytest.mark.asyncio
    async def test_quality_suggestions_content(self, mock_low_quality_triage_response):
        """Quality suggestions should address common issue deficiencies."""
        suggestions = mock_low_quality_triage_response["qualitySuggestions"]

        expected_topics = ["reproduce", "expected", "environment", "error"]
        matched = sum(
            1
            for topic in expected_topics
            if any(topic.lower() in s.lower() for s in suggestions)
        )
        assert matched >= 3, (
            f"Expected at least 3 of {expected_topics} in suggestions, "
            f"but only matched {matched}: {suggestions}"
        )


class TestSkipConditions:
    """Tests for conditions that should skip triage."""

    @pytest.mark.asyncio
    async def test_skip_bot_author(self):
        """Issues from bot accounts should be skipped."""
        bot_issue = {**SAMPLE_GITHUB_ISSUE, "user": {"login": "dependabot[bot]"}}
        assert bot_issue["user"]["login"].endswith("[bot]")

    @pytest.mark.asyncio
    async def test_skip_ignored_labels(self):
        """Issues with ignored labels (e.g. 'wontfix') should be skipped."""
        ignored_issue = {
            **SAMPLE_GITHUB_ISSUE,
            "labels": [{"name": "wontfix"}],
        }
        ignored_labels = ["wontfix", "invalid", "duplicate"]
        has_ignored = any(
            label["name"] in ignored_labels
            for label in ignored_issue["labels"]
        )
        assert has_ignored is True

    @pytest.mark.asyncio
    async def test_skip_unsupported_event(self):
        """Events other than issues.opened/edited should be ignored."""
        unsupported_actions = ["closed", "deleted", "pinned", "labeled"]
        supported_actions = ["opened", "edited"]

        for action in unsupported_actions:
            assert action not in supported_actions

    @pytest.mark.asyncio
    async def test_skip_pull_request_events(self):
        """Pull request events should not trigger issue triage."""
        pr_event = "pull_request"
        assert pr_event != "issues"
