"""GitHub API client with installation token management and rate limiting."""

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from jose import jwt as jose_jwt

from app.core.config import get_settings

settings = get_settings()


class TokenBucket:
    """Simple async token-bucket rate limiter.

    Tokens are refilled at a fixed rate.  ``consume`` awaits until a token
    is available.
    """

    def __init__(self, rate: int, window: int) -> None:
        self.rate = rate  # max tokens (requests) per window
        self.window = window  # window size in seconds
        self.tokens = float(rate)
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def consume(self) -> None:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(self.rate, self.tokens + elapsed * (self.rate / self.window))
            self.last_refill = now

            if self.tokens < 1:
                wait = (1 - self.tokens) * (self.window / self.rate)
                await asyncio.sleep(wait)
                self.tokens = 0
            else:
                self.tokens -= 1


class GitHubService:
    """Async wrapper around the GitHub REST API for a GitHub App installation."""

    def __init__(self) -> None:
        self._rate_limiter = TokenBucket(
            rate=settings.GITHUB_API_RATE_LIMIT,
            window=settings.GITHUB_API_RATE_WINDOW,
        )
        self._installation_tokens: dict[int, tuple[str, datetime]] = {}

    # ── JWT for GitHub App authentication ────────────────────────────────

    def _create_app_jwt(self) -> str:
        """Create a short-lived JWT signed with the App's private key."""
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + (10 * 60),
            "iss": settings.GITHUB_APP_ID,
        }
        return jose_jwt.encode(payload, settings.GITHUB_PRIVATE_KEY, algorithm="RS256")

    # ── Installation token management ────────────────────────────────────

    async def get_installation_token(self, installation_id: int) -> str:
        """Return a cached installation access token, refreshing if expired.

        Args:
            installation_id: GitHub App installation id.

        Returns:
            A valid installation access token string.
        """
        cached = self._installation_tokens.get(installation_id)
        if cached:
            token, expires_at = cached
            if datetime.now(timezone.utc) < expires_at:
                return token

        app_jwt = self._create_app_jwt()
        await self._rate_limiter.consume()

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{settings.GITHUB_API_BASE_URL}/app/installations/{installation_id}/access_tokens",
                headers={
                    "Authorization": f"Bearer {app_jwt}",
                    "Accept": "application/vnd.github+json",
                },
            )
            response.raise_for_status()

        data = response.json()
        token = data["token"]
        expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
        self._installation_tokens[installation_id] = (token, expires_at)
        return token

    # ── Authenticated request helper ─────────────────────────────────────

    async def _request(
        self,
        method: str,
        url: str,
        token: str,
        json_body: Any = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Send an authenticated request to the GitHub API with rate limiting."""
        await self._rate_limiter.consume()

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(
                method,
                url if url.startswith("https://") else f"{settings.GITHUB_API_BASE_URL}{url}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                json=json_body,
                params=params,
            )
            response.raise_for_status()
        return response

    # ── High-level API operations ────────────────────────────────────────

    async def get_repo_issues(
        self,
        installation_id: int,
        owner: str,
        repo: str,
        state: str = "open",
        per_page: int = 100,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """Fetch issues for a repository.

        Args:
            installation_id: GitHub App installation id.
            owner: Repository owner login.
            repo: Repository name.
            state: Issue state filter (open, closed, all).
            per_page: Results per page (max 100).
            page: Page number.

        Returns:
            List of issue dicts from the GitHub API.
        """
        token = await self.get_installation_token(installation_id)
        response = await self._request(
            "GET",
            f"/repos/{owner}/{repo}/issues",
            token,
            params={
                "state": state,
                "per_page": per_page,
                "page": page,
                "sort": "created",
                "direction": "desc",
            },
        )
        return response.json()

    async def apply_labels(
        self,
        installation_id: int,
        owner: str,
        repo: str,
        issue_number: int,
        labels: list[str],
    ) -> list[dict[str, Any]]:
        """Add labels to a GitHub issue.

        Args:
            installation_id: GitHub App installation id.
            owner: Repository owner login.
            repo: Repository name.
            issue_number: Issue number.
            labels: List of label names to apply.

        Returns:
            Updated list of label dicts on the issue.
        """
        token = await self.get_installation_token(installation_id)
        response = await self._request(
            "POST",
            f"/repos/{owner}/{repo}/issues/{issue_number}/labels",
            token,
            json_body={"labels": labels},
        )
        return response.json()

    async def post_comment(
        self,
        installation_id: int,
        owner: str,
        repo: str,
        issue_number: int,
        body: str,
    ) -> dict[str, Any]:
        """Post a comment on a GitHub issue.

        Args:
            installation_id: GitHub App installation id.
            owner: Repository owner login.
            repo: Repository name.
            issue_number: Issue number.
            body: Markdown body of the comment.

        Returns:
            Created comment dict from the GitHub API.
        """
        token = await self.get_installation_token(installation_id)
        response = await self._request(
            "POST",
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
            token,
            json_body={"body": body},
        )
        return response.json()

    async def get_repo_contents(
        self,
        installation_id: int,
        owner: str,
        repo: str,
        path: str = "",
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Fetch repository contents at a given path.

        Args:
            installation_id: GitHub App installation id.
            owner: Repository owner login.
            repo: Repository name.
            path: Path within the repository (empty string for root).

        Returns:
            Directory listing (list) or file content (dict).
        """
        token = await self.get_installation_token(installation_id)
        response = await self._request(
            "GET",
            f"/repos/{owner}/{repo}/contents/{path}",
            token,
        )
        return response.json()

    async def get_repo_details(
        self,
        installation_id: int,
        owner: str,
        repo: str,
    ) -> dict[str, Any]:
        """Fetch full repository metadata.

        Args:
            installation_id: GitHub App installation id.
            owner: Repository owner login.
            repo: Repository name.

        Returns:
            Repository dict from the GitHub API.
        """
        token = await self.get_installation_token(installation_id)
        response = await self._request(
            "GET",
            f"/repos/{owner}/{repo}",
            token,
        )
        return response.json()

    async def get_repo_contributors(
        self,
        installation_id: int,
        owner: str,
        repo: str,
        per_page: int = 100,
    ) -> list[dict[str, Any]]:
        """Fetch contributors for a repository.

        Args:
            installation_id: GitHub App installation id.
            owner: Repository owner login.
            repo: Repository name.
            per_page: Results per page.

        Returns:
            List of contributor dicts.
        """
        token = await self.get_installation_token(installation_id)
        response = await self._request(
            "GET",
            f"/repos/{owner}/{repo}/contributors",
            token,
            params={"per_page": per_page},
        )
        return response.json()


# Module-level singleton
github_service = GitHubService()
