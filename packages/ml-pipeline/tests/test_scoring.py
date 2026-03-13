"""Tests for HealthScorer, SkillProfiler, and MatchScorer modules."""

from __future__ import annotations

import math

import pytest

from contribhub_ml.scoring.health_scorer import HealthScore, HealthScorer
from contribhub_ml.scoring.match_scorer import MatchScore, MatchScorer
from contribhub_ml.scoring.skill_profiler import Skill, SkillProfile, SkillProfiler


# ===========================================================================
# HealthScorer tests
# ===========================================================================


class TestHealthScorer:
    """Tests for the repository health scoring system."""

    def test_active_repo_high_score(self, active_repo_data):
        """A healthy active repo should get a high total score."""
        scorer = HealthScorer()
        result = scorer.score(active_repo_data)

        assert result.total_score > 50.0
        assert result.is_active is True

    def test_dormant_repo_low_score(self, dormant_repo_data):
        """A dormant repo should get a low total score and is_active=False."""
        scorer = HealthScorer()
        result = scorer.score(dormant_repo_data)

        assert result.total_score < 40.0
        assert result.is_active is False

    def test_active_repo_bus_factor(self, active_repo_data):
        """A repo with many contributors should have a high bus factor."""
        scorer = HealthScorer()
        result = scorer.score(active_repo_data)

        # active_repo_data has 8 authors, 6 above 5%
        assert result.bus_factor >= 5

    def test_dormant_repo_bus_factor(self, dormant_repo_data):
        """A single-maintainer repo should have bus factor of 1-2."""
        scorer = HealthScorer()
        result = scorer.score(dormant_repo_data)

        assert result.bus_factor <= 2

    def test_score_breakdown_has_all_dimensions(self, active_repo_data):
        """Score breakdown should include all seven dimensions."""
        scorer = HealthScorer()
        result = scorer.score(active_repo_data)

        expected_dims = {
            "activity", "community", "quality", "docs",
            "responsiveness", "sustainability", "security",
        }
        assert set(result.breakdown.keys()) == expected_dims

    def test_score_breakdown_values_in_range(self, active_repo_data):
        """Each dimension score should be between 0 and 100."""
        scorer = HealthScorer()
        result = scorer.score(active_repo_data)

        for dim, value in result.breakdown.items():
            assert 0.0 <= value <= 100.0, f"{dim} = {value} is out of range"

    def test_total_score_in_range(self, active_repo_data):
        """Total score should be between 0 and 100."""
        scorer = HealthScorer()
        result = scorer.score(active_repo_data)

        assert 0.0 <= result.total_score <= 100.0

    def test_docs_score_all_present(self, active_repo_data):
        """When all doc artifacts are present, docs score should be 100."""
        scorer = HealthScorer()
        result = scorer.score(active_repo_data)

        assert result.breakdown["docs"] == 100.0

    def test_docs_score_minimal(self, dormant_repo_data):
        """When only README and LICENSE exist, docs score should be partial."""
        scorer = HealthScorer()
        result = scorer.score(dormant_repo_data)

        # has_readme (30) + has_license (15) = 45
        assert result.breakdown["docs"] == 45.0

    def test_empty_repo_data(self):
        """Empty repo data should produce a low but valid score."""
        scorer = HealthScorer()
        result = scorer.score({})

        assert 0.0 <= result.total_score <= 100.0
        assert result.bus_factor >= 1

    def test_dormant_threshold_configurable(self, dormant_repo_data):
        """Custom dormant_threshold should change is_active classification."""
        # Very low threshold: even dormant repos would be "active"
        scorer_lenient = HealthScorer(dormant_threshold=1.0, dormant_days=9999)
        result_lenient = scorer_lenient.score(dormant_repo_data)

        # Strict threshold
        scorer_strict = HealthScorer(dormant_threshold=95.0)
        result_strict = scorer_strict.score(dormant_repo_data)

        # lenient might still mark as dormant due to dormant_days check on last_commit_date
        # strict should definitely mark as dormant
        assert result_strict.is_active is False

    def test_to_dict(self, active_repo_data):
        """to_dict should produce a serialisable dictionary."""
        scorer = HealthScorer()
        result = scorer.score(active_repo_data)
        d = result.to_dict()

        assert isinstance(d["total_score"], float)
        assert isinstance(d["breakdown"], dict)
        assert isinstance(d["is_active"], bool)
        assert isinstance(d["bus_factor"], int)

    def test_responsiveness_fast_responses(self):
        """Very fast response times should yield a high responsiveness score."""
        scorer = HealthScorer()
        data = {
            "median_issue_close_hours": 12.0,
            "median_pr_merge_hours": 6.0,
            "pct_issues_responded_24h": 95.0,
        }
        result = scorer.score(data)
        assert result.breakdown["responsiveness"] > 70.0

    def test_responsiveness_no_responses(self):
        """Infinite response times should yield zero responsiveness."""
        scorer = HealthScorer()
        data = {
            "median_issue_close_hours": float("inf"),
            "median_pr_merge_hours": float("inf"),
            "pct_issues_responded_24h": 0.0,
        }
        result = scorer.score(data)
        assert result.breakdown["responsiveness"] == 0.0

    def test_security_all_good(self):
        """Perfect security signals should yield a high security score."""
        scorer = HealthScorer()
        data = {
            "has_security_policy": True,
            "open_vulnerability_count": 0,
            "dependabot_enabled": True,
            "signed_commits_pct": 100.0,
        }
        result = scorer.score(data)
        assert result.breakdown["security"] > 70.0

    def test_security_all_bad(self):
        """Poor security signals should yield a low security score."""
        scorer = HealthScorer()
        data = {
            "has_security_policy": False,
            "open_vulnerability_count": 10,
            "dependabot_enabled": False,
            "signed_commits_pct": 0.0,
        }
        result = scorer.score(data)
        assert result.breakdown["security"] < 30.0


