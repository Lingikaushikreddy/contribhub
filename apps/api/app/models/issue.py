"""Issue ORM model."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.match import Match
    from app.models.repo import Repo
    from app.models.triage_event import TriageEvent


class IssueCategory(str, enum.Enum):
    bug = "bug"
    feature = "feature"
    question = "question"
    docs = "docs"
    chore = "chore"


class IssuePriority(str, enum.Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class Issue(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A GitHub issue tracked by ContribHub."""

    __tablename__ = "issues"

    repo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    github_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(1024), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    state: Mapped[str] = mapped_column(String(20), default="open", nullable=False, index=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    labels: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True, default=list)
    category: Mapped[Optional[IssueCategory]] = mapped_column(
        Enum(IssueCategory, name="issue_category", native_enum=True), nullable=True
    )
    priority: Mapped[Optional[IssuePriority]] = mapped_column(
        Enum(IssuePriority, name="issue_priority", native_enum=True), nullable=True
    )
    complexity_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quality_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_claimed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    embedding_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Relationships ────────────────────────────────────────────────────
    repo: Mapped["Repo"] = relationship("Repo", back_populates="issues")
    matches: Mapped[List["Match"]] = relationship(
        "Match", back_populates="issue", cascade="all, delete-orphan", lazy="select"
    )
    triage_events: Mapped[List["TriageEvent"]] = relationship(
        "TriageEvent", back_populates="issue", cascade="all, delete-orphan", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Issue #{self.number} {self.title[:40]}>"
