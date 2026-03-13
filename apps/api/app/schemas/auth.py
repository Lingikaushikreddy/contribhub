"""Pydantic schemas for authentication endpoints."""

from pydantic import BaseModel, Field

from app.schemas.user import UserResponse


class GitHubCallbackRequest(BaseModel):
    """Payload for the GitHub OAuth callback."""

    code: str = Field(..., min_length=1, description="OAuth authorization code from GitHub")


class TokenResponse(BaseModel):
    """Response containing a JWT access token."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
