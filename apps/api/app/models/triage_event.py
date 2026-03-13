"""TriageEvent ORM model — audit log of automated issue triage actions."""

import enum
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.issue import Issue
    from app.models.repo import Repo


class ResponseStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    edited = "edited"
    discarded = "discarded"


class TriageEvent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Record of a single triage action performed on an issue."""

    __tablename__ = "triage_events"

    repo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    issue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    labels_applied: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True, default=list)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    duplicate_of_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issues.id", ondelete="SET NULL"), nullable=True
    )
    response_draft: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_status: Mapped[ResponseStatus] = mapped_column(
        Enum(ResponseStatus, name="response_status", native_enum=True),
        default=ResponseStatus.pending,
        nullable=False,
    )
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ── Relationships ────────────────────────────────────────────────────
    repo: Mapped["Repo"] = relationship("Repo", back_populates="triage_events")
    issue: Mapped["Issue"] = relationship(
        "Issue",
        back_populates="triage_events",
        foreign_keys=[issue_id],
    )
    duplicate_of: Mapped[Optional["Issue"]] = relationship(
        "Issue",
        foreign_keys=[duplicate_of_id],
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<TriageEvent {self.event_type} issue={self.issue_id} conf={self.confidence:.2f}>"
