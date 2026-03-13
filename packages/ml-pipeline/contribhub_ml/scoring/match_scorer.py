"""
Contributor-to-issue match scoring.

Computes a composite 0-1 score from four dimensions: skill match,
repository health, interest alignment, and growth stretch.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class MatchScore:
    """Result of matching a contributor to an issue."""

    total: float
    breakdown: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": round(self.total, 4),
            "breakdown": {k: round(v, 4) for k, v in self.breakdown.items()},
        }


# Dimension weights
_WEIGHTS: dict[str, float] = {
    "skill_match": 0.40,
    "health_match": 0.25,
    "interest_match": 0.20,
    "growth_stretch": 0.15,
}


def _cosine_sim(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors (returns 0 on empty/zero)."""
    va = np.asarray(a, dtype=np.float64)
    vb = np.asarray(b, dtype=np.float64)
    norm_a = float(np.linalg.norm(va))
    norm_b = float(np.linalg.norm(vb))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))


class MatchScorer:
    """Score how well a contributor matches an issue.

    Parameters
    ----------
    growth_bonus : float
        Extra score added for issues slightly above the contributor's level.
    growth_range : tuple[float, float]
        (min_delta, max_delta) defining the "sweet spot" range above the
        contributor's current level.  Delta is measured in normalised
        complexity units (0-1 scale).
    """

    def __init__(
        self,
        growth_bonus: float = 0.15,
        growth_range: tuple[float, float] = (0.05, 0.25),
    ) -> None:
        self.growth_bonus = growth_bonus
        self.growth_range = growth_range

    def score(
        self,
        contributor_profile: dict[str, Any],
        issue: dict[str, Any],
        repo_health: dict[str, Any] | None = None,
    ) -> MatchScore:
        """Compute the match score.

        Parameters
        ----------
        contributor_profile : dict
            Output of ``SkillProfile.to_dict()`` or a compatible dict.
            Expected keys: ``skills`` (list of {name, category, proficiency}),
            ``languages`` (dict[str, float]), ``experience_level`` (str),
            ``domains`` (list[str]), and optionally ``skill_vector`` (list[float]).

        issue : dict
            Expected keys: ``required_skills`` (list of {name, category, proficiency}),
            ``labels`` (list[str]), ``complexity_score`` (float 1-10),
            ``language`` (str), and optionally ``skill_vector`` (list[float]).

        repo_health : dict | None
            Output of ``HealthScore.to_dict()`` or compatible dict.
            Expected keys: ``total_score`` (0-100), ``is_active`` (bool).

        Returns
        -------
        MatchScore
        """
        if repo_health is None:
            repo_health = {}

        skill = self._skill_match(contributor_profile, issue)
        health = self._health_match(repo_health)
        interest = self._interest_match(contributor_profile, issue)
        growth = self._growth_stretch(contributor_profile, issue)

        total = (
            _WEIGHTS["skill_match"] * skill
            + _WEIGHTS["health_match"] * health
            + _WEIGHTS["interest_match"] * interest
            + _WEIGHTS["growth_stretch"] * growth
        )
        total = max(0.0, min(1.0, total))

        return MatchScore(
            total=total,
            breakdown={
                "skill_match": skill,
                "health_match": health,
                "interest_match": interest,
                "growth_stretch": growth,
            },
        )

    # ------------------------------------------------------------------
    # Dimension scorers
    # ------------------------------------------------------------------

    def _skill_match(
        self, profile: dict[str, Any], issue: dict[str, Any]
    ) -> float:
        """Compare contributor skills to issue requirements.

        Uses cosine similarity on skill vectors if available, otherwise
        falls back to set overlap and proficiency comparison.
        """
        # Fast path: precomputed vectors
        profile_vec = profile.get("skill_vector")
        issue_vec = issue.get("skill_vector")
        if profile_vec and issue_vec:
            return max(0.0, min(1.0, _cosine_sim(profile_vec, issue_vec)))

        # Slow path: set-based comparison
        contributor_skills = {
            s["name"].lower(): s.get("proficiency", 0.5)
            for s in profile.get("skills", [])
        }
        required_skills = {
            s["name"].lower(): s.get("proficiency", 0.5)
            for s in issue.get("required_skills", [])
        }

        if not required_skills:
            # No requirements — give a moderate default score
            return 0.5

        # Weighted overlap
        total_weight = 0.0
        matched_weight = 0.0
        for skill_name, required_prof in required_skills.items():
            total_weight += required_prof
            if skill_name in contributor_skills:
                contrib_prof = contributor_skills[skill_name]
                # Scale by how well proficiency matches
                ratio = min(contrib_prof / max(required_prof, 0.01), 1.0)
                matched_weight += required_prof * ratio

        if total_weight == 0:
            return 0.5

        # Language bonus
        lang_bonus = 0.0
        issue_lang = issue.get("language", "").lower()
        if issue_lang:
            contributor_langs = {
                k.lower(): v for k, v in profile.get("languages", {}).items()
            }
            if issue_lang in contributor_langs:
                lang_bonus = 0.1 * contributor_langs[issue_lang]

        raw = matched_weight / total_weight + lang_bonus
        return max(0.0, min(1.0, raw))

    @staticmethod
    def _health_match(repo_health: dict[str, Any]) -> float:
        """Higher-health repos get a better match score.

        Maps the 0-100 health score to 0-1 and penalises inactive repos.
        """
        total = repo_health.get("total_score", 50.0)
        is_active = repo_health.get("is_active", True)

        base = total / 100.0
        if not is_active:
            base *= 0.5  # heavy penalty for dormant repos

        return max(0.0, min(1.0, base))

    @staticmethod
    def _interest_match(
        profile: dict[str, Any], issue: dict[str, Any]
    ) -> float:
        """Score based on overlap between contributor domains and issue labels."""
        contributor_domains = {d.lower() for d in profile.get("domains", [])}
        contributor_langs = {k.lower() for k in profile.get("languages", {})}

        issue_labels = {lbl.lower() for lbl in issue.get("labels", [])}
        issue_lang = issue.get("language", "").lower()
        issue_categories = set()

        # Map labels to domain-level categories
        label_domain_map: dict[str, str] = {
            "bug": "engineering",
            "feature": "engineering",
            "enhancement": "engineering",
            "documentation": "documentation",
            "docs": "documentation",
            "frontend": "frontend",
            "backend": "backend",
            "api": "backend",
            "infra": "infrastructure",
            "infrastructure": "infrastructure",
            "ci": "infrastructure",
            "ci/cd": "infrastructure",
            "testing": "testing",
            "test": "testing",
            "security": "security",
            "ml": "ml",
            "machine-learning": "ml",
            "data": "ml",
        }
        for lbl in issue_labels:
            mapped = label_domain_map.get(lbl)
            if mapped:
                issue_categories.add(mapped)

        if not issue_categories and not issue_lang:
            return 0.5  # neutral

        matches = 0
        checks = 0

        # Domain overlap
        if issue_categories:
            overlap = contributor_domains & issue_categories
            checks += 1
            if overlap:
                matches += len(overlap) / len(issue_categories)

        # Language match
        if issue_lang:
            checks += 1
            if issue_lang in contributor_langs:
                matches += 1.0

        if checks == 0:
            return 0.5

        return max(0.0, min(1.0, matches / checks))

    def _growth_stretch(
        self, profile: dict[str, Any], issue: dict[str, Any]
    ) -> float:
        """Slightly higher score for issues just above contributor level.

        This promotes learning by matching contributors to challenges
        within a productive stretch zone.
        """
        # Map experience levels to a numeric scale
        level_map: dict[str, float] = {
            "beginner": 0.15,
            "intermediate": 0.40,
            "advanced": 0.70,
            "expert": 0.95,
        }

        contributor_level = level_map.get(
            profile.get("experience_level", "beginner"), 0.15
        )

        # Issue complexity normalised to 0-1
        complexity = issue.get("complexity_score", 5.0)
        issue_difficulty = (complexity - 1.0) / 9.0  # map 1-10 to 0-1

        delta = issue_difficulty - contributor_level
        min_d, max_d = self.growth_range

        if min_d <= delta <= max_d:
            # In the sweet spot — maximum growth bonus
            return min(1.0, 0.70 + self.growth_bonus)
        elif delta < min_d:
            # Issue is at or below contributor level
            # Still fine, just less growth potential
            return 0.50 + max(0.0, delta / min_d) * 0.20
        else:
            # Issue is too far above contributor level
            # Score drops off as delta exceeds max_d
            overshoot = delta - max_d
            return max(0.0, 0.70 - overshoot * 2.0)
