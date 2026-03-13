"""Pydantic schemas for Repository."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RepoResponse(BaseModel):
    """Public representation of an installed repository."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    github_id: int
    owner: str
    name: str
    full_name: str
    description: Optional[str] = None
    stars: int
    language: Optional[str] = None
    health_score: float
    config: Optional[dict[str, Any]] = None
    installed_at: Optional[datetime] = None
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class RepoConfigUpdate(BaseModel):
    """Payload for updating a repo's triage configuration."""

    auto_label: Optional[bool] = None
    auto_respond: Optional[bool] = None
    auto_assign: Optional[bool] = None
    priority_labels: Optional[list[str]] = None
    excluded_labels: Optional[list[str]] = None
    complexity_threshold: Optional[int] = Field(None, ge=1, le=10)
    language_model: Optional[str] = Field(None, pattern="^(openai|anthropic)$")


class HealthScoreResponse(BaseModel):
    """Breakdown of a repository's health score."""

    repo_id: UUID
    overall: float = Field(..., ge=0.0, le=1.0)
    documentation: float = Field(..., ge=0.0, le=1.0)
    issue_responsiveness: float = Field(..., ge=0.0, le=1.0)
    pr_merge_rate: float = Field(..., ge=0.0, le=1.0)
    community_engagement: float = Field(..., ge=0.0, le=1.0)
    release_cadence: float = Field(..., ge=0.0, le=1.0)
    calculated_at: datetime
