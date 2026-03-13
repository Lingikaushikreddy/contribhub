"""Shared pytest fixtures for the ContribHub ML pipeline test suite."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Sample issues
# ---------------------------------------------------------------------------


@pytest.fixture()
def bug_issue() -> dict:
    """A sample bug issue with reproduction steps."""
    return {
        "title": "App crashes on login with SSO enabled",
        "body": (
            "When clicking 'Sign in with Google' the app immediately crashes "
            "with a segfault.\n\nStack trace:\n```\nSIGSEGV at 0x00000000\n"
            "auth_service.rs:142 -- unwrap on None\n```\n\n"
            "This started after the v2.4.0 release."
        ),
        "labels": ["bug", "critical"],
        "author": "alice",
        "category": "bug",
        "is_first_time": False,
    }


@pytest.fixture()
def feature_issue() -> dict:
    """A sample feature request issue."""
    return {
        "title": "Add dark mode support",
        "body": (
            "It would be great to have a dark mode toggle in the settings. "
            "Many users work late and the bright theme is harsh.\n\n"
            "Suggested approach:\n- Use CSS custom properties\n"
            "- Store preference in localStorage\n"
            "- Respect prefers-color-scheme media query"
        ),
        "labels": ["enhancement", "frontend"],
        "author": "bob",
        "category": "feature",
        "is_first_time": False,
    }


@pytest.fixture()
def question_issue() -> dict:
    """A sample question issue."""
    return {
        "title": "How do I configure rate limiting?",
        "body": (
            "I'm trying to set up rate limiting for our API but can't find docs. "
            "Is there a built-in middleware or do I need a third-party library?"
        ),
        "labels": ["question"],
        "author": "charlie",
        "category": "question",
        "is_first_time": True,
    }


@pytest.fixture()
def docs_issue() -> dict:
    """A sample documentation issue."""
    return {
        "title": "Fix broken links in the contribution guide",
        "body": (
            "Several links in CONTRIBUTING.md are broken:\n"
            "- Line 34: link to code style guide returns 404\n"
            "- Line 58: link to issue templates points to old repo"
        ),
        "labels": ["docs"],
        "author": "diana",
        "category": "docs",
        "is_first_time": False,
    }


@pytest.fixture()
def chore_issue() -> dict:
    """A sample chore issue."""
    return {
        "title": "Upgrade ESLint to v9 flat config",
        "body": (
            "ESLint v9 deprecates .eslintrc in favour of flat config. "
            "We should migrate before the next major release."
        ),
        "labels": ["chore"],
        "author": "eve",
        "category": "chore",
        "is_first_time": False,
    }


# ---------------------------------------------------------------------------
# Sample repositories
# ---------------------------------------------------------------------------


@pytest.fixture()
def active_repo_data() -> dict:
    """Repository data for a healthy, active project."""
    return {
        "commits_last_90d": 250,
        "releases_last_year": 6,
        "last_commit_date": "2026-03-12T10:00:00Z",
        "contributors_count": 45,
        "new_contributors_last_90d": 8,
        "stars": 2500,
        "forks": 340,
        "watchers": 120,
        "has_ci": True,
        "test_coverage_pct": 82.0,
        "open_bugs_count": 12,
        "closed_bugs_last_90d": 35,
        "avg_pr_review_comments": 3.5,
        "has_readme": True,
        "has_contributing": True,
        "has_code_of_conduct": True,
        "has_changelog": True,
        "has_license": True,
        "has_issue_templates": True,
        "median_issue_close_hours": 36.0,
        "median_pr_merge_hours": 18.0,
        "pct_issues_responded_24h": 78.0,
        "commit_authors": [
            {"author": "lead-dev", "pct": 35.0},
            {"author": "core-dev1", "pct": 20.0},
            {"author": "core-dev2", "pct": 15.0},
            {"author": "contributor1", "pct": 10.0},
            {"author": "contributor2", "pct": 8.0},
            {"author": "contributor3", "pct": 6.0},
            {"author": "contributor4", "pct": 3.5},
            {"author": "contributor5", "pct": 2.5},
        ],
        "has_funding": True,
        "has_roadmap": True,
        "dependency_count": 40,
        "outdated_deps_count": 5,
        "has_security_policy": True,
        "open_vulnerability_count": 0,
        "dependabot_enabled": True,
        "signed_commits_pct": 65.0,
    }


@pytest.fixture()
def dormant_repo_data() -> dict:
    """Repository data for an inactive / dormant project."""
    return {
        "commits_last_90d": 0,
        "releases_last_year": 0,
        "last_commit_date": "2024-06-01T10:00:00Z",
        "contributors_count": 2,
        "new_contributors_last_90d": 0,
        "stars": 15,
        "forks": 1,
        "watchers": 2,
        "has_ci": False,
        "test_coverage_pct": 0.0,
        "open_bugs_count": 20,
        "closed_bugs_last_90d": 0,
        "avg_pr_review_comments": 0.0,
        "has_readme": True,
        "has_contributing": False,
        "has_code_of_conduct": False,
        "has_changelog": False,
        "has_license": True,
        "has_issue_templates": False,
        "median_issue_close_hours": float("inf"),
        "median_pr_merge_hours": float("inf"),
        "pct_issues_responded_24h": 0.0,
        "commit_authors": [
            {"author": "solo-dev", "pct": 95.0},
            {"author": "once-contributor", "pct": 5.0},
        ],
        "has_funding": False,
        "has_roadmap": False,
        "dependency_count": 30,
        "outdated_deps_count": 25,
        "has_security_policy": False,
        "open_vulnerability_count": 8,
        "dependabot_enabled": False,
        "signed_commits_pct": 0.0,
    }


# ---------------------------------------------------------------------------
# Sample contributor profiles
# ---------------------------------------------------------------------------


@pytest.fixture()
def experienced_contributor() -> dict:
    """A well-rounded experienced contributor profile."""
    return {
        "github_username": "senior-dev",
        "skills": [
            {"name": "React -- Component Development", "category": "frontend", "proficiency": 0.9},
            {"name": "API Design -- REST/GraphQL", "category": "backend", "proficiency": 0.8},
            {"name": "Docker -- Containerisation", "category": "infrastructure", "proficiency": 0.7},
            {"name": "Testing -- Unit Tests", "category": "testing", "proficiency": 0.85},
            {"name": "Code Review -- Peer Review", "category": "engineering", "proficiency": 0.75},
        ],
        "languages": {
            "TypeScript": 0.95,
            "Python": 0.8,
            "Rust": 0.4,
            "Go": 0.3,
        },
        "experience_level": "advanced",
        "domains": ["frontend", "backend", "testing", "infrastructure", "engineering"],
    }


@pytest.fixture()
def beginner_contributor() -> dict:
    """A beginner contributor profile with limited skills."""
    return {
        "github_username": "new-dev",
        "skills": [
            {"name": "Markdown -- Documentation", "category": "documentation", "proficiency": 0.6},
            {"name": "CSS -- Styling", "category": "frontend", "proficiency": 0.3},
        ],
        "languages": {
            "JavaScript": 0.5,
            "HTML": 0.4,
        },
        "experience_level": "beginner",
        "domains": ["documentation", "frontend"],
    }


# ---------------------------------------------------------------------------
# Mock API responses
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_openai_classification_response():
    """Factory fixture: returns a function that creates mock OpenAI responses."""

    def _make_response(category: str, priority: str, confidence: float, reasoning: str):
        import json

        class _Message:
            def __init__(self, content):
                self.content = content

        class _Choice:
            def __init__(self, message):
                self.message = message

        class _Response:
            def __init__(self, choices):
                self.choices = choices

        content = json.dumps({
            "category": category,
            "priority": priority,
            "confidence": confidence,
            "reasoning": reasoning,
        })
        return _Response([_Choice(_Message(content))])

    return _make_response


@pytest.fixture()
def mock_anthropic_classification_response():
    """Factory fixture: returns a function that creates mock Anthropic responses."""

    def _make_response(category: str, priority: str, confidence: float, reasoning: str):
        import json

        class _TextBlock:
            def __init__(self, text):
                self.text = text

        class _Response:
            def __init__(self, content):
                self.content = content

        content = json.dumps({
            "category": category,
            "priority": priority,
            "confidence": confidence,
            "reasoning": reasoning,
        })
        return _Response([_TextBlock(content)])

    return _make_response


@pytest.fixture()
def mock_openai_embedding_response():
    """Factory fixture: returns a function that creates mock embedding responses."""

    def _make_response(embeddings: list[list[float]]):
        class _EmbeddingData:
            def __init__(self, embedding, index):
                self.embedding = embedding
                self.index = index

        class _Response:
            def __init__(self, data):
                self.data = data

        data = [_EmbeddingData(emb, i) for i, emb in enumerate(embeddings)]
        return _Response(data)

    return _make_response
