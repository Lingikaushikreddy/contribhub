"""Repository management endpoints."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.issue import Issue
from app.models.repo import Repo
from app.models.triage_event import TriageEvent
from app.models.user import User
from app.schemas.repo import HealthScoreResponse, RepoConfigUpdate, RepoResponse

router = APIRouter(prefix="/repos", tags=["repos"])


@router.get(
    "",
    response_model=list[RepoResponse],
    summary="List installed repositories",
)
async def list_repos(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    language: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[RepoResponse]:
    """Return a paginated list of repositories with an active ContribHub installation."""
    query = select(Repo).order_by(Repo.stars.desc())

    if language:
        query = query.where(Repo.language == language)

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    repos = result.scalars().all()
    return [RepoResponse.model_validate(r) for r in repos]


@router.get(
    "/{repo_id}",
    response_model=RepoResponse,
    summary="Get repository details",
)
async def get_repo(
    repo_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> RepoResponse:
    """Return full details for a single installed repository."""
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    return RepoResponse.model_validate(repo)


@router.get(
    "/{repo_id}/health",
    response_model=HealthScoreResponse,
    summary="Get repository health score breakdown",
)
async def get_repo_health(
    repo_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> HealthScoreResponse:
    """Return a detailed health-score breakdown for a repository.

    In a production system these sub-scores are calculated by the
    health worker; here we return the stored overall score split
    into weighted components.
    """
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")

    overall = repo.health_score

    # Derive sub-scores from overall (placeholder split — the health worker
    # will store these individually in a future iteration).
    return HealthScoreResponse(
        repo_id=repo.id,
        overall=overall,
        documentation=min(1.0, overall * 1.1),
        issue_responsiveness=min(1.0, overall * 0.95),
        pr_merge_rate=min(1.0, overall * 1.05),
        community_engagement=min(1.0, overall * 0.9),
        release_cadence=min(1.0, overall * 0.85),
        calculated_at=repo.updated_at,
    )


@router.post(
    "/{repo_id}/sync",
    response_model=RepoResponse,
    summary="Trigger repository re-sync",
)
async def sync_repo(
    repo_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> RepoResponse:
    """Queue a full re-sync of repository issues and metadata.

    In this synchronous implementation the last_synced_at timestamp is
    updated immediately.  A production deployment would enqueue a
    background task via Dramatiq.
    """
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")

    repo.last_synced_at = datetime.now(timezone.utc)
    db.add(repo)
    await db.flush()

    return RepoResponse.model_validate(repo)


@router.put(
    "/{repo_id}/config",
    response_model=RepoResponse,
    summary="Update triage configuration",
)
async def update_repo_config(
    repo_id: UUID,
    config_update: RepoConfigUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> RepoResponse:
    """Merge new triage-configuration fields into the repository's JSONB config."""
    repo = await db.get(Repo, repo_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")

    existing_config = repo.config or {}
    update_data = config_update.model_dump(exclude_none=True)
    existing_config.update(update_data)
    repo.config = existing_config
    db.add(repo)
    await db.flush()

    return RepoResponse.model_validate(repo)
