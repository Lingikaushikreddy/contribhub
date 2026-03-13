"""
Shared fixtures for ContribHub integration tests.

Provides mock GitHub API responses, test database setup/teardown, mock Redis,
and sample issue payloads for all test scenarios.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event as sa_event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings, get_settings
from app.models.base import Base


# ---------------------------------------------------------------------------
# Settings Override
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///file::memory:?cache=shared&uri=true"


def get_test_settings() -> Settings:
    """Return settings configured for the test environment."""
    return Settings(
        DATABASE_URL=TEST_DATABASE_URL,
        REDIS_URL="redis://localhost:6379/15",
        GITHUB_APP_ID="test-app-id",
        GITHUB_PRIVATE_KEY="test-private-key",
        GITHUB_WEBHOOK_SECRET="test-webhook-secret",
        JWT_SECRET_KEY="test-jwt-secret",
        ENVIRONMENT="test",
        DEBUG=True,
    )


# ---------------------------------------------------------------------------
# Database Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create an async SQLite engine for tests, with tables created and dropped each test."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncSession:
    """Provide a scoped async session that rolls back after each test."""
    session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session
        await session.rollback()


# ---------------------------------------------------------------------------
# Mock Redis
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_redis():
    """Provide a mock Redis client with common operations."""
    redis_mock = MagicMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=1)
    redis_mock.incr = AsyncMock(return_value=1)
    redis_mock.expire = AsyncMock(return_value=True)
    redis_mock.setex = AsyncMock(return_value=True)
    redis_mock.exists = AsyncMock(return_value=0)
    redis_mock.lpush = AsyncMock(return_value=1)
    redis_mock.lrange = AsyncMock(return_value=[])
    redis_mock.pipeline = MagicMock(return_value=redis_mock)
    redis_mock.execute = AsyncMock(return_value=[])
    redis_mock.__aenter__ = AsyncMock(return_value=redis_mock)
    redis_mock.__aexit__ = AsyncMock(return_value=None)
    return redis_mock


# ---------------------------------------------------------------------------
# Mock GitHub API
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_github_api():
    """Provide a mock GitHub API client with standard responses."""
    mock = MagicMock()

    mock.rest = MagicMock()

    mock.rest.issues.get.return_value = MagicMock(data=SAMPLE_GITHUB_ISSUE)
    mock.rest.issues.createLabel.return_value = MagicMock(status=201)
    mock.rest.issues.addLabels.return_value = MagicMock(status=200)
    mock.rest.issues.createComment.return_value = MagicMock(
        status=201,
        data={"id": 99001, "body": "comment body"},
    )
    mock.rest.issues.listComments.return_value = MagicMock(data=[])
    mock.rest.issues.listLabelsOnIssue.return_value = MagicMock(data=[])

    mock.rest.repos.getContent.return_value = MagicMock(
        data={
            "type": "file",
            "content": "",
            "encoding": "base64",
        }
    )

    return mock


# ---------------------------------------------------------------------------
# HTTP Test Client
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture()
async def api_client(db_session, mock_redis):
    """Provide an HTTPX AsyncClient wired to the FastAPI app with test overrides."""
    from app.core.database import get_db

    # Lazy import so the app module isn't loaded at collection time
    try:
        from app.main import app
    except ImportError:
        # If main.py doesn't exist yet, create a minimal stub
        from fastapi import FastAPI
        app = FastAPI()

    app.dependency_overrides[get_settings] = get_test_settings
    app.dependency_overrides[get_db] = lambda: db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Sample Issue Payloads
# ---------------------------------------------------------------------------

SAMPLE_REPO_OWNER = "test-org"
SAMPLE_REPO_NAME = "test-repo"
SAMPLE_REPO_FULL_NAME = f"{SAMPLE_REPO_OWNER}/{SAMPLE_REPO_NAME}"

SAMPLE_GITHUB_ISSUE: dict[str, Any] = {
    "id": 1001,
    "number": 42,
    "title": "App crashes on startup when config file is missing",
    "body": (
        "## Bug Report\n\n"
        "### Steps to Reproduce\n"
        "1. Delete the config.yml file\n"
        "2. Run `app start`\n"
        "3. Observe crash with traceback\n\n"
        "### Expected Behavior\n"
        "The app should start with default configuration.\n\n"
        "### Actual Behavior\n"
        "Unhandled FileNotFoundError — full traceback below.\n\n"
        "### Environment\n"
        "- OS: Ubuntu 22.04\n"
        "- App version: 2.4.1\n"
        "- Python: 3.11.6\n\n"
        "```\n"
        'Traceback (most recent call last):\n'
        '  File "app/main.py", line 23, in main\n'
        "    config = load_config('config.yml')\n"
        "FileNotFoundError: [Errno 2] No such file or directory: 'config.yml'\n"
        "```"
    ),
    "state": "open",
    "user": {"login": "test-reporter", "avatar_url": "https://example.com/avatar.png"},
    "labels": [],
    "created_at": "2026-03-01T10:00:00Z",
    "updated_at": "2026-03-01T10:00:00Z",
    "html_url": f"https://github.com/{SAMPLE_REPO_FULL_NAME}/issues/42",
}


@pytest.fixture()
def bug_issue_payload() -> dict[str, Any]:
    """A well-formed bug report with repro steps and traceback."""
    return {
        "owner": SAMPLE_REPO_OWNER,
        "repo": SAMPLE_REPO_NAME,
        "issue_number": 42,
        "title": "App crashes on startup when config file is missing",
        "body": SAMPLE_GITHUB_ISSUE["body"],
        "author": "test-reporter",
        "labels": [],
        "created_at": "2026-03-01T10:00:00Z",
        "updated_at": "2026-03-01T10:00:00Z",
        "html_url": f"https://github.com/{SAMPLE_REPO_FULL_NAME}/issues/42",
    }


@pytest.fixture()
def feature_issue_payload() -> dict[str, Any]:
    """A feature request with use case and proposed solution."""
    return {
        "owner": SAMPLE_REPO_OWNER,
        "repo": SAMPLE_REPO_NAME,
        "issue_number": 43,
        "title": "Support TOML configuration files in addition to YAML",
        "body": (
            "## Feature Request\n\n"
            "### Problem\n"
            "Many Python projects prefer TOML for configuration (PEP 518). "
            "Currently only YAML is supported.\n\n"
            "### Proposed Solution\n"
            "Add a TOML parser alongside the existing YAML parser. "
            "Auto-detect based on file extension.\n\n"
            "### Alternatives Considered\n"
            "Using a YAML-to-TOML converter, but that adds friction.\n\n"
            "### Additional Context\n"
            "This would also allow embedding config in pyproject.toml."
        ),
        "author": "feature-requester",
        "labels": [],
        "created_at": "2026-03-02T14:30:00Z",
        "updated_at": "2026-03-02T14:30:00Z",
        "html_url": f"https://github.com/{SAMPLE_REPO_FULL_NAME}/issues/43",
    }


@pytest.fixture()
def question_issue_payload() -> dict[str, Any]:
    """A question/support request."""
    return {
        "owner": SAMPLE_REPO_OWNER,
        "repo": SAMPLE_REPO_NAME,
        "issue_number": 44,
        "title": "How do I configure Redis connection pooling?",
        "body": (
            "I'm trying to set up connection pooling for Redis but the docs "
            "don't seem to cover this. Is there a recommended approach?\n\n"
            "I've tried setting `REDIS_MAX_CONNECTIONS=50` but connections "
            "still seem to pile up."
        ),
        "author": "curious-user",
        "labels": [],
        "created_at": "2026-03-03T09:15:00Z",
        "updated_at": "2026-03-03T09:15:00Z",
        "html_url": f"https://github.com/{SAMPLE_REPO_FULL_NAME}/issues/44",
    }


@pytest.fixture()
def duplicate_issue_payload() -> dict[str, Any]:
    """An issue that is essentially a duplicate of the bug_issue_payload."""
    return {
        "owner": SAMPLE_REPO_OWNER,
        "repo": SAMPLE_REPO_NAME,
        "issue_number": 45,
        "title": "FileNotFoundError when config.yml doesn't exist",
        "body": (
            "When I try to run the app without a config file, it crashes "
            "with a FileNotFoundError. The app should handle missing config "
            "gracefully and use defaults instead."
        ),
        "author": "another-reporter",
        "labels": [],
        "created_at": "2026-03-03T16:00:00Z",
        "updated_at": "2026-03-03T16:00:00Z",
        "html_url": f"https://github.com/{SAMPLE_REPO_FULL_NAME}/issues/45",
    }


@pytest.fixture()
def low_quality_issue_payload() -> dict[str, Any]:
    """An issue with very little detail — should trigger quality suggestions."""
    return {
        "owner": SAMPLE_REPO_OWNER,
        "repo": SAMPLE_REPO_NAME,
        "issue_number": 46,
        "title": "it doesn't work",
        "body": "broken please fix",
        "author": "vague-reporter",
        "labels": [],
        "created_at": "2026-03-04T11:00:00Z",
        "updated_at": "2026-03-04T11:00:00Z",
        "html_url": f"https://github.com/{SAMPLE_REPO_FULL_NAME}/issues/46",
    }


# ---------------------------------------------------------------------------
# Sample Triage API Responses
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_triage_response() -> dict[str, Any]:
    """Mock API response for a successful triage call."""
    return {
        "category": "bug",
        "priority": "P1",
        "complexity": "medium",
        "confidence": 0.92,
        "labels": [
            {"name": "contribhub/category: bug", "color": "d73a4a", "description": "Bug report", "confidence": 0.92},
            {"name": "contribhub/priority: P1", "color": "d93f0b", "description": "Priority: P1", "confidence": 0.88},
            {"name": "contribhub/complexity: medium", "color": "fbca04", "description": "Medium complexity", "confidence": 0.85},
        ],
        "qualityScore": 78,
        "qualitySuggestions": [],
        "responseDraftId": str(uuid.uuid4()),
        "processingTimeMs": 340,
    }


@pytest.fixture()
def mock_duplicate_response() -> dict[str, Any]:
    """Mock API response for a duplicate detection call with matches."""
    return {
        "hasDuplicates": True,
        "duplicates": [
            {
                "issueNumber": 42,
                "issueTitle": "App crashes on startup when config file is missing",
                "similarity": 0.93,
                "htmlUrl": f"https://github.com/{SAMPLE_REPO_FULL_NAME}/issues/42",
                "state": "open",
            },
        ],
        "processingTimeMs": 210,
    }


@pytest.fixture()
def mock_no_duplicate_response() -> dict[str, Any]:
    """Mock API response for a duplicate detection call with no matches."""
    return {
        "hasDuplicates": False,
        "duplicates": [],
        "processingTimeMs": 180,
    }


@pytest.fixture()
def mock_low_quality_triage_response() -> dict[str, Any]:
    """Mock API response for a low-quality issue."""
    return {
        "category": "bug",
        "priority": "P3",
        "complexity": "easy",
        "confidence": 0.55,
        "labels": [
            {"name": "contribhub/category: bug", "color": "d73a4a", "description": "Bug report", "confidence": 0.55},
        ],
        "qualityScore": 15,
        "qualitySuggestions": [
            "Add steps to reproduce the issue",
            "Include the expected vs actual behavior",
            "Provide environment details (OS, version, etc.)",
            "Add any error messages or logs",
        ],
        "responseDraftId": None,
        "processingTimeMs": 120,
    }


# ---------------------------------------------------------------------------
# Sample Domain Objects
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_repo_data() -> dict[str, Any]:
    """Data for creating a test Repo record."""
    return {
        "github_id": 12345,
        "owner": SAMPLE_REPO_OWNER,
        "name": SAMPLE_REPO_NAME,
        "full_name": SAMPLE_REPO_FULL_NAME,
        "description": "A test repository for integration testing",
        "stars": 150,
        "language": "Python",
        "health_score": 82.5,
    }


@pytest.fixture()
def sample_contributor_profile() -> dict[str, Any]:
    """A contributor profile for matching tests."""
    return {
        "github_id": 20001,
        "username": "skilled-dev",
        "email": "dev@example.com",
        "avatar_url": "https://avatars.githubusercontent.com/u/20001",
        "role": "contributor",
        "skills": [
            {"name": "Python", "proficiency": 0.85, "source": "inferred"},
            {"name": "FastAPI", "proficiency": 0.75, "source": "inferred"},
            {"name": "SQLAlchemy", "proficiency": 0.70, "source": "declared"},
            {"name": "TypeScript", "proficiency": 0.60, "source": "inferred"},
            {"name": "React", "proficiency": 0.50, "source": "declared"},
        ],
    }


@pytest.fixture()
def sample_issues_for_matching() -> list[dict[str, Any]]:
    """A set of issues with varying difficulty for matching tests."""
    now = datetime.now(timezone.utc)
    return [
        {
            "github_id": 5001,
            "number": 101,
            "title": "Add type hints to database module",
            "body": "The database module is missing type hints. Add them for better IDE support.",
            "state": "open",
            "category": "chore",
            "priority": "P3",
            "complexity_score": 20,
            "quality_score": 70,
            "is_claimed": False,
            "labels": ["good-first-issue", "typing"],
        },
        {
            "github_id": 5002,
            "number": 102,
            "title": "Implement connection pool monitoring",
            "body": "We need to expose connection pool metrics via a /health endpoint.",
            "state": "open",
            "category": "feature",
            "priority": "P2",
            "complexity_score": 55,
            "quality_score": 85,
            "is_claimed": False,
            "labels": ["feature", "monitoring"],
        },
        {
            "github_id": 5003,
            "number": 103,
            "title": "Fix race condition in async task scheduler",
            "body": "Under high load the task scheduler produces duplicate jobs. Needs mutex.",
            "state": "open",
            "category": "bug",
            "priority": "P1",
            "complexity_score": 80,
            "quality_score": 90,
            "is_claimed": False,
            "labels": ["bug", "concurrency"],
        },
        {
            "github_id": 5004,
            "number": 104,
            "title": "Update contributing guidelines",
            "body": "The contributing doc is outdated.",
            "state": "open",
            "category": "docs",
            "priority": "P3",
            "complexity_score": 10,
            "quality_score": 60,
            "is_claimed": True,
            "labels": ["docs", "good-first-issue"],
        },
        {
            "github_id": 5005,
            "number": 105,
            "title": "Migrate to SQLAlchemy 2.0 style queries",
            "body": "Replace legacy query() calls with the new select() API.",
            "state": "open",
            "category": "chore",
            "priority": "P2",
            "complexity_score": 45,
            "quality_score": 80,
            "is_claimed": False,
            "labels": ["refactor", "sqlalchemy"],
        },
    ]


# ---------------------------------------------------------------------------
# Health Scoring Test Data
# ---------------------------------------------------------------------------

@pytest.fixture()
def active_repo_metrics() -> dict[str, Any]:
    """Metrics for a healthy, active repository."""
    now = datetime.now(timezone.utc)
    return {
        "github_id": 30001,
        "owner": "healthy-org",
        "name": "active-project",
        "full_name": "healthy-org/active-project",
        "stars": 1200,
        "language": "Python",
        "last_commit_at": (now - timedelta(days=2)).isoformat(),
        "commit_count_90d": 145,
        "contributor_count": 18,
        "avg_issue_response_hours": 4.5,
        "avg_pr_merge_hours": 12.0,
        "open_issues": 23,
        "closed_issues_30d": 15,
        "release_count_90d": 4,
        "has_contributing_guide": True,
        "has_code_of_conduct": True,
        "has_issue_templates": True,
        "license": "MIT",
    }


@pytest.fixture()
def dormant_repo_metrics() -> dict[str, Any]:
    """Metrics for a dormant/inactive repository."""
    now = datetime.now(timezone.utc)
    return {
        "github_id": 30002,
        "owner": "abandoned-org",
        "name": "dead-project",
        "full_name": "abandoned-org/dead-project",
        "stars": 340,
        "language": "JavaScript",
        "last_commit_at": (now - timedelta(days=180)).isoformat(),
        "commit_count_90d": 0,
        "contributor_count": 2,
        "avg_issue_response_hours": 720.0,
        "avg_pr_merge_hours": None,
        "open_issues": 47,
        "closed_issues_30d": 0,
        "release_count_90d": 0,
        "has_contributing_guide": False,
        "has_code_of_conduct": False,
        "has_issue_templates": False,
        "license": None,
    }


@pytest.fixture()
def single_maintainer_repo_metrics() -> dict[str, Any]:
    """Metrics for a repo with a single maintainer (bus factor = 1)."""
    now = datetime.now(timezone.utc)
    return {
        "github_id": 30003,
        "owner": "solo-dev",
        "name": "my-lib",
        "full_name": "solo-dev/my-lib",
        "stars": 85,
        "language": "Rust",
        "last_commit_at": (now - timedelta(days=5)).isoformat(),
        "commit_count_90d": 30,
        "contributor_count": 1,
        "avg_issue_response_hours": 24.0,
        "avg_pr_merge_hours": 48.0,
        "open_issues": 8,
        "closed_issues_30d": 3,
        "release_count_90d": 1,
        "has_contributing_guide": True,
        "has_code_of_conduct": False,
        "has_issue_templates": True,
        "license": "Apache-2.0",
    }


# ---------------------------------------------------------------------------
# Webhook Payload Helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def webhook_headers() -> dict[str, str]:
    """Standard headers for a GitHub webhook delivery."""
    return {
        "Content-Type": "application/json",
        "X-GitHub-Event": "issues",
        "X-GitHub-Delivery": str(uuid.uuid4()),
        "X-Hub-Signature-256": "sha256=test_signature",
    }


def build_webhook_payload(
    action: str,
    issue: dict[str, Any],
    repo_owner: str = SAMPLE_REPO_OWNER,
    repo_name: str = SAMPLE_REPO_NAME,
) -> dict[str, Any]:
    """Build a complete GitHub webhook payload for an issues event."""
    return {
        "action": action,
        "issue": issue,
        "repository": {
            "id": 12345,
            "name": repo_name,
            "full_name": f"{repo_owner}/{repo_name}",
            "owner": {"login": repo_owner},
            "html_url": f"https://github.com/{repo_owner}/{repo_name}",
            "private": False,
        },
        "sender": {
            "login": issue.get("user", {}).get("login", "unknown"),
        },
        "installation": {
            "id": 99999,
        },
    }
