"""Triage statistics and event management endpoints."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.issue import Issue
from app.models.repo import Repo
from app.models.triage_event import ResponseStatus, TriageEvent
from app.models.user import User
from app.schemas.triage import TriageApproveRequest, TriageEventResponse, TriageStatsResponse
from app.services.github_service import github_service

router = APIRouter(tags=["triage"])


@router.get(
    "/repos/{repo_id}/triage/stats",
    response_model=TriageStatsResponse,
    summary="Get triage statistics for a repository",
)
async def get_triage_stats(
    repo_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> TriageStatsResponse:
    """Return accuracy, volume, and response-time metrics for triage on a repo."""
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")

    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)

    base = select(TriageEvent).where(TriageEvent.repo_id == repo_id)

    # Total events
    total_result = await db.execute(
        select(func.count()).select_from(base.subquery())
    )
    total_events = total_result.scalar() or 0

    # Average confidence
    avg_conf_result = await db.execute(
        select(func.avg(TriageEvent.confidence)).where(TriageEvent.repo_id == repo_id)
    )
    avg_confidence = float(avg_conf_result.scalar() or 0.0)

    # Average processing time
    avg_time_result = await db.execute(
        select(func.avg(TriageEvent.processing_time_ms)).where(TriageEvent.repo_id == repo_id)
    )
    avg_processing_time = float(avg_time_result.scalar() or 0.0)

    # Events in last 24h
    events_24h_result = await db.execute(
        select(func.count()).where(
            TriageEvent.repo_id == repo_id,
            TriageEvent.created_at >= day_ago,
        )
    )
    events_24h = events_24h_result.scalar() or 0

    # Events in last 7d
    events_7d_result = await db.execute(
        select(func.count()).where(
            TriageEvent.repo_id == repo_id,
            TriageEvent.created_at >= week_ago,
        )
    )
    events_7d = events_7d_result.scalar() or 0

    # Accuracy: proportion of approved responses
    approved_result = await db.execute(
        select(func.count()).where(
            TriageEvent.repo_id == repo_id,
            TriageEvent.response_status == ResponseStatus.approved,
        )
    )
    approved = approved_result.scalar() or 0

    discarded_result = await db.execute(
        select(func.count()).where(
            TriageEvent.repo_id == repo_id,
            TriageEvent.response_status == ResponseStatus.discarded,
        )
    )
    discarded = discarded_result.scalar() or 0

    reviewed = approved + discarded
    accuracy_rate = approved / reviewed if reviewed > 0 else 0.0

    # Category distribution from linked issues
    cat_result = await db.execute(
        select(Issue.category, func.count())
        .join(TriageEvent, TriageEvent.issue_id == Issue.id)
        .where(TriageEvent.repo_id == repo_id)
        .group_by(Issue.category)
    )
    category_distribution = {
        (row[0].value if row[0] else "unknown"): row[1] for row in cat_result.all()
    }

    return TriageStatsResponse(
        repo_id=repo_id,
        total_events=total_events,
        average_confidence=round(avg_confidence, 4),
        average_processing_time_ms=round(avg_processing_time, 2),
        events_last_24h=events_24h,
        events_last_7d=events_7d,
        accuracy_rate=round(accuracy_rate, 4),
        category_distribution=category_distribution,
        auto_responses_approved=approved,
        auto_responses_discarded=discarded,
    )


@router.get(
    "/repos/{repo_id}/triage/events",
    response_model=list[TriageEventResponse],
    summary="List recent triage events",
)
async def list_triage_events(
    repo_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[TriageEventResponse]:
    """Return a paginated list of triage events for a repository."""
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")

    result = await db.execute(
        select(TriageEvent)
        .where(TriageEvent.repo_id == repo_id)
        .order_by(TriageEvent.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    events = result.scalars().all()
    return [TriageEventResponse.model_validate(e) for e in events]


@router.post(
    "/triage/events/{event_id}/approve",
    response_model=TriageEventResponse,
    summary="Approve, edit, or discard a triage response draft",
)
async def approve_triage_event(
    event_id: UUID,
    payload: TriageApproveRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> TriageEventResponse:
    """Update the response status of a triage event.

    - ``approve``: marks the response as approved; if the response has not
      yet been posted to GitHub, it will be posted now.
    - ``edit``: replaces the draft with ``edited_response`` and marks it
      as edited.
    - ``discard``: marks the response as discarded (will not be posted).
    """
    event = await db.get(TriageEvent, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Triage event not found")

    if payload.action == "approve":
        event.response_status = ResponseStatus.approved
    elif payload.action == "edit":
        if not payload.edited_response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="edited_response is required when action is 'edit'",
            )
        event.response_draft = payload.edited_response
        event.response_status = ResponseStatus.edited
    elif payload.action == "discard":
        event.response_status = ResponseStatus.discarded

    db.add(event)
    await db.flush()

    return TriageEventResponse.model_validate(event)
