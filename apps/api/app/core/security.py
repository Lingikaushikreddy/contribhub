"""Security utilities: webhook verification, JWT, GitHub OAuth."""

import hashlib
import hmac
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

import httpx
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db

settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=False)


# ── Webhook Signature Verification ──────────────────────────────────────────


def verify_webhook_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify a GitHub webhook HMAC-SHA256 signature using constant-time comparison.

    Args:
        payload_body: Raw request body bytes.
        signature_header: The X-Hub-Signature-256 header value (``sha256=<hex>``).

    Returns:
        True when the signature is valid.

    Raises:
        HTTPException: 401 if the signature is missing or invalid.
    """
    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Hub-Signature-256 header",
        )

    if not signature_header.startswith("sha256="):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature format — expected sha256=<hex>",
        )

    expected_sig = hmac.new(
        key=settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    received_sig = signature_header[len("sha256="):]

    if not hmac.compare_digest(expected_sig, received_sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Webhook signature verification failed",
        )

    return True


# ── JWT Tokens ───────────────────────────────────────────────────────────────


def create_access_token(
    subject: str,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token.

    Args:
        subject: Token subject — typically the user id.
        extra_claims: Additional claims merged into the payload.
        expires_delta: Custom lifetime; defaults to config value.
    """
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token.

    Returns:
        The decoded payload dict.

    Raises:
        HTTPException: 401 on invalid or expired token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {exc}",
        ) from exc


# ── Current User Dependency ──────────────────────────────────────────────────


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    """FastAPI dependency that resolves the authenticated User from the JWT."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Deferred import to avoid circular dependency at module load time.
    from app.models.user import User

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


# ── GitHub OAuth ─────────────────────────────────────────────────────────────


async def exchange_github_code(code: str) -> dict[str, Any]:
    """Exchange a GitHub OAuth authorization code for an access token.

    Args:
        code: The ``code`` query-param from the OAuth callback.

    Returns:
        Dict containing ``access_token``, ``token_type``, and ``scope``.

    Raises:
        HTTPException: 400 on exchange failure.
    """
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub OAuth token exchange failed",
        )

    data = response.json()
    if "error" in data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitHub OAuth error: {data.get('error_description', data['error'])}",
        )

    return data


async def get_github_user(access_token: str) -> dict[str, Any]:
    """Fetch the authenticated GitHub user's profile.

    Args:
        access_token: A valid GitHub OAuth access token.

    Returns:
        GitHub user profile dict.
    """
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to fetch GitHub user profile",
        )

    return response.json()
