"""Match ORM model — contributor-to-issue recommendation."""

import enum
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.issue import Issue
    from app.models.user import User


class MatchStatus(str, enum.Enum):
    recommended = "recommended"
    viewed = "viewed"
    accepted = "accepted"
    completed = "completed"
    rejected = "rejected"


class Match(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A scored recommendation linking a contributor to an issue."""

    __tablename__ = "matches"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    issue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("issues.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    skill_match: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    health_match: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    interest_match: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    growth_match: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus, name="match_status", native_enum=True),
        default=MatchStatus.recommended,
        nullable=False,
    )
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── Relationships ────────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="matches")
    issue: Mapped["Issue"] = relationship("Issue", back_populates="matches", lazy="joined")

    def __repr__(self) -> str:
        return f"<Match user={self.user_id} issue={self.issue_id} score={self.score:.2f}>"
