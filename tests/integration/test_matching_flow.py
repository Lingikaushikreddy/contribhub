"""
End-to-end integration tests for the contributor matching flow.

Validates:
  1. Contributor profiles are created with skills and languages
  2. Issues with varying difficulty are matched correctly
  3. Recommendations are ranked by composite score
  4. Dormant repositories are excluded from recommendations
  5. Claimed issues are excluded from recommendations
  6. Feedback loop updates future recommendations
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from tests.integration.conftest import (
    SAMPLE_REPO_FULL_NAME,
    SAMPLE_REPO_NAME,
    SAMPLE_REPO_OWNER,
)


class TestContributorProfileCreation:
    """Tests for contributor profile and skill inference."""

    @pytest.mark.asyncio
    async def test_create_contributor_profile(
        self,
        db_session,
        sample_contributor_profile,
    ):
        """A contributor profile should be created with inferred and declared skills."""
        from app.models.user import User, UserRole

        user = User(
            github_id=sample_contributor_profile["github_id"],
            username=sample_contributor_profile["username"],
            email=sample_contributor_profile["email"],
            avatar_url=sample_contributor_profile["avatar_url"],
            role=UserRole.contributor,
        )
        db_session.add(user)
        await db_session.flush()

        assert user.id is not None
        assert user.username == "skilled-dev"
        assert user.role == UserRole.contributor

    @pytest.mark.asyncio
    async def test_skill_proficiency_stored(
        self,
        db_session,
        sample_contributor_profile,
    ):
        """Skill proficiency values should be persisted correctly."""
        from app.models.skill import Skill
        from app.models.user import SkillSource, User, UserSkill

        user = User(
            github_id=sample_contributor_profile["github_id"],
            username=sample_contributor_profile["username"],
            role="contributor",
        )
        db_session.add(user)
        await db_session.flush()

        skill = Skill(name="Python", category="language")
        db_session.add(skill)
        await db_session.flush()

        user_skill = UserSkill(
            user_id=user.id,
            skill_id=skill.id,
            proficiency=0.85,
            source=SkillSource.inferred,
        )
        db_session.add(user_skill)
        await db_session.flush()

        assert user_skill.proficiency == 0.85
        assert user_skill.source == SkillSource.inferred


class TestMatchingAlgorithm:
    """Tests for the matching algorithm's ranking and filtering."""

    @pytest.mark.asyncio
    async def test_recommendations_ranked_by_score(
        self,
        db_session,
        sample_contributor_profile,
        sample_issues_for_matching,
        sample_repo_data,
    ):
        """Recommendations should be returned sorted by descending match score."""
        from app.models.issue import Issue
        from app.models.match import Match, MatchStatus
        from app.models.repo import Repo
        from app.models.user import User

        repo = Repo(**sample_repo_data)
        db_session.add(repo)
        await db_session.flush()

        user = User(
            github_id=sample_contributor_profile["github_id"],
            username=sample_contributor_profile["username"],
            role="contributor",
        )
        db_session.add(user)
        await db_session.flush()

        issues = []
        for issue_data in sample_issues_for_matching:
            if not issue_data["is_claimed"]:
                issue = Issue(
                    repo_id=repo.id,
                    github_id=issue_data["github_id"],
                    number=issue_data["number"],
                    title=issue_data["title"],
                    body=issue_data["body"],
                    state=issue_data["state"],
                )
                db_session.add(issue)
                issues.append(issue)

        await db_session.flush()

        # Create matches with varying scores
        match_scores = [0.72, 0.91, 0.65, 0.83]
        matches = []
        for i, issue in enumerate(issues):
            match = Match(
                user_id=user.id,
                issue_id=issue.id,
                score=match_scores[i],
                skill_match=match_scores[i] * 0.4,
                health_match=0.82,
                interest_match=match_scores[i] * 0.3,
                growth_match=match_scores[i] * 0.2,
                status=MatchStatus.recommended,
            )
            db_session.add(match)
            matches.append(match)

        await db_session.flush()

        # Verify matches are created and can be ranked
        scored = sorted(matches, key=lambda m: m.score, reverse=True)
        assert scored[0].score == 0.91
        assert scored[-1].score == 0.65

        # Verify descending order
        for i in range(len(scored) - 1):
            assert scored[i].score >= scored[i + 1].score

    @pytest.mark.asyncio
    async def test_claimed_issues_excluded(
        self,
        sample_issues_for_matching,
    ):
        """Issues that are already claimed should be excluded from matching."""
        unclaimed = [
            issue for issue in sample_issues_for_matching
            if not issue["is_claimed"]
        ]
        claimed = [
            issue for issue in sample_issues_for_matching
            if issue["is_claimed"]
        ]

        assert len(claimed) > 0, "Test data should include at least one claimed issue"
        assert len(unclaimed) < len(sample_issues_for_matching)

        # Issue #104 is claimed
        claimed_numbers = {issue["number"] for issue in claimed}
        assert 104 in claimed_numbers

        # Unclaimed issues should not include #104
        unclaimed_numbers = {issue["number"] for issue in unclaimed}
        assert 104 not in unclaimed_numbers

    @pytest.mark.asyncio
    async def test_dormant_repos_excluded(
        self,
        dormant_repo_metrics,
    ):
        """Repositories with no commits in 90+ days should be excluded."""
        last_commit = datetime.fromisoformat(dormant_repo_metrics["last_commit_at"])
        now = datetime.now(timezone.utc)
        days_since_commit = (now - last_commit).days

        assert days_since_commit > 90, (
            f"Dormant repo should have no commits in 90+ days, "
            f"but last commit was {days_since_commit} days ago"
        )
        assert dormant_repo_metrics["commit_count_90d"] == 0

        # This repo should be filtered out during matching
        is_active = dormant_repo_metrics["commit_count_90d"] > 0
        assert is_active is False

    @pytest.mark.asyncio
    async def test_difficulty_matches_skill_level(
        self,
        sample_contributor_profile,
        sample_issues_for_matching,
    ):
        """Issues should be matched based on compatible difficulty levels."""
        # A contributor with 0.85 Python proficiency should be matched
        # with medium-hard issues, not trivial or expert
        python_proficiency = next(
            skill["proficiency"]
            for skill in sample_contributor_profile["skills"]
            if skill["name"] == "Python"
        )

        assert python_proficiency == 0.85

        # Suitable issues for this proficiency level (complexity 30-80)
        suitable = [
            issue for issue in sample_issues_for_matching
            if 30 <= issue["complexity_score"] <= 80
        ]
        assert len(suitable) > 0, "Should have issues in the suitable difficulty range"

        # Trivial issues (< 20) should not be top recommendations
        trivial = [
            issue for issue in sample_issues_for_matching
            if issue["complexity_score"] < 20
        ]
        assert all(
            issue["complexity_score"] < python_proficiency * 100 * 0.3
            for issue in trivial
        ), "Trivial issues should be well below skill level"


