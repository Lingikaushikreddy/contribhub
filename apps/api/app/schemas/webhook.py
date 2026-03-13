"""Pydantic schemas for GitHub webhook payloads."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class WebhookIssue(BaseModel):
    """Subset of the GitHub issue object relevant to triage."""

    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: str = "open"
    user: Optional[dict[str, Any]] = None
    labels: list[dict[str, Any]] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class WebhookRepository(BaseModel):
    """Subset of the GitHub repository object."""

    id: int
    name: str
    full_name: str
    owner: Optional[dict[str, Any]] = None


class WebhookInstallation(BaseModel):
    """GitHub App installation reference."""

    id: int
    account: Optional[dict[str, Any]] = None


class WebhookPayload(BaseModel):
    """Top-level GitHub webhook event payload.

    This captures the common shape; individual event handlers
    inspect nested fields as needed.
    """

    action: Optional[str] = None
    issue: Optional[WebhookIssue] = None
    repository: Optional[WebhookRepository] = None
    installation: Optional[WebhookInstallation] = None
    sender: Optional[dict[str, Any]] = None
