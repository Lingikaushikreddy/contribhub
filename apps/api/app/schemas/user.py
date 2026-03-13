"""Pydantic schemas for User and UserSkill."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Fields required when creating a user from GitHub OAuth."""

    github_id: int
    username: str = Field(..., max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=512)
    role: str = Field(default="contributor", pattern="^(maintainer|contributor|both)$")


class UserUpdate(BaseModel):
    """Optional fields for updating a user profile."""

    email: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=512)
    role: Optional[str] = Field(None, pattern="^(maintainer|contributor|both)$")


class UserSkillResponse(BaseModel):
    """Serialized skill attached to a user."""

    model_config = ConfigDict(from_attributes=True)

    skill_id: UUID
    proficiency: float
    source: str
    skill_name: Optional[str] = None


class UserResponse(BaseModel):
    """Public representation of a User."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    github_id: int
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    created_at: datetime
    updated_at: datetime


class UserWithSkillsResponse(UserResponse):
    """User with resolved skill list."""

    skills: list[UserSkillResponse] = []
