"""Pydantic schemas for Triage events and results."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TriageResult(BaseModel):
    """Result returned after an issue is triaged by the AI pipeline."""

    issue_id: UUID
    category: str
    priority: str
    complexity_score: int = Field(..., ge=1, le=10)
    quality_score: int = Field(..., ge=1, le=10)
    labels: list[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    is_duplicate: bool = False
    duplicate_of_number: Optional[int] = None
    response_draft: Optional[str] = None
    processing_time_ms: int


class TriageEventResponse(BaseModel):
    """Public representation of a triage event."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    repo_id: UUID
    issue_id: UUID
    event_type: str
    labels_applied: Optional[list[Any]] = None
    confidence: float
    duplicate_of_id: Optional[UUID] = None
    response_draft: Optional[str] = None
    response_status: str
    processing_time_ms: Optional[int] = None
    created_at: datetime


class TriageStatsResponse(BaseModel):
    """Aggregate triage statistics for a repository."""

    repo_id: UUID
    total_events: int
    average_confidence: float
    average_processing_time_ms: float
    events_last_24h: int
    events_last_7d: int
    accuracy_rate: float
    category_distribution: dict[str, int]
    auto_responses_approved: int
    auto_responses_discarded: int


class TriageApproveRequest(BaseModel):
    """Payload for approving or editing a triage response draft."""

    action: str = Field(..., pattern="^(approve|edit|discard)$")
    edited_response: Optional[str] = Field(None, max_length=10000)
