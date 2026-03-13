"""Pydantic schemas for Matches."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.issue import IssueResponse


class MatchResponse(BaseModel):
    """Public representation of a contributor-issue match."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    issue_id: UUID
    score: float
    skill_match: float
    health_match: float
    interest_match: float
    growth_match: float
    status: str
    feedback: Optional[str] = None
    created_at: datetime


class MatchWithIssueResponse(MatchResponse):
    """Match with the full issue object inlined."""

    issue: Optional[IssueResponse] = None


class MatchFeedbackRequest(BaseModel):
    """Payload for submitting feedback on a match recommendation."""

    rating: str = Field(..., pattern="^(up|down)$")
    reason: Optional[str] = Field(None, max_length=1024)


class MatchStatsResponse(BaseModel):
    """Aggregate match statistics."""

    total_matches: int
    accepted: int
    completed: int
    rejected: int
    average_score: float
    acceptance_rate: float
    completion_rate: float
