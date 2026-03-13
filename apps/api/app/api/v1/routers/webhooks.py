"""GitHub webhook receiver endpoint."""

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_webhook_signature
from app.models.issue import Issue
from app.models.repo import Repo
from app.schemas.webhook import WebhookPayload
from app.services.triage_service import triage_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post(
    "/github",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive GitHub webhook events",
)
async def receive_github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(None),
    x_github_event: str | None = Header(None),
    x_github_delivery: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Verify and process incoming GitHub webhook events.

    Supported events:
        - ``issues`` (opened, edited, closed, reopened, labeled)
        - ``installation`` (created, deleted)

    All other events are acknowledged but not processed.
    """
    # 1. Read raw body for signature verification
    body = await request.body()
    verify_webhook_signature(body, x_hub_signature_256 or "")

    # 2. Parse payload
    payload_json = await request.json()
    payload = WebhookPayload.model_validate(payload_json)

    event_type = x_github_event or "unknown"
    action = payload.action or "unknown"
    delivery_id = x_github_delivery or "none"

    logger.info(
        "Webhook received: event=%s action=%s delivery=%s",
        event_type,
        action,
        delivery_id,
    )

    # 3. Route by event type
    if event_type == "issues":
        await _handle_issue_event(db, payload, action)
    elif event_type == "installation":
        await _handle_installation_event(db, payload, action)
    else:
        logger.info("Ignoring unhandled event type: %s", event_type)

    return {"status": "accepted", "delivery_id": delivery_id}


async def _handle_issue_event(
    db: AsyncSession,
    payload: WebhookPayload,
    action: str,
) -> None:
    """Process an issue webhook event."""
    if payload.issue is None or payload.repository is None:
        logger.warning("Issue event missing issue or repository data")
        return

    gh_issue = payload.issue
    gh_repo = payload.repository

    # Look up the repo
    result = await db.execute(
        select(Repo).where(Repo.github_id == gh_repo.id)
    )
    repo = result.scalar_one_or_none()
    if repo is None:
        logger.warning("Received event for untracked repo: %s", gh_repo.full_name)
        return

    # Upsert the issue
    issue_result = await db.execute(
        select(Issue).where(Issue.github_id == gh_issue.id, Issue.repo_id == repo.id)
    )
    issue = issue_result.scalar_one_or_none()

    author = gh_issue.user.get("login", "unknown") if gh_issue.user else "unknown"
    label_names = [lbl.get("name", "") for lbl in gh_issue.labels] if gh_issue.labels else []

    if issue is None:
        issue = Issue(
            repo_id=repo.id,
            github_id=gh_issue.id,
            number=gh_issue.number,
            title=gh_issue.title,
            body=gh_issue.body,
            state=gh_issue.state,
            author=author,
            labels=label_names,
        )
        db.add(issue)
        await db.flush()
    else:
        issue.title = gh_issue.title
        issue.body = gh_issue.body
        issue.state = gh_issue.state
        issue.labels = label_names
        if gh_issue.state == "closed":
            issue.closed_at = datetime.now(timezone.utc)
        db.add(issue)
        await db.flush()

    # Trigger triage on newly opened issues
    if action == "opened":
        installation_id = (
            payload.installation.id if payload.installation else None
        )
        try:
            await triage_service.triage_issue(
                db, issue, installation_id=installation_id
            )
        except Exception:
            logger.exception("Triage failed for issue #%d", gh_issue.number)


async def _handle_installation_event(
    db: AsyncSession,
    payload: WebhookPayload,
    action: str,
) -> None:
    """Process an installation webhook event (app installed/uninstalled)."""
    if payload.installation is None:
        return

    installation = payload.installation
    logger.info(
        "Installation event: action=%s installation_id=%d",
        action,
        installation.id,
    )

    if action == "deleted":
        # Mark repos from this installation as removed (soft delete via config flag)
        account = installation.account
        if account and account.get("login"):
            result = await db.execute(
                select(Repo).where(Repo.owner == account["login"])
            )
            repos = result.scalars().all()
            for repo in repos:
                existing_config = repo.config or {}
                existing_config["installation_deleted"] = True
                repo.config = existing_config
                db.add(repo)
            await db.flush()
