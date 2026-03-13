"""Matching service — contributor-to-issue recommendation engine."""

import uuid
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.issue import Issue
from app.models.match import Match, MatchStatus
from app.models.repo import Repo
from app.models.skill import Skill
from app.models.user import User, UserSkill


class MatchingService:
    """Generates and manages contributor-issue match recommendations."""

    # ── Weights for composite score ──────────────────────────────────────
    WEIGHT_SKILL = 0.40
    WEIGHT_HEALTH = 0.15
    WEIGHT_INTEREST = 0.25
    WEIGHT_GROWTH = 0.20

    # ── Skill profile ───────────────────────────────────────────────────

    async def get_skill_profile(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> dict[str, float]:
        """Build a {skill_name: proficiency} map for a user.

        Args:
            db: Active database session.
            user_id: The user whose profile to fetch.

        Returns:
            Dict mapping skill name to proficiency score.
        """
        result = await db.execute(
            select(Skill.name, UserSkill.proficiency)
            .join(UserSkill, UserSkill.skill_id == Skill.id)
            .where(UserSkill.user_id == user_id)
        )
        return {row.name: row.proficiency for row in result.all()}

    # ── Scoring functions ────────────────────────────────────────────────

    def _skill_score(
        self, user_skills: dict[str, float], issue: Issue
    ) -> float:
        """Compute skill-match score between user skills and issue requirements.

        Uses issue labels and language as proxies for required skills.
        """
        if not user_skills:
            return 0.0

        issue_signals: set[str] = set()
        if issue.labels:
            for label in issue.labels:
                name = label if isinstance(label, str) else label.get("name", "")
                issue_signals.add(name.lower())

        # Add the repository language when available (loaded via relationship or passed)
        repo_lang = getattr(issue, "_repo_language", None)
        if repo_lang:
            issue_signals.add(repo_lang.lower())

        if not issue_signals:
            return 0.5  # neutral when no signal

        matched = sum(
            prof
            for skill_name, prof in user_skills.items()
            if skill_name.lower() in issue_signals
        )
        return min(1.0, matched / max(len(issue_signals), 1))

    def _health_score(self, repo_health: float) -> float:
        """Return normalized repo health — higher is better for contributors."""
        return min(1.0, max(0.0, repo_health))

    def _interest_score(self, user_skills: dict[str, float], issue: Issue) -> float:
        """Estimate how interesting this issue is to the contributor.

        Higher complexity and feature-type issues are considered more interesting
        for contributors who have declared high proficiency.
        """
        complexity = (issue.complexity_score or 5) / 10.0
        avg_prof = sum(user_skills.values()) / max(len(user_skills), 1)
        # Contributors with higher proficiency prefer higher complexity
        alignment = 1.0 - abs(avg_prof - complexity)
        # Boost features and bugs
        category_bonus = 0.1 if issue.category and issue.category.value in ("feature", "bug") else 0.0
        return min(1.0, alignment + category_bonus)

    def _growth_score(self, user_skills: dict[str, float], issue: Issue) -> float:
        """Score the growth opportunity — issues slightly above the contributor's level.

        Returns higher scores when the issue complexity is just above the
        contributor's average skill level (zone of proximal development).
        """
        avg_prof = sum(user_skills.values()) / max(len(user_skills), 1)
        complexity = (issue.complexity_score or 5) / 10.0
        delta = complexity - avg_prof
        # Sweet spot: issue is 0.1–0.3 above skill level
        if 0.05 <= delta <= 0.35:
            return 0.9
        elif 0.0 <= delta <= 0.5:
            return 0.6
        elif delta < 0:
            return 0.3  # too easy
        else:
            return 0.2  # too hard

    def _composite_score(
        self,
        skill: float,
        health: float,
        interest: float,
        growth: float,
    ) -> float:
        return (
            self.WEIGHT_SKILL * skill
            + self.WEIGHT_HEALTH * health
            + self.WEIGHT_INTEREST * interest
            + self.WEIGHT_GROWTH * growth
        )

    # ── Candidate generation ─────────────────────────────────────────────

    async def generate_recommendations(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        limit: int = 20,
    ) -> list[Match]:
        """Generate ranked issue recommendations for a contributor.

        Steps:
            1. Build the user's skill profile.
            2. Query open, unclaimed issues that the user hasn't already been matched to.
            3. Score each candidate issue.
            4. Persist top-N matches.

        Args:
            db: Active database session.
            user_id: The contributor to generate recommendations for.
            limit: Maximum number of matches to return.

        Returns:
            Sorted list of Match objects (highest score first).
        """
        user_skills = await self.get_skill_profile(db, user_id)

        # Get existing matched issue ids to exclude
        existing_result = await db.execute(
            select(Match.issue_id).where(
                Match.user_id == user_id,
                Match.status.in_([MatchStatus.accepted, MatchStatus.completed]),
            )
        )
        excluded_issue_ids = {row[0] for row in existing_result.all()}

        # Candidate issues: open, not claimed, not already matched
        issue_query = (
            select(Issue, Repo.health_score, Repo.language)
            .join(Repo, Issue.repo_id == Repo.id)
            .where(
                Issue.state == "open",
                Issue.is_claimed == False,  # noqa: E712
            )
            .order_by(Issue.created_at.desc())
            .limit(500)
        )
        result = await db.execute(issue_query)
        candidates = result.all()

        scored: list[tuple[float, float, float, float, float, Issue]] = []
        for issue, repo_health, repo_language in candidates:
            if issue.id in excluded_issue_ids:
                continue

            # Attach language for scoring
            issue._repo_language = repo_language

            s = self._skill_score(user_skills, issue)
            h = self._health_score(repo_health)
            i = self._interest_score(user_skills, issue)
            g = self._growth_score(user_skills, issue)
            c = self._composite_score(s, h, i, g)
            scored.append((c, s, h, i, g, issue))

        # Sort descending by composite score, take top N
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:limit]

        matches: list[Match] = []
        for composite, skill, health, interest, growth, issue in top:
            match = Match(
                user_id=user_id,
                issue_id=issue.id,
                score=round(composite, 4),
                skill_match=round(skill, 4),
                health_match=round(health, 4),
                interest_match=round(interest, 4),
                growth_match=round(growth, 4),
                status=MatchStatus.recommended,
            )
            db.add(match)
            matches.append(match)

        await db.flush()
        return matches

    # ── Statistics ───────────────────────────────────────────────────────

    async def get_match_stats(
        self, db: AsyncSession, user_id: uuid.UUID | None = None
    ) -> dict[str, Any]:
        """Compute aggregate match statistics.

        Args:
            db: Active database session.
            user_id: Optional filter for a specific user.

        Returns:
            Dict with totals, rates, and averages.
        """
        base = select(Match)
        if user_id:
            base = base.where(Match.user_id == user_id)

        total_result = await db.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = total_result.scalar() or 0

        status_counts: dict[str, int] = {}
        for status_val in MatchStatus:
            q = base.where(Match.status == status_val)
            cnt_result = await db.execute(
                select(func.count()).select_from(q.subquery())
            )
            status_counts[status_val.value] = cnt_result.scalar() or 0

        avg_result = await db.execute(
            select(func.avg(Match.score)).select_from(base.subquery())
        )
        avg_score = avg_result.scalar() or 0.0

        accepted = status_counts.get("accepted", 0)
        completed = status_counts.get("completed", 0)
        rejected = status_counts.get("rejected", 0)

        acceptance_rate = accepted / total if total > 0 else 0.0
        completion_rate = completed / accepted if accepted > 0 else 0.0

        return {
            "total_matches": total,
            "accepted": accepted,
            "completed": completed,
            "rejected": rejected,
            "average_score": round(float(avg_score), 4),
            "acceptance_rate": round(acceptance_rate, 4),
            "completion_rate": round(completion_rate, 4),
        }


# Module-level singleton
matching_service = MatchingService()
