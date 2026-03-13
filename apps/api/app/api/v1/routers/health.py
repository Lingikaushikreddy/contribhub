"""Health and readiness check endpoints."""

import logging
from datetime import datetime, timezone

import redis.asyncio as aioredis
from fastapi import APIRouter, status
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import engine

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Basic liveness check",
)
async def health_check() -> dict:
    """Return a simple liveness response.

    This endpoint does not check external dependencies — it only confirms
    that the API process is running and can serve requests.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check with dependency verification",
)
async def readiness_check() -> dict:
    """Verify that all critical dependencies (Postgres, Redis) are reachable.

    Returns 200 only when every dependency is healthy.  Returns 503 if any
    check fails.
    """
    checks: dict[str, dict] = {}

    # ── Postgres ─────────────────────────────────────────────────────────
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.scalar()
        checks["postgres"] = {"status": "ok"}
    except Exception as exc:
        logger.error("Postgres readiness check failed: %s", exc)
        checks["postgres"] = {"status": "error", "detail": str(exc)}

    # ── Redis ────────────────────────────────────────────────────────────
    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL, decode_responses=True, socket_connect_timeout=5
        )
        await redis_client.ping()
        await redis_client.aclose()
        checks["redis"] = {"status": "ok"}
    except Exception as exc:
        logger.error("Redis readiness check failed: %s", exc)
        checks["redis"] = {"status": "error", "detail": str(exc)}

    # ── Aggregate ────────────────────────────────────────────────────────
    all_ok = all(c["status"] == "ok" for c in checks.values())

    return {
        "status": "ready" if all_ok else "degraded",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
