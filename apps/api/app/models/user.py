"""User and UserSkill ORM models."""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.match import Match
    from app.models.skill import Skill


class UserRole(str, enum.Enum):
    maintainer = "maintainer"
    contributor = "contributor"
    both = "both"


class SkillSource(str, enum.Enum):
    inferred = "inferred"
    declared = "declared"


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A GitHub user who has authenticated with ContribHub."""

    __tablename__ = "users"

    github_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=True),
        default=UserRole.contributor,
        nullable=False,
    )

    # ── Relationships ────────────────────────────────────────────────────
    skills: Mapped[List["UserSkill"]] = relationship(
        "UserSkill", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    matches: Mapped[List["Match"]] = relationship(
        "Match", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role.value})>"


class UserSkill(Base):
    """Association between a user and a skill with proficiency tracking."""

    __tablename__ = "user_skills"
    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True
    )
    proficiency: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    source: Mapped[SkillSource] = mapped_column(
        Enum(SkillSource, name="skill_source", native_enum=True),
        default=SkillSource.inferred,
        nullable=False,
    )

    # ── Relationships ────────────────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="user_skills", lazy="joined")

    def __repr__(self) -> str:
        return f"<UserSkill user={self.user_id} skill={self.skill_id} prof={self.proficiency}>"
