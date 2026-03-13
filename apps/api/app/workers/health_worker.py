"""Scheduled worker that recalculates project health scores daily.

Uses APScheduler to run the recalculation on a cron-like schedule.
In production this would be started as a separate process alongside
the API server.
"""

import asyncio
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.database import async_session_factory
from app.models.issue import Issue
from app.models.repo import Repo
from app.models.triage_event import ResponseStatus, TriageEvent

logger = logging.getLogger(__name__)
settings = get_settings()


async def recalculate_health_scores() -> None:
    """Recalculate health scores for every tracked repository.

    Health score components:
        - issue_responsiveness: fraction of issues triaged within 24h
        - triage_accuracy: fraction of triage responses approved
        - issue_resolution_rate: fraction of issues that are closed
        - community_score: normalized star count (log scale)
        - freshness: days since last sync (inverse)

    Each component is [0, 1]; the overall score is a weighted average.
    """
    logger.info("Starting health-score recalculation")

    async with async_session_factory() as db:
        try:
            result = await db.execute(select(Repo))
            repos = result.scalars().all()

            for repo in repos:
                score = await _calculate_repo_health(db, repo)
                repo.health_score = round(score, 4)
                db.add(repo)

            await db.commit()
            logger.info("Health scores recalculated for %d repositories", len(repos))
        except Exception:
            await db.rollback()
            logger.exception("Health-score recalculation failed")
            raise


async def _calculate_repo_health(db, repo: Repo) -> float:
    """Calculate a composite health score for a single repository."""
    weights = {
        "responsiveness": 0.25,
        "accuracy": 0.25,
        "resolution": 0.20,
        "community": 0.15,
        "freshness": 0.15,
    }

    # ── Issue responsiveness ─────────────────────────────────────────────
    total_issues_result = await db.execute(
        select(func.count()).where(Issue.repo_id == repo.id)
    )
    total_issues = total_issues_result.scalar() or 0

    triaged_result = await db.execute(
        select(func.count())
        .where(TriageEvent.repo_id == repo.id)
        .where(TriageEvent.processing_time_ms.isnot(None))
        .where(TriageEvent.processing_time_ms <= 86_400_000)  # within 24h
    )
    triaged_fast = triaged_result.scalar() or 0
    responsiveness = triaged_fast / max(total_issues, 1)

    # ── Triage accuracy ──────────────────────────────────────────────────
    total_events_result = await db.execute(
        select(func.count()).where(TriageEvent.repo_id == repo.id)
    )
    total_events = total_events_result.scalar() or 0

    approved_result = await db.execute(
        select(func.count()).where(
            TriageEvent.repo_id == repo.id,
            TriageEvent.response_status == ResponseStatus.approved,
        )
    )
    approved = approved_result.scalar() or 0
    accuracy = approved / max(total_events, 1)

    # ── Issue resolution rate ────────────────────────────────────────────
    closed_result = await db.execute(
        select(func.count()).where(Issue.repo_id == repo.id, Issue.state == "closed")
    )
    closed = closed_result.scalar() or 0
    resolution = closed / max(total_issues, 1)

    # ── Community score (log-scaled stars) ────────────────────────────────
    import math

    community = min(1.0, math.log10(max(repo.stars, 1) + 1) / 5.0)

    # ── Freshness ────────────────────────────────────────────────────────
    if repo.last_synced_at:
        days_since_sync = (datetime.now(timezone.utc) - repo.last_synced_at).days
        freshness = max(0.0, 1.0 - days_since_sync / 30.0)
    else:
        freshness = 0.3  # never synced

    overall = (
        weights["responsiveness"] * min(1.0, responsiveness)
        + weights["accuracy"] * min(1.0, accuracy)
        + weights["resolution"] * min(1.0, resolution)
        + weights["community"] * community
        + weights["freshness"] * freshness
    )

    return min(1.0, max(0.0, overall))


def start_health_scheduler() -> AsyncIOScheduler:
    """Create and start the APScheduler instance for the health worker.

    Runs ``recalculate_health_scores`` once daily at 03:00 UTC.
    """
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        recalculate_health_scores,
        trigger="cron",
        hour=3,
        minute=0,
        timezone="UTC",
        id="health_score_recalculation",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Health-score scheduler started (daily at 03:00 UTC)")
    return scheduler
