"""Skill ORM model (self-referential hierarchy)."""

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import UserSkill


class Skill(Base, UUIDPrimaryKeyMixin):
    """A skill node with optional hierarchy (e.g. Python -> FastAPI)."""

    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True
    )

    # ── Self-referential hierarchy ───────────────────────────────────────
    children: Mapped[List["Skill"]] = relationship(
        "Skill",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="select",
    )
    parent: Mapped[Optional["Skill"]] = relationship(
        "Skill",
        back_populates="children",
        remote_side="Skill.id",
        lazy="joined",
    )

    # ── Reverse to UserSkill ─────────────────────────────────────────────
    user_skills: Mapped[List["UserSkill"]] = relationship(
        "UserSkill", back_populates="skill", cascade="all, delete-orphan", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Skill {self.name} ({self.category})>"
