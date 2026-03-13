"""Authentication endpoints — GitHub OAuth callback and current-user."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    exchange_github_code,
    get_current_user,
    get_github_user,
)
from app.models.user import User, UserRole
from app.schemas.auth import GitHubCallbackRequest, TokenResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/github/callback",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Exchange GitHub OAuth code for a JWT",
)
async def github_callback(
    payload: GitHubCallbackRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Exchange a GitHub OAuth authorization code for a ContribHub JWT.

    If the GitHub user does not already exist in the database, a new
    User record is created.
    """
    # 1. Exchange the code for a GitHub access token
    token_data = await exchange_github_code(payload.code)
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No access token returned from GitHub",
        )

    # 2. Fetch the GitHub user profile
    gh_user = await get_github_user(access_token)
    github_id = gh_user["id"]
    username = gh_user["login"]
    email = gh_user.get("email")
    avatar_url = gh_user.get("avatar_url")

    # 3. Upsert user
    result = await db.execute(select(User).where(User.github_id == github_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            github_id=github_id,
            username=username,
            email=email,
            avatar_url=avatar_url,
            role=UserRole.contributor,
        )
        db.add(user)
        await db.flush()
    else:
        # Update potentially stale fields
        user.username = username
        user.avatar_url = avatar_url
        if email:
            user.email = email
        db.add(user)
        await db.flush()

    # 4. Issue JWT
    jwt_token = create_access_token(
        subject=str(user.id),
        extra_claims={"github_id": github_id, "username": username},
    )

    return TokenResponse(
        access_token=jwt_token,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the current authenticated user",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    return UserResponse.model_validate(current_user)
