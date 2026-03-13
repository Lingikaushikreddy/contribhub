"""Triage orchestration service.

Coordinates issue classification, duplicate detection, response
generation, label application, and triage-event recording.
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.issue import Issue, IssueCategory, IssuePriority
from app.models.triage_event import ResponseStatus, TriageEvent
from app.schemas.triage import TriageResult
from app.services.github_service import github_service

settings = get_settings()


class TriageService:
    """Orchestrates the full issue-triage pipeline."""

    # ── LLM classification ───────────────────────────────────────────────

    async def _classify_issue(self, title: str, body: str) -> dict[str, Any]:
        """Call the LLM to classify an issue by category, priority, and complexity.

        Falls back to heuristic classification if the LLM call fails.
        """
        prompt = (
            "You are an expert open-source issue triager. Analyze the following GitHub issue "
            "and return a JSON object with these fields:\n"
            '- "category": one of "bug", "feature", "question", "docs", "chore"\n'
            '- "priority": one of "P0" (critical), "P1" (high), "P2" (medium), "P3" (low)\n'
            '- "complexity_score": integer 1-10 (1=trivial, 10=very complex)\n'
            '- "quality_score": integer 1-10 (1=poor, 10=excellent)\n'
            '- "labels": list of suggested label strings\n'
            '- "response_draft": a helpful initial response to the issue author\n'
            "Respond ONLY with the JSON object.\n\n"
            f"Title: {title}\n\nBody:\n{body or '(no body)'}"
        )

        try:
            if settings.ANTHROPIC_API_KEY:
                return await self._classify_with_anthropic(prompt)
            elif settings.OPENAI_API_KEY:
                return await self._classify_with_openai(prompt)
            else:
                return self._classify_heuristic(title, body)
        except Exception:
            return self._classify_heuristic(title, body)

    async def _classify_with_anthropic(self, prompt: str) -> dict[str, Any]:
        """Classify via the Anthropic Messages API."""
        import json

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()

        data = response.json()
        text = data["content"][0]["text"]
        # Strip markdown code fences if present
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        return json.loads(text)

    async def _classify_with_openai(self, prompt: str) -> dict[str, Any]:
        """Classify via the OpenAI Chat Completions API."""
        import json

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()

        data = response.json()
        return json.loads(data["choices"][0]["message"]["content"])

    def _classify_heuristic(self, title: str, body: str) -> dict[str, Any]:
        """Keyword-based fallback when no LLM key is configured."""
        combined = f"{title} {body or ''}".lower()

        # Category detection
        if any(w in combined for w in ["bug", "error", "crash", "broken", "fix", "fail"]):
            category = "bug"
        elif any(w in combined for w in ["feature", "request", "enhancement", "add", "new"]):
            category = "feature"
        elif any(w in combined for w in ["question", "how", "help", "why", "?"]):
            category = "question"
        elif any(w in combined for w in ["doc", "readme", "typo", "documentation"]):
            category = "docs"
        else:
            category = "chore"

        # Priority detection
        if any(w in combined for w in ["critical", "urgent", "security", "cve", "vulnerability"]):
            priority = "P0"
        elif any(w in combined for w in ["important", "blocker", "regression"]):
            priority = "P1"
        elif any(w in combined for w in ["minor", "low", "cosmetic", "nit"]):
            priority = "P3"
        else:
            priority = "P2"

        # Simple complexity estimate based on body length
        body_length = len(body) if body else 0
        complexity = min(10, max(1, body_length // 200 + 3))

        return {
            "category": category,
            "priority": priority,
            "complexity_score": complexity,
            "quality_score": 5,
            "labels": [category, priority],
            "response_draft": None,
        }

    # ── Duplicate detection ──────────────────────────────────────────────

    async def _check_duplicates(
        self,
        db: AsyncSession,
        repo_id: uuid.UUID,
        title: str,
        body: str,
    ) -> Optional[int]:
        """Check if this issue is a likely duplicate of an existing open issue.

        Uses simple title similarity. A production system would use vector
        embeddings, but this gives a functional baseline.
        """
        result = await db.execute(
            select(Issue).where(
                Issue.repo_id == repo_id,
                Issue.state == "open",
            ).limit(200)
        )
        existing_issues = result.scalars().all()

        title_lower = title.lower()
        for existing in existing_issues:
            existing_title = existing.title.lower()
            # Jaccard similarity on word sets
            words_a = set(title_lower.split())
            words_b = set(existing_title.split())
            if not words_a or not words_b:
                continue
            intersection = words_a & words_b
            union = words_a | words_b
            similarity = len(intersection) / len(union)
            if similarity > 0.7:
                return existing.number

        return None

    # ── Main triage pipeline ─────────────────────────────────────────────

    async def triage_issue(
        self,
        db: AsyncSession,
        issue: Issue,
        installation_id: Optional[int] = None,
    ) -> TriageResult:
        """Run the full triage pipeline on an issue.

        1. Classify with LLM (or heuristic fallback).
        2. Check for duplicates.
        3. Update the issue record with classification data.
        4. Optionally apply labels and post a response via the GitHub API.
        5. Record a TriageEvent.

        Args:
            db: Active database session.
            issue: The Issue ORM object to triage.
            installation_id: GitHub App installation id for API calls.

        Returns:
            A TriageResult with the full classification output.
        """
        start_ms = int(time.time() * 1000)

        # 1. Classify
        classification = await self._classify_issue(issue.title, issue.body or "")

        category_str = classification.get("category", "chore")
        priority_str = classification.get("priority", "P2")
        complexity = classification.get("complexity_score", 5)
        quality = classification.get("quality_score", 5)
        labels = classification.get("labels", [])
        response_draft = classification.get("response_draft")
        confidence = 0.85 if settings.ANTHROPIC_API_KEY or settings.OPENAI_API_KEY else 0.5

        # 2. Duplicate check
        duplicate_number = await self._check_duplicates(db, issue.repo_id, issue.title, issue.body or "")
        is_duplicate = duplicate_number is not None

        # 3. Update issue record
        try:
            issue.category = IssueCategory(category_str)
        except ValueError:
            issue.category = IssueCategory.chore
        try:
            issue.priority = IssuePriority(priority_str)
        except ValueError:
            issue.priority = IssuePriority.P2
        issue.complexity_score = max(1, min(10, complexity))
        issue.quality_score = max(1, min(10, quality))

        if is_duplicate:
            labels.append("possible-duplicate")

        db.add(issue)

        # 4. Apply labels via GitHub API (if installation context available)
        repo = await db.get(type(issue).repo.property.mapper.class_, issue.repo_id)
        if installation_id and repo and labels:
            try:
                await github_service.apply_labels(
                    installation_id, repo.owner, repo.name, issue.number, labels
                )
            except Exception:
                pass  # Non-fatal — label application is best-effort

        if installation_id and repo and response_draft and not is_duplicate:
            try:
                await github_service.post_comment(
                    installation_id, repo.owner, repo.name, issue.number, response_draft
                )
            except Exception:
                pass

        processing_time_ms = int(time.time() * 1000) - start_ms

        # 5. Record triage event
        event = TriageEvent(
            repo_id=issue.repo_id,
            issue_id=issue.id,
            event_type="auto_triage",
            labels_applied=labels,
            confidence=confidence,
            response_draft=response_draft,
            response_status=ResponseStatus.pending if response_draft else ResponseStatus.discarded,
            processing_time_ms=processing_time_ms,
        )
        db.add(event)
        await db.flush()

        return TriageResult(
            issue_id=issue.id,
            category=category_str,
            priority=priority_str,
            complexity_score=issue.complexity_score,
            quality_score=issue.quality_score,
            labels=labels,
            confidence=confidence,
            is_duplicate=is_duplicate,
            duplicate_of_number=duplicate_number,
            response_draft=response_draft,
            processing_time_ms=processing_time_ms,
        )


# Module-level singleton
triage_service = TriageService()
