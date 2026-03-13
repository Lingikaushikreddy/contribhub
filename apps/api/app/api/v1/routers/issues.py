"""Issue listing, detail, and manual triage endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.issue import Issue, IssueCategory, IssuePriority
from app.models.triage_event import TriageEvent
from app.models.user import User
from app.schemas.issue import IssueResponse
from app.schemas.triage import TriageEventResponse, TriageResult
from app.services.triage_service import triage_service

router = APIRouter(tags=["issues"])


@router.get(
    "/repos/{repo_id}/issues",
    response_model=list[IssueResponse],
    summary="List issues for a repository",
)
async def list_repo_issues(
    repo_id: UUID,
    category: str | None = Query(None, pattern="^(bug|feature|question|docs|chore)$"),
    priority: str | None = Query(None, pattern="^(P0|P1|P2|P3)$"),
    complexity_min: int | None = Query(None, ge=1, le=10),
    complexity_max: int | None = Query(None, ge=1, le=10),
    state: str = Query("open", pattern="^(open|closed|all)$"),
    is_claimed: bool | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[IssueResponse]:
    """Return a filtered, paginated list of issues for a repository."""
    query = select(Issue).where(Issue.repo_id == repo_id).order_by(Issue.created_at.desc())

    if state != "all":
        query = query.where(Issue.state == state)

    if category:
        try:
            query = query.where(Issue.category == IssueCategory(category))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {category}",
            )

    if priority:
        try:
            query = query.where(Issue.priority == IssuePriority(priority))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority: {priority}",
            )

    if complexity_min is not None:
        query = query.where(Issue.complexity_score >= complexity_min)
    if complexity_max is not None:
        query = query.where(Issue.complexity_score <= complexity_max)
    if is_claimed is not None:
        query = query.where(Issue.is_claimed == is_claimed)

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    issues = result.scalars().all()
    return [IssueResponse.model_validate(i) for i in issues]


@router.get(
    "/issues/{issue_id}",
    response_model=IssueResponse,
    summary="Get issue detail with triage history",
)
async def get_issue(
    issue_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> dict:
    """Return issue details along with its triage event history."""
    issue = await db.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

    # Fetch triage history
    triage_result = await db.execute(
        select(TriageEvent)
        .where(TriageEvent.issue_id == issue_id)
        .order_by(TriageEvent.created_at.desc())
    )
    triage_events = triage_result.scalars().all()

    issue_data = IssueResponse.model_validate(issue).model_dump()
    issue_data["triage_history"] = [
        TriageEventResponse.model_validate(e).model_dump() for e in triage_events
    ]
    return issue_data


@router.post(
    "/issues/{issue_id}/triage",
    response_model=TriageResult,
    summary="Manually trigger issue triage",
)
async def trigger_triage(
    issue_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> TriageResult:
    """Run the triage pipeline on a specific issue.

    This is the manual trigger; automated triage runs via the webhook
    worker.
    """
    issue = await db.get(Issue, issue_id)
    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

    result = await triage_service.triage_issue(db, issue)
    return result
