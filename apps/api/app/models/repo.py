"""Repository ORM model."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.issue import Issue
    from app.models.triage_event import TriageEvent


class Repo(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A GitHub repository with an active ContribHub installation."""

    __tablename__ = "repos"

    github_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    owner: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(512), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stars: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    health_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True, default=dict)
    installed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Relationships ────────────────────────────────────────────────────
    issues: Mapped[List["Issue"]] = relationship(
        "Issue", back_populates="repo", cascade="all, delete-orphan", lazy="select"
    )
    triage_events: Mapped[List["TriageEvent"]] = relationship(
        "TriageEvent", back_populates="repo", cascade="all, delete-orphan", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Repo {self.full_name} stars={self.stars}>"
