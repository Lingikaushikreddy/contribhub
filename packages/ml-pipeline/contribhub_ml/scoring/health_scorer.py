"""
Repository health scoring.

Computes a composite 0-100 score across seven weighted dimensions:
activity, community, quality, documentation, responsiveness,
sustainability, and security.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class HealthScore:
    """Composite repository health score."""

    total_score: float
    breakdown: dict[str, float] = field(default_factory=dict)
    is_active: bool = True
    bus_factor: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_score": round(self.total_score, 2),
            "breakdown": {k: round(v, 2) for k, v in self.breakdown.items()},
            "is_active": self.is_active,
            "bus_factor": self.bus_factor,
        }


# Dimension weights (must sum to 1.0)
_WEIGHTS: dict[str, float] = {
    "activity": 0.18,
    "community": 0.18,
    "quality": 0.15,
    "docs": 0.15,
    "responsiveness": 0.12,
    "sustainability": 0.12,
    "security": 0.10,
}


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


class HealthScorer:
    """Score the health of a GitHub repository.

    Parameters
    ----------
    dormant_threshold : float
        Total score below which the repo is considered dormant.
    dormant_days : int
        Number of days without commits after which the repo is dormant.
    """

    def __init__(
        self,
        dormant_threshold: float = 30.0,
        dormant_days: int = 90,
    ) -> None:
        self.dormant_threshold = dormant_threshold
        self.dormant_days = dormant_days

    def score(self, repo_data: dict[str, Any]) -> HealthScore:
        """Score a repository's health.

        Parameters
        ----------
        repo_data : dict
            Expected keys (all optional, defaults produce low scores):

            **Activity**
            - ``commits_last_90d`` : int
            - ``releases_last_year`` : int
            - ``last_commit_date`` : str (ISO 8601)

            **Community**
            - ``contributors_count`` : int
            - ``new_contributors_last_90d`` : int
            - ``stars`` : int
            - ``forks`` : int
            - ``watchers`` : int

            **Quality**
            - ``has_ci`` : bool
            - ``test_coverage_pct`` : float (0-100)
            - ``open_bugs_count`` : int
            - ``closed_bugs_last_90d`` : int
            - ``avg_pr_review_comments`` : float

            **Docs**
            - ``has_readme`` : bool
            - ``has_contributing`` : bool
            - ``has_code_of_conduct`` : bool
            - ``has_changelog`` : bool
            - ``has_license`` : bool
            - ``has_issue_templates`` : bool

            **Responsiveness**
            - ``median_issue_close_hours`` : float
            - ``median_pr_merge_hours`` : float
            - ``pct_issues_responded_24h`` : float (0-100)

            **Sustainability**
            - ``commit_authors`` : list[dict] with ``author`` (str), ``pct`` (float)
            - ``has_funding`` : bool
            - ``has_roadmap`` : bool
            - ``dependency_count`` : int
            - ``outdated_deps_count`` : int

            **Security**
            - ``has_security_policy`` : bool
            - ``open_vulnerability_count`` : int
            - ``dependabot_enabled`` : bool
            - ``signed_commits_pct`` : float (0-100)

        Returns
        -------
        HealthScore
        """
        breakdown: dict[str, float] = {
            "activity": self._score_activity(repo_data),
            "community": self._score_community(repo_data),
            "quality": self._score_quality(repo_data),
            "docs": self._score_docs(repo_data),
            "responsiveness": self._score_responsiveness(repo_data),
            "sustainability": self._score_sustainability(repo_data),
            "security": self._score_security(repo_data),
        }

        total = sum(
            breakdown[dim] * _WEIGHTS[dim] for dim in _WEIGHTS
        )
        total = _clamp(total)

        bus_factor = self._calculate_bus_factor(repo_data)
        is_active = self._check_active(total, repo_data)

        return HealthScore(
            total_score=total,
            breakdown=breakdown,
            is_active=is_active,
            bus_factor=bus_factor,
        )

    # ------------------------------------------------------------------
    # Sub-scorers (each returns 0-100)
    # ------------------------------------------------------------------

    @staticmethod
    def _score_activity(data: dict[str, Any]) -> float:
        commits = data.get("commits_last_90d", 0)
        releases = data.get("releases_last_year", 0)

        # Log-scaled commit score (100+ commits/90d is great)
        commit_score = min(math.log10(commits + 1) / math.log10(101) * 100, 100) if commits > 0 else 0

        # Release cadence: 4+ releases/year is solid
        release_score = min(releases / 4.0 * 100, 100)

        # Recency bonus
        recency_score = 0.0
        last_commit = data.get("last_commit_date")
        if last_commit:
            try:
                last_dt = datetime.fromisoformat(last_commit.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                days_since = (now - last_dt).days
                recency_score = max(0, 100 - days_since * 1.5)
            except (ValueError, TypeError):
                pass

        return _clamp(0.45 * commit_score + 0.25 * release_score + 0.30 * recency_score)

    @staticmethod
    def _score_community(data: dict[str, Any]) -> float:
        contributors = data.get("contributors_count", 0)
        new_contribs = data.get("new_contributors_last_90d", 0)
        stars = data.get("stars", 0)
        forks = data.get("forks", 0)

        contrib_score = min(math.log10(contributors + 1) / math.log10(201) * 100, 100) if contributors > 0 else 0
        growth_score = min(new_contribs / 5.0 * 100, 100)
        popularity = min(math.log10(stars + 1) / math.log10(10001) * 100, 100) if stars > 0 else 0
        fork_score = min(math.log10(forks + 1) / math.log10(1001) * 100, 100) if forks > 0 else 0

        return _clamp(
            0.35 * contrib_score + 0.25 * growth_score
            + 0.25 * popularity + 0.15 * fork_score
        )

    @staticmethod
    def _score_quality(data: dict[str, Any]) -> float:
        has_ci = data.get("has_ci", False)
        coverage = data.get("test_coverage_pct", 0.0)
        open_bugs = data.get("open_bugs_count", 0)
        closed_bugs = data.get("closed_bugs_last_90d", 0)
        review_comments = data.get("avg_pr_review_comments", 0.0)

        ci_score = 100.0 if has_ci else 0.0
        coverage_score = min(coverage, 100.0)

        # Bug close rate
        total_bugs = open_bugs + closed_bugs
        bug_close_rate = (closed_bugs / total_bugs * 100) if total_bugs > 0 else 50.0

        # Review engagement
        review_score = min(review_comments / 3.0 * 100, 100)

        return _clamp(
            0.25 * ci_score + 0.30 * coverage_score
            + 0.25 * bug_close_rate + 0.20 * review_score
        )

    @staticmethod
    def _score_docs(data: dict[str, Any]) -> float:
        checks = [
            ("has_readme", 30),
            ("has_contributing", 20),
            ("has_code_of_conduct", 10),
            ("has_changelog", 15),
            ("has_license", 15),
            ("has_issue_templates", 10),
        ]
        total = sum(weight for key, weight in checks if data.get(key, False))
        return _clamp(float(total))

    @staticmethod
    def _score_responsiveness(data: dict[str, Any]) -> float:
        issue_hours = data.get("median_issue_close_hours", float("inf"))
        pr_hours = data.get("median_pr_merge_hours", float("inf"))
        pct_24h = data.get("pct_issues_responded_24h", 0.0)

        # Issue close time: <48h = 100, >720h = 0
        if issue_hours == float("inf"):
            issue_score = 0.0
        else:
            issue_score = max(0.0, 100 - (issue_hours - 48) / (720 - 48) * 100)
            issue_score = _clamp(issue_score)

        # PR merge time: <24h = 100, >336h (2wk) = 0
        if pr_hours == float("inf"):
            pr_score = 0.0
        else:
            pr_score = max(0.0, 100 - (pr_hours - 24) / (336 - 24) * 100)
            pr_score = _clamp(pr_score)

        response_score = min(pct_24h, 100.0)

        return _clamp(0.35 * issue_score + 0.35 * pr_score + 0.30 * response_score)

    @staticmethod
    def _score_sustainability(data: dict[str, Any]) -> float:
        has_funding = data.get("has_funding", False)
        has_roadmap = data.get("has_roadmap", False)
        dep_count = data.get("dependency_count", 0)
        outdated = data.get("outdated_deps_count", 0)

        # Bus factor is scored separately; here we look at other sustainability signals
        funding_score = 30.0 if has_funding else 0.0
        roadmap_score = 20.0 if has_roadmap else 0.0

        # Dependency health
        if dep_count > 0:
            dep_health = max(0.0, 100 - (outdated / dep_count) * 100)
        else:
            dep_health = 100.0

        # Commit author diversity (use commit_authors list)
        authors = data.get("commit_authors", [])
        if len(authors) >= 5:
            diversity_score = 50.0
        elif len(authors) >= 3:
            diversity_score = 30.0
        elif len(authors) >= 2:
            diversity_score = 15.0
        else:
            diversity_score = 0.0

        raw = funding_score + roadmap_score + (dep_health * 0.3) + (diversity_score * 0.4)
        return _clamp(raw)

    @staticmethod
    def _score_security(data: dict[str, Any]) -> float:
        has_policy = data.get("has_security_policy", False)
        vulns = data.get("open_vulnerability_count", 0)
        dependabot = data.get("dependabot_enabled", False)
        signed_pct = data.get("signed_commits_pct", 0.0)

        policy_score = 30.0 if has_policy else 0.0
        dependabot_score = 25.0 if dependabot else 0.0

        # Fewer vulns = better
        vuln_score = max(0.0, 100 - vulns * 20)

        signed_score = min(signed_pct, 100.0)

        raw = policy_score + dependabot_score + vuln_score * 0.25 + signed_score * 0.20
        return _clamp(raw)

    # ------------------------------------------------------------------
    # Bus factor
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_bus_factor(data: dict[str, Any]) -> int:
        """Count developers who authored >5% of recent commits."""
        authors = data.get("commit_authors", [])
        if not authors:
            return 1
        significant = [a for a in authors if a.get("pct", 0) > 5.0]
        return max(len(significant), 1)

    # ------------------------------------------------------------------
    # Dormancy detection
    # ------------------------------------------------------------------

    def _check_active(self, total_score: float, data: dict[str, Any]) -> bool:
        """Return False if the repo is dormant."""
        if total_score < self.dormant_threshold:
            return False

        last_commit = data.get("last_commit_date")
        if last_commit:
            try:
                last_dt = datetime.fromisoformat(last_commit.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                days_since = (now - last_dt).days
                if days_since > self.dormant_days:
                    return False
            except (ValueError, TypeError):
                pass

        return True