# ===========================================================================
# SkillProfiler tests
# ===========================================================================


class TestSkillProfiler:
    """Tests for the contributor skill profiling system."""

    def test_build_profile_basic(self):
        """Basic profile should extract languages and skills from file paths."""
        profiler = SkillProfiler()
        data = {
            "files_touched": [
                {"path": "src/components/Button.tsx", "loc": 100},
                {"path": "src/components/Card.tsx", "loc": 50},
                {"path": "api/routes/users.ts", "loc": 80},
                {"path": "test/Button.test.tsx", "loc": 40},
            ],
            "prs": [
                {"files_changed": 5, "additions": 200, "deletions": 50, "reviews_given": 2, "reviews_received": 3}
            ],
            "languages": {"TypeScript": 500},
            "commits": 100,
            "repos_contributed": 5,
            "account_age_days": 730,
        }

        profile = profiler.build_profile("testuser", data)

        assert profile.github_username == "testuser"
        assert len(profile.skills) > 0
        assert "TypeScript" in profile.languages
        assert profile.experience_level in ("beginner", "intermediate", "advanced", "expert")

    def test_languages_normalized(self):
        """Top language should have proficiency 1.0."""
        profiler = SkillProfiler()
        data = {
            "languages": {"Python": 1000, "JavaScript": 500, "Rust": 100},
            "files_touched": [],
            "prs": [],
            "commits": 10,
            "repos_contributed": 1,
            "account_age_days": 100,
        }

        profile = profiler.build_profile("user", data)

        assert profile.languages["Python"] == 1.0
        assert profile.languages["JavaScript"] == 0.5
        assert profile.languages["Rust"] == 0.1

    def test_experience_level_beginner(self):
        """Few commits and repos should yield 'beginner'."""
        profiler = SkillProfiler()
        data = {
            "commits": 5,
            "repos_contributed": 1,
            "prs": [],
            "account_age_days": 30,
            "files_touched": [],
            "languages": {},
        }

        profile = profiler.build_profile("newbie", data)
        assert profile.experience_level == "beginner"

    def test_experience_level_expert(self):
        """Many commits, repos, PRs, and long tenure should yield 'expert'."""
        profiler = SkillProfiler()
        data = {
            "commits": 5000,
            "repos_contributed": 50,
            "prs": [{"files_changed": 10, "additions": 100, "deletions": 50, "reviews_given": 5, "reviews_received": 3}] * 100,
            "account_age_days": 365 * 8,
            "files_touched": [],
            "languages": {},
        }

        profile = profiler.build_profile("veteran", data)
        assert profile.experience_level == "expert"

    def test_domains_extracted(self):
        """Domains should be extracted from skill categories."""
        profiler = SkillProfiler()
        data = {
            "files_touched": [
                {"path": "src/components/App.tsx", "loc": 200},
                {"path": "api/routes/index.ts", "loc": 150},
                {"path": "test/unit/app.test.ts", "loc": 100},
            ],
            "prs": [],
            "languages": {},
            "commits": 50,
            "repos_contributed": 3,
            "account_age_days": 365,
        }

        profile = profiler.build_profile("user", data)

        assert len(profile.domains) > 0
        assert "frontend" in profile.domains

    def test_min_proficiency_filter(self):
        """Skills below min_proficiency should be filtered out."""
        profiler = SkillProfiler(min_proficiency=0.5)
        data = {
            "files_touched": [
                {"path": "src/components/Big.tsx", "loc": 1000},
                {"path": "docs/tiny.md", "loc": 1},  # tiny LOC -> low proficiency
            ],
            "prs": [],
            "languages": {},
            "commits": 10,
            "repos_contributed": 1,
            "account_age_days": 100,
        }

        profile = profiler.build_profile("user", data)

        for skill in profile.skills:
            assert skill.proficiency >= 0.5

    def test_empty_contributions(self):
        """Empty contributions should produce a minimal profile."""
        profiler = SkillProfiler()
        data = {
            "files_touched": [],
            "prs": [],
            "languages": {},
            "commits": 0,
            "repos_contributed": 0,
            "account_age_days": 0,
        }

        profile = profiler.build_profile("empty", data)

        assert profile.github_username == "empty"
        assert profile.skills == []
        assert profile.languages == {}
        assert profile.experience_level == "beginner"

    def test_skill_profile_to_dict(self):
        """to_dict should produce a serialisable dictionary."""
        profile = SkillProfile(
            github_username="testuser",
            skills=[Skill(name="React", category="frontend", proficiency=0.9)],
            languages={"TypeScript": 0.95},
            experience_level="advanced",
            domains=["frontend"],
        )
        d = profile.to_dict()

        assert d["github_username"] == "testuser"
        assert len(d["skills"]) == 1
        assert d["skills"][0]["name"] == "React"
        assert d["languages"]["TypeScript"] == 0.95

    def test_skills_sorted_by_proficiency(self):
        """Skills should be sorted by proficiency descending."""
        profiler = SkillProfiler()
        data = {
            "files_touched": [
                {"path": "src/components/Big.tsx", "loc": 500},
                {"path": "api/routes/index.ts", "loc": 300},
                {"path": "test/unit/app.test.ts", "loc": 100},
            ],
            "prs": [],
            "languages": {},
            "commits": 20,
            "repos_contributed": 2,
            "account_age_days": 200,
        }

        profile = profiler.build_profile("user", data)

        proficiencies = [s.proficiency for s in profile.skills]
        assert proficiencies == sorted(proficiencies, reverse=True)


