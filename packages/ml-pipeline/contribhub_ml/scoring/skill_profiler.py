"""
Contributor skill profiling from GitHub activity data.

Analyses languages used, file paths touched, PR complexity, and review
activity to build a structured skill profile with a 3-level taxonomy.
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """A single skill entry."""

    name: str
    category: str
    proficiency: float  # 0.0 – 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "proficiency": round(self.proficiency, 3),
        }


@dataclass
class SkillProfile:
    """Complete skill profile for a contributor."""

    github_username: str
    skills: list[Skill] = field(default_factory=list)
    languages: dict[str, float] = field(default_factory=dict)
    experience_level: str = "beginner"
    domains: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "github_username": self.github_username,
            "skills": [s.to_dict() for s in self.skills],
            "languages": {k: round(v, 3) for k, v in self.languages.items()},
            "experience_level": self.experience_level,
            "domains": self.domains,
        }


# ---------------------------------------------------------------------------
# 3-level taxonomy:  Domain -> Technology -> Specific
# ---------------------------------------------------------------------------

_PATH_SKILL_MAP: dict[str, tuple[str, str, str]] = {
    # (pattern substring, domain, technology, specific skill)
    # Web frontend
    "src/components": ("frontend", "React", "Component Development"),
    "pages/": ("frontend", "React", "Page Routing"),
    "app/": ("frontend", "Next.js", "App Router"),
    "styles/": ("frontend", "CSS", "Styling"),
    ".css": ("frontend", "CSS", "Styling"),
    ".scss": ("frontend", "Sass", "Styling"),
    "tailwind": ("frontend", "Tailwind CSS", "Utility-First CSS"),
    # Backend
    "api/": ("backend", "API Design", "REST/GraphQL"),
    "routes/": ("backend", "Routing", "HTTP Handlers"),
    "middleware": ("backend", "Middleware", "Request Processing"),
    "controllers/": ("backend", "MVC", "Controller Logic"),
    "services/": ("backend", "Services", "Business Logic"),
    "prisma/": ("backend", "Prisma", "ORM / Database"),
    "models/": ("backend", "Data Modeling", "Schema Design"),
    "migrations/": ("backend", "Database", "Migrations"),
    # Infrastructure
    "docker": ("infrastructure", "Docker", "Containerisation"),
    "terraform": ("infrastructure", "Terraform", "IaC"),
    "k8s": ("infrastructure", "Kubernetes", "Orchestration"),
    ".github/workflows": ("infrastructure", "GitHub Actions", "CI/CD"),
    "ci/": ("infrastructure", "CI/CD", "Pipeline Config"),
    # ML / Data
    "model": ("ml", "Machine Learning", "Model Development"),
    "training": ("ml", "Machine Learning", "Model Training"),
    "notebook": ("ml", "Jupyter", "Experimentation"),
    "pipeline": ("ml", "Data Pipeline", "ETL"),
    # Testing
    "test": ("testing", "Testing", "Test Authoring"),
    "spec": ("testing", "Testing", "Spec Writing"),
    "__tests__": ("testing", "Testing", "Unit Tests"),
    "e2e": ("testing", "Testing", "End-to-End Tests"),
    # Documentation
    "docs/": ("documentation", "Technical Writing", "Documentation"),
    "readme": ("documentation", "Technical Writing", "README"),
    ".md": ("documentation", "Markdown", "Documentation"),
}

# Language file extensions → language name
_EXT_LANGUAGE_MAP: dict[str, str] = {
    ".py": "Python",
    ".pyi": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".rs": "Rust",
    ".go": "Go",
    ".java": "Java",
    ".kt": "Kotlin",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C",
    ".swift": "Swift",
    ".scala": "Scala",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".hs": "Haskell",
    ".lua": "Lua",
    ".r": "R",
    ".sql": "SQL",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".json": "JSON",
    ".toml": "TOML",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
}


def _extension_of(path: str) -> str:
    """Return the lowercase file extension."""
    dot = path.rfind(".")
    if dot == -1:
        return ""
    return path[dot:].lower()


class SkillProfiler:
    """Build a contributor skill profile from GitHub activity data.

    Parameters
    ----------
    min_proficiency : float
        Minimum proficiency to include a skill (filters noise).
    """

    def __init__(self, min_proficiency: float = 0.05) -> None:
        self.min_proficiency = min_proficiency

    def build_profile(
        self,
        github_username: str,
        contributions_data: dict[str, Any],
    ) -> SkillProfile:
        """Analyse contribution data and return a skill profile.

        Parameters
        ----------
        github_username : str
            GitHub handle of the contributor.
        contributions_data : dict
            Expected keys:

            - ``files_touched`` : list[dict] with ``path`` (str) and ``loc`` (int)
            - ``prs`` : list[dict] with ``files_changed`` (int), ``additions`` (int),
              ``deletions`` (int), ``reviews_given`` (int), ``reviews_received`` (int)
            - ``languages`` : dict[str, int]  — language name to LOC
            - ``commits`` : int
            - ``repos_contributed`` : int
            - ``account_age_days`` : int

        Returns
        -------
        SkillProfile
        """
        languages = self._extract_languages(contributions_data)
        skills = self._extract_skills(contributions_data)
        domains = self._extract_domains(skills)
        experience_level = self._determine_experience_level(contributions_data)

        # Filter low-signal skills
        skills = [s for s in skills if s.proficiency >= self.min_proficiency]

        # Sort by proficiency descending
        skills.sort(key=lambda s: s.proficiency, reverse=True)

        return SkillProfile(
            github_username=github_username,
            skills=skills,
            languages=languages,
            experience_level=experience_level,
            domains=domains,
        )

    # ------------------------------------------------------------------
    # Language analysis
    # ------------------------------------------------------------------

    def _extract_languages(self, data: dict[str, Any]) -> dict[str, float]:
        """Build a language → proficiency dict weighted by LOC.

        Proficiency is normalised so the top language gets 1.0.
        """
        lang_loc: dict[str, int] = {}

        # Explicit language LOC from contributions_data
        for lang, loc in data.get("languages", {}).items():
            lang_loc[lang] = lang_loc.get(lang, 0) + loc

        # Infer from file paths
        for file_info in data.get("files_touched", []):
            path = file_info.get("path", "")
            loc = file_info.get("loc", 1)
            ext = _extension_of(path)
            lang = _EXT_LANGUAGE_MAP.get(ext)
            if lang:
                lang_loc[lang] = lang_loc.get(lang, 0) + loc

        if not lang_loc:
            return {}

        max_loc = max(lang_loc.values())
        if max_loc == 0:
            return {}

        return {
            lang: min(loc / max_loc, 1.0)
            for lang, loc in lang_loc.items()
        }

    # ------------------------------------------------------------------
    # Skill extraction from file paths
    # ------------------------------------------------------------------

    def _extract_skills(self, data: dict[str, Any]) -> list[Skill]:
        """Extract skills from file paths and PR activity."""
        skill_scores: dict[tuple[str, str, str], float] = defaultdict(float)

        # File-path based signals
        for file_info in data.get("files_touched", []):
            path = file_info.get("path", "").lower()
            loc = file_info.get("loc", 1)
            for pattern, (domain, tech, specific) in _PATH_SKILL_MAP.items():
                if pattern in path:
                    skill_scores[(domain, tech, specific)] += loc

        # PR complexity signal — reward larger PRs but with diminishing returns
        for pr in data.get("prs", []):
            size = pr.get("additions", 0) + pr.get("deletions", 0)
            if size > 500:
                skill_scores[("engineering", "Large Changes", "Refactoring")] += 1.0
            reviews_given = pr.get("reviews_given", 0)
            if reviews_given > 0:
                skill_scores[("engineering", "Code Review", "Peer Review")] += reviews_given

        if not skill_scores:
            return []

        max_score = max(skill_scores.values())
        if max_score == 0:
            return []

        skills: list[Skill] = []
        for (domain, tech, specific), raw in skill_scores.items():
            proficiency = min(raw / max_score, 1.0)
            skills.append(Skill(
                name=f"{tech} — {specific}",
                category=domain,
                proficiency=proficiency,
            ))

        return skills

    # ------------------------------------------------------------------
    # Domain extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_domains(skills: list[Skill]) -> list[str]:
        """Unique domains sorted by aggregate proficiency."""
        domain_total: dict[str, float] = defaultdict(float)
        for s in skills:
            domain_total[s.category] += s.proficiency
        sorted_domains = sorted(domain_total, key=domain_total.get, reverse=True)  # type: ignore[arg-type]
        return sorted_domains

    # ------------------------------------------------------------------
    # Experience level
    # ------------------------------------------------------------------

    @staticmethod
    def _determine_experience_level(data: dict[str, Any]) -> str:
        """Heuristic experience level from aggregate activity."""
        commits = data.get("commits", 0)
        repos = data.get("repos_contributed", 0)
        prs = len(data.get("prs", []))
        age_days = data.get("account_age_days", 0)

        score = 0.0
        # Commit volume (log-scaled)
        if commits > 0:
            import math
            score += min(math.log10(commits + 1) / 4.0, 1.0) * 30

        # Repo breadth
        score += min(repos / 15.0, 1.0) * 25

        # PR throughput
        score += min(prs / 50.0, 1.0) * 25

        # Account tenure
        score += min(age_days / (365 * 5), 1.0) * 20

        if score >= 75:
            return "expert"
        if score >= 50:
            return "advanced"
        if score >= 25:
            return "intermediate"
        return "beginner"
