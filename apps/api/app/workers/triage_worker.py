"""Dramatiq actor for processing webhook-triggered triage jobs.

Events are enqueued by the webhook endpoint and consumed asynchronously
by this worker, keeping the webhook response fast (< 200ms).
"""

import asyncio
import logging
import uuid

import dramatiq
from dramatiq.brokers.redis import RedisBroker

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Broker setup ─────────────────────────────────────────────────────────────
redis_broker = RedisBroker(url=settings.REDIS_URL)
dramatiq.set_broker(redis_broker)


def _run_async(coro):
    """Run an async coroutine in a new event loop (worker threads are sync)."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@dramatiq.actor(max_retries=3, min_backoff=1000, max_backoff=60000)
def process_triage_event(issue_id: str, installation_id: int | None = None) -> None:
    """Process an issue triage job from the queue.

    Args:
        issue_id: UUID string of the issue to triage.
        installation_id: GitHub App installation id for API calls.
    """
    _run_async(_async_process_triage(issue_id, installation_id))


async def _async_process_triage(
    issue_id_str: str, installation_id: int | None
) -> None:
    """Async implementation of the triage worker."""
    from app.core.database import async_session_factory
    from app.models.issue import Issue
    from app.services.triage_service import triage_service

    issue_uuid = uuid.UUID(issue_id_str)

    async with async_session_factory() as db:
        try:
            issue = await db.get(Issue, issue_uuid)
            if issue is None:
                logger.error("Triage worker: issue %s not found", issue_id_str)
                return

            result = await triage_service.triage_issue(
                db, issue, installation_id=installation_id
            )
            await db.commit()

            logger.info(
                "Triage complete: issue=%s category=%s priority=%s confidence=%.2f time=%dms",
                issue_id_str,
                result.category,
                result.priority,
                result.confidence,
                result.processing_time_ms,
            )
        except Exception:
            await db.rollback()
            logger.exception("Triage worker failed for issue %s", issue_id_str)
            raise
