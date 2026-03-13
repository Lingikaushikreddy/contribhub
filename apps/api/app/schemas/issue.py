"""Pydantic schemas for Issues."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IssueResponse(BaseModel):
    """Public representation of a triaged issue."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    repo_id: UUID
    github_id: int
    number: int
    title: str
    body: Optional[str] = None
    state: str
    author: Optional[str] = None
    labels: Optional[list[Any]] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    complexity_score: Optional[int] = None
    quality_score: Optional[int] = None
    is_claimed: bool
    embedding_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None


class IssueListParams(BaseModel):
    """Query parameters for listing issues."""

    category: Optional[str] = Field(None, pattern="^(bug|feature|question|docs|chore)$")
    priority: Optional[str] = Field(None, pattern="^(P0|P1|P2|P3)$")
    complexity_min: Optional[int] = Field(None, ge=1, le=10)
    complexity_max: Optional[int] = Field(None, ge=1, le=10)
    state: Optional[str] = Field(default="open", pattern="^(open|closed|all)$")
    is_claimed: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
