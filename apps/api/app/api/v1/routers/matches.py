"""Match recommendation endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.match import Match, MatchStatus
from app.models.user import User
from app.schemas.match import (
    MatchFeedbackRequest,
    MatchResponse,
    MatchStatsResponse,
    MatchWithIssueResponse,
)
from app.services.matching_service import matching_service

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get(
    "",
    response_model=list[MatchWithIssueResponse],
    summary="Get personalized issue recommendations",
)
async def get_recommendations(
    refresh: bool = Query(False, description="Force regeneration of recommendations"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MatchWithIssueResponse]:
    """Return scored issue recommendations for the current user.

    Pass ``refresh=true`` to discard stale recommendations and recompute.
    """
    if refresh:
        # Delete existing recommended (unactioned) matches before regenerating
        existing = await db.execute(
            select(Match).where(
                Match.user_id == current_user.id,
                Match.status == MatchStatus.recommended,
            )
        )
        for m in existing.scalars().all():
            await db.delete(m)
        await db.flush()

    # Check for existing recommendations
    result = await db.execute(
        select(Match)
        .where(Match.user_id == current_user.id, Match.status == MatchStatus.recommended)
        .order_by(Match.score.desc())
        .limit(limit)
    )
    matches = list(result.scalars().all())

    if not matches:
        matches = await matching_service.generate_recommendations(
            db, current_user.id, limit=limit
        )

    return [MatchWithIssueResponse.model_validate(m) for m in matches]


@router.post(
    "/{match_id}/feedback",
    response_model=MatchResponse,
    summary="Submit feedback on a match",
)
async def submit_feedback(
    match_id: UUID,
    feedback: MatchFeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MatchResponse:
    """Record thumbs-up/down feedback on a recommendation.

    - ``up`` transitions the match status to ``accepted``.
    - ``down`` transitions the match status to ``rejected``.
    """
    match = await db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    if match.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your match")

    if feedback.rating == "up":
        match.status = MatchStatus.accepted
    else:
        match.status = MatchStatus.rejected

    match.feedback = feedback.reason
    db.add(match)
    await db.flush()

    return MatchResponse.model_validate(match)


@router.get(
    "/stats",
    response_model=MatchStatsResponse,
    summary="Get match success metrics",
)
async def get_match_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MatchStatsResponse:
    """Return aggregate match statistics for the current user."""
    stats = await matching_service.get_match_stats(db, user_id=current_user.id)
    return MatchStatsResponse(**stats)