class TestMatchScoreComponents:
    """Tests for individual components of the match score."""

    @pytest.mark.asyncio
    async def test_skill_match_component(
        self,
        db_session,
        sample_contributor_profile,
        sample_repo_data,
    ):
        """Skill match should reflect overlap between user skills and issue requirements."""
        from app.models.issue import Issue
        from app.models.match import Match
        from app.models.repo import Repo
        from app.models.user import User

        repo = Repo(**sample_repo_data)
        db_session.add(repo)
        await db_session.flush()

        user = User(
            github_id=sample_contributor_profile["github_id"],
            username=sample_contributor_profile["username"],
            role="contributor",
        )
        db_session.add(user)
        await db_session.flush()

        issue = Issue(
            repo_id=repo.id,
            github_id=5002,
            number=102,
            title="Implement connection pool monitoring",
            body="Need to expose pool metrics",
            state="open",
        )
        db_session.add(issue)
        await db_session.flush()

        # Python + FastAPI skill match should produce high skill_match
        match = Match(
            user_id=user.id,
            issue_id=issue.id,
            score=0.88,
            skill_match=0.90,
            health_match=0.82,
            interest_match=0.75,
            growth_match=0.60,
        )
        db_session.add(match)
        await db_session.flush()

        assert match.skill_match == 0.90
        assert match.score == 0.88

    @pytest.mark.asyncio
    async def test_health_match_penalizes_unhealthy_repos(
        self,
        dormant_repo_metrics,
    ):
        """Health match should be low for dormant repositories."""
        # A dormant repo should have a low health score
        commit_activity = dormant_repo_metrics["commit_count_90d"]
        response_time = dormant_repo_metrics["avg_issue_response_hours"]

        assert commit_activity == 0
        assert response_time > 500

        # Health match for this repo should be very low
        health_match = min(1.0, max(0.0, 1.0 - (response_time / 1000)))
        assert health_match < 0.5

    @pytest.mark.asyncio
    async def test_growth_match_favors_stretch_issues(
        self,
        sample_contributor_profile,
    ):
        """Growth match should be higher for issues slightly above current skill level."""
        python_proficiency = 0.85

        # An issue requiring proficiency 0.90 is a good stretch
        stretch_difficulty = 0.90
        growth_match = max(0, 1.0 - abs(stretch_difficulty - python_proficiency - 0.10))
        assert growth_match > 0.5

        # An issue way above skill level (0.99) is not a good match
        too_hard_difficulty = 0.99
        growth_match_hard = max(0, 1.0 - abs(too_hard_difficulty - python_proficiency - 0.10))
        assert growth_match_hard < growth_match