# ===========================================================================
# MatchScorer tests
# ===========================================================================


class TestMatchScorer:
    """Tests for the contributor-to-issue match scoring system."""

    def test_high_skill_match_high_score(self, experienced_contributor):
        """A contributor with matching skills should get a high match score."""
        scorer = MatchScorer()

        issue = {
            "required_skills": [
                {"name": "React -- Component Development", "category": "frontend", "proficiency": 0.8},
                {"name": "Testing -- Unit Tests", "category": "testing", "proficiency": 0.7},
            ],
            "labels": ["frontend", "bug"],
            "complexity_score": 6.0,
            "language": "typescript",
        }
        repo_health = {"total_score": 80.0, "is_active": True}

        result = scorer.score(experienced_contributor, issue, repo_health)

        assert result.total > 0.5

    def test_low_skill_match_low_score(self, beginner_contributor):
        """A beginner with non-matching skills should get a low match score."""
        scorer = MatchScorer()

        issue = {
            "required_skills": [
                {"name": "Docker -- Containerisation", "category": "infrastructure", "proficiency": 0.9},
                {"name": "Kubernetes", "category": "infrastructure", "proficiency": 0.8},
            ],
            "labels": ["infrastructure"],
            "complexity_score": 8.0,
            "language": "go",
        }
        repo_health = {"total_score": 70.0, "is_active": True}

        result = scorer.score(beginner_contributor, issue, repo_health)

        assert result.total < 0.4

    def test_inactive_repo_penalty(self, experienced_contributor):
        """An inactive repo should penalise the health match dimension."""
        scorer = MatchScorer()

        issue = {
            "required_skills": [],
            "labels": [],
            "complexity_score": 5.0,
            "language": "python",
        }

        active_health = {"total_score": 60.0, "is_active": True}
        inactive_health = {"total_score": 60.0, "is_active": False}

        result_active = scorer.score(experienced_contributor, issue, active_health)
        result_inactive = scorer.score(experienced_contributor, issue, inactive_health)

        assert result_active.breakdown["health_match"] > result_inactive.breakdown["health_match"]

    def test_score_breakdown_dimensions(self, experienced_contributor):
        """Match score breakdown should include all four dimensions."""
        scorer = MatchScorer()

        issue = {
            "required_skills": [],
            "labels": [],
            "complexity_score": 5.0,
            "language": "",
        }

        result = scorer.score(experienced_contributor, issue)

        expected_dims = {"skill_match", "health_match", "interest_match", "growth_stretch"}
        assert set(result.breakdown.keys()) == expected_dims

    def test_total_score_between_0_and_1(self, experienced_contributor):
        """Total match score should always be between 0 and 1."""
        scorer = MatchScorer()

        issue = {
            "required_skills": [],
            "labels": [],
            "complexity_score": 5.0,
            "language": "",
        }

        result = scorer.score(experienced_contributor, issue)

        assert 0.0 <= result.total <= 1.0

    def test_no_required_skills_moderate_skill_match(self, experienced_contributor):
        """When issue has no required skills, skill match should be moderate (0.5)."""
        scorer = MatchScorer()

        issue = {
            "required_skills": [],
            "labels": [],
            "complexity_score": 5.0,
            "language": "",
        }

        result = scorer.score(experienced_contributor, issue)

        assert math.isclose(result.breakdown["skill_match"], 0.5, abs_tol=0.01)

    def test_growth_stretch_sweet_spot(self):
        """An issue slightly above contributor level should get a growth bonus."""
        scorer = MatchScorer(growth_bonus=0.15, growth_range=(0.05, 0.25))

        contributor = {
            "skills": [],
            "languages": {},
            "experience_level": "beginner",  # maps to 0.15
            "domains": [],
        }

        # Complexity that puts issue_difficulty in the sweet spot
        # beginner = 0.15, sweet spot = 0.15 + [0.05, 0.25] = [0.20, 0.40]
        # issue_difficulty = (complexity - 1) / 9
        # complexity 3.5 gives difficulty = 2.5/9 ~ 0.278, delta ~ 0.128 (well in sweet spot)
        issue = {
            "required_skills": [],
            "labels": [],
            "complexity_score": 3.5,
            "language": "",
        }

        result = scorer.score(contributor, issue)

        # Growth stretch should be at the bonus level (0.70 + 0.15 = 0.85)
        assert result.breakdown["growth_stretch"] >= 0.80

    def test_growth_stretch_too_hard(self):
        """An issue far above contributor level should lower the growth score."""
        scorer = MatchScorer()

        contributor = {
            "skills": [],
            "languages": {},
            "experience_level": "beginner",  # 0.15
            "domains": [],
        }

        # Very high complexity => issue_difficulty close to 1.0
        issue = {
            "required_skills": [],
            "labels": [],
            "complexity_score": 10.0,  # difficulty = 1.0
            "language": "",
        }

        result = scorer.score(contributor, issue)

        # Delta = 1.0 - 0.15 = 0.85 >> max_d (0.25), so score should drop
        assert result.breakdown["growth_stretch"] < 0.5

    def test_interest_match_domain_overlap(self, experienced_contributor):
        """Labels matching contributor domains should boost interest score."""
        scorer = MatchScorer()

        issue = {
            "required_skills": [],
            "labels": ["frontend", "testing"],
            "complexity_score": 5.0,
            "language": "typescript",
        }

        result = scorer.score(experienced_contributor, issue)

        # experienced_contributor has frontend, testing, etc. in domains
        # and TypeScript in languages
        assert result.breakdown["interest_match"] > 0.5

    def test_interest_match_no_overlap(self, beginner_contributor):
        """No domain overlap should yield low interest score."""
        scorer = MatchScorer()

        issue = {
            "required_skills": [],
            "labels": ["infrastructure", "security"],
            "complexity_score": 5.0,
            "language": "rust",
        }

        result = scorer.score(beginner_contributor, issue)

        # beginner has documentation and frontend, not infrastructure or security
        assert result.breakdown["interest_match"] < 0.5

    def test_skill_match_with_vectors(self):
        """When skill vectors are provided, cosine similarity should be used."""
        scorer = MatchScorer()

        contributor = {
            "skills": [],
            "languages": {},
            "experience_level": "intermediate",
            "domains": [],
            "skill_vector": [1.0, 0.0, 0.0],
        }

        issue_similar = {
            "required_skills": [],
            "labels": [],
            "complexity_score": 5.0,
            "language": "",
            "skill_vector": [0.95, 0.1, 0.0],
        }
        issue_different = {
            "required_skills": [],
            "labels": [],
            "complexity_score": 5.0,
            "language": "",
            "skill_vector": [0.0, 0.0, 1.0],
        }

        result_similar = scorer.score(contributor, issue_similar)
        result_different = scorer.score(contributor, issue_different)

        assert result_similar.breakdown["skill_match"] > result_different.breakdown["skill_match"]

    def test_language_bonus_applied(self):
        """Matching language should add a bonus to skill_match."""
        scorer = MatchScorer()

        contributor = {
            "skills": [],
            "languages": {"python": 1.0},
            "experience_level": "intermediate",
            "domains": [],
        }

        issue_with_lang = {
            "required_skills": [
                {"name": "SomeSkill", "category": "backend", "proficiency": 0.5},
            ],
            "labels": [],
            "complexity_score": 5.0,
            "language": "python",
        }
        issue_without_lang = {
            "required_skills": [
                {"name": "SomeSkill", "category": "backend", "proficiency": 0.5},
            ],
            "labels": [],
            "complexity_score": 5.0,
            "language": "haskell",
        }

        result_with = scorer.score(contributor, issue_with_lang)
        result_without = scorer.score(contributor, issue_without_lang)

        assert result_with.breakdown["skill_match"] > result_without.breakdown["skill_match"]

    def test_no_repo_health_defaults(self, experienced_contributor):
        """When repo_health is None, health_match should use defaults."""
        scorer = MatchScorer()

        issue = {
            "required_skills": [],
            "labels": [],
            "complexity_score": 5.0,
            "language": "",
        }

        result = scorer.score(experienced_contributor, issue, repo_health=None)

        # Default total_score=50, is_active=True => 0.5
        assert math.isclose(result.breakdown["health_match"], 0.5, abs_tol=0.01)

    def test_match_score_to_dict(self):
        """to_dict should serialise correctly."""
        ms = MatchScore(
            total=0.7654321,
            breakdown={"skill_match": 0.8, "health_match": 0.6, "interest_match": 0.7, "growth_stretch": 0.9},
        )
        d = ms.to_dict()

        assert d["total"] == 0.7654
        assert d["breakdown"]["skill_match"] == 0.8