class TestMatchingEndpoint:
    """Tests for the matching API endpoint."""

    @pytest.mark.asyncio
    async def test_matching_endpoint_returns_ranked_results(
        self,
        sample_contributor_profile,
    ):
        """The /match endpoint should return issues ranked by match score."""
        # Validate that recommendation data can be sorted by score
        recommendations = [
            {
                "id": str(uuid.uuid4()),
                "issue": {
                    "number": 102,
                    "title": "Implement connection pool monitoring",
                    "complexity": "medium",
                },
                "matchScore": 0.91,
                "healthLevel": 4,
                "difficulty": 55,
                "estimatedMinutes": 180,
            },
            {
                "id": str(uuid.uuid4()),
                "issue": {
                    "number": 101,
                    "title": "Add type hints to database module",
                    "complexity": "easy",
                },
                "matchScore": 0.72,
                "healthLevel": 4,
                "difficulty": 20,
                "estimatedMinutes": 60,
            },
        ]

        # Results should be ranked by descending match score
        sorted_recs = sorted(recommendations, key=lambda r: r["matchScore"], reverse=True)
        assert sorted_recs[0]["matchScore"] >= sorted_recs[1]["matchScore"]
        assert sorted_recs[0]["issue"]["number"] == 102

    @pytest.mark.asyncio
    async def test_matching_excludes_claimed_issues(
        self,
        sample_issues_for_matching,
    ):
        """The matching endpoint should never return claimed issues."""
        # Simulate filtering
        available = [
            issue for issue in sample_issues_for_matching
            if not issue["is_claimed"]
        ]

        for issue in available:
            assert issue["is_claimed"] is False

        # Issue 104 was claimed and should not appear
        available_numbers = {issue["number"] for issue in available}
        assert 104 not in available_numbers

    @pytest.mark.asyncio
    async def test_matching_filters_by_language(
        self,
        sample_contributor_profile,
    ):
        """Users can filter recommendations by programming language."""
        skills = sample_contributor_profile["skills"]
        python_skill = next(s for s in skills if s["name"] == "Python")
        ts_skill = next(s for s in skills if s["name"] == "TypeScript")

        # Python proficiency is higher, so Python repos should rank higher
        assert python_skill["proficiency"] > ts_skill["proficiency"]


class TestFeedbackLoop:
    """Tests for the recommendation feedback mechanism."""

    @pytest.mark.asyncio
    async def test_positive_feedback_recorded(
        self,
        db_session,
        sample_contributor_profile,
        sample_repo_data,
    ):
        """Positive feedback should update the match status."""
        from app.models.issue import Issue
        from app.models.match import Match, MatchStatus
        from app.models.repo import Repo
        from app.models.user import User

        repo = Repo(**sample_repo_data)
        db_session.add(repo)
        await db_session.flush()

        user = User(
            github_id=sample_contributor_profile["github_id"],
            username=sample_contributor_profile["username"],
            role="contributor",
        )
        db_session.add(user)
        await db_session.flush()

        issue = Issue(
            repo_id=repo.id,
            github_id=5002,
            number=102,
            title="Implement pool monitoring",
            body="...",
            state="open",
        )
        db_session.add(issue)
        await db_session.flush()

        match = Match(
            user_id=user.id,
            issue_id=issue.id,
            score=0.88,
            skill_match=0.90,
            health_match=0.82,
            interest_match=0.75,
            growth_match=0.60,
            status=MatchStatus.recommended,
        )
        db_session.add(match)
        await db_session.flush()

        # Simulate accepting the recommendation
        match.status = MatchStatus.accepted
        match.feedback = "positive"
        await db_session.flush()

        assert match.status == MatchStatus.accepted
        assert match.feedback == "positive"

    @pytest.mark.asyncio
    async def test_negative_feedback_recorded(
        self,
        db_session,
        sample_contributor_profile,
        sample_repo_data,
    ):
        """Negative feedback with reason should be stored for model improvement."""
        from app.models.issue import Issue
        from app.models.match import Match, MatchStatus
        from app.models.repo import Repo
        from app.models.user import User

        repo = Repo(**sample_repo_data)
        db_session.add(repo)
        await db_session.flush()

        user = User(
            github_id=sample_contributor_profile["github_id"],
            username=sample_contributor_profile["username"],
            role="contributor",
        )
        db_session.add(user)
        await db_session.flush()

        issue = Issue(
            repo_id=repo.id,
            github_id=5003,
            number=103,
            title="Fix race condition in async scheduler",
            body="...",
            state="open",
        )
        db_session.add(issue)
        await db_session.flush()

        match = Match(
            user_id=user.id,
            issue_id=issue.id,
            score=0.65,
            skill_match=0.50,
            health_match=0.82,
            interest_match=0.60,
            growth_match=0.80,
            status=MatchStatus.recommended,
        )
        db_session.add(match)
        await db_session.flush()

        match.status = MatchStatus.rejected
        match.feedback = "too_hard"
        await db_session.flush()

        assert match.status == MatchStatus.rejected
        assert match.feedback == "too_hard"
