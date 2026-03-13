"""
Automated response drafting with tone control and RAG.

Uses Anthropic Claude for generation, with model routing between
claude-haiku-4-5-20251001 (templated) and claude-sonnet-4-6 (complex).
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Literal

from contribhub_ml.drafter.templates import TEMPLATES, ResponseTemplate

logger = logging.getLogger(__name__)


@dataclass
class DraftResult:
    """Result returned by the response drafter."""

    response_text: str
    template_type: str
    confidence: float
    model_used: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "response_text": self.response_text,
            "template_type": self.template_type,
            "confidence": round(self.confidence, 4),
            "model_used": self.model_used,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# Few-shot examples per tone
# ---------------------------------------------------------------------------

_FEW_SHOT_EXAMPLES: dict[str, list[dict[str, str]]] = {
    "formal": [
        {
            "role": "user",
            "content": (
                "Issue: App crashes on startup\n"
                "Category: bug\nTemplate: missing_info\n"
                "Write a formal response requesting more information."
            ),
        },
        {
            "role": "assistant",
            "content": (
                "Thank you for reporting this issue.\n\n"
                "To assist us in diagnosing the startup crash, could you "
                "please provide the following:\n\n"
                "1. Operating system and version\n"
                "2. Steps to reproduce the crash\n"
                "3. Full error log or stack trace\n\n"
                "We appreciate your assistance in resolving this matter."
            ),
        },
    ],
    "friendly": [
        {
            "role": "user",
            "content": (
                "Issue: App crashes on startup\n"
                "Category: bug\nTemplate: missing_info\n"
                "Write a friendly response requesting more information."
            ),
        },
        {
            "role": "assistant",
            "content": (
                "Hey there! Thanks for letting us know about the crash.\n\n"
                "Could you share a few details so we can dig in?\n\n"
                "- What OS are you on?\n"
                "- Steps to trigger the crash?\n"
                "- Any error messages or logs?\n\n"
                "That'll help us squash this fast!"
            ),
        },
    ],
    "minimal": [
        {
            "role": "user",
            "content": (
                "Issue: App crashes on startup\n"
                "Category: bug\nTemplate: missing_info\n"
                "Write a minimal response requesting more information."
            ),
        },
        {
            "role": "assistant",
            "content": (
                "Please share your OS, reproduction steps, and any error "
                "logs so we can investigate."
            ),
        },
    ],
}

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are a GitHub issue response assistant for an open-source project.

Guidelines:
- Be helpful, accurate, and respectful.
- If the template type is provided, follow its structure.
- Incorporate repository context (README, CONTRIBUTING.md excerpts) when relevant.
- Adapt tone as instructed: formal, friendly, or minimal.
- Do NOT fabricate links, version numbers, or facts not present in the context.
- Return ONLY the response text — no JSON wrapper, no markdown fences.
"""

# Template types that are simple enough for the faster model
_SIMPLE_TEMPLATES = frozenset([
    "missing_info",
    "missing_environment",
    "duplicate",
    "feature_ack",
    "question_redirect",
    "welcome_first_time",
])


@dataclass
class DrafterConfig:
    """Configuration for the response drafter."""

    tone: Literal["formal", "friendly", "minimal"] = "friendly"
    max_tokens: int = 512
    temperature: float = 0.4
    anthropic_api_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "tone": self.tone,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }


class ResponseDrafter:
    """Draft responses for GitHub issues using Anthropic Claude.

    Parameters
    ----------
    api_key : str | None
        Anthropic API key.  Falls back to ``ANTHROPIC_API_KEY`` env var.
    fast_model : str
        Model for simple templated responses.
    complex_model : str
        Model for complex, context-heavy responses.
    """

    def __init__(
        self,
        api_key: str | None = None,
        fast_model: str = "claude-haiku-4-5-20251001",
        complex_model: str = "claude-sonnet-4-6",
    ) -> None:
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.fast_model = fast_model
        self.complex_model = complex_model
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is None:
            import anthropic

            if not self._api_key:
                raise EnvironmentError("ANTHROPIC_API_KEY is not set")
            self._client = anthropic.Anthropic(api_key=self._api_key)
        return self._client

    def _select_model(self, template_type: str) -> str:
        """Route to the fast model for simple templates, complex otherwise."""
        if template_type in _SIMPLE_TEMPLATES:
            return self.fast_model
        return self.complex_model

    def _build_user_prompt(
        self,
        issue: dict[str, Any],
        template_type: str,
        repo_context: dict[str, str],
        tone: str,
    ) -> str:
        """Assemble the user prompt with issue details and repo context."""
        parts: list[str] = []

        # Issue details
        parts.append(f"Issue Title: {issue.get('title', 'N/A')}")
        parts.append(f"Issue Body:\n{issue.get('body', 'N/A')}")
        if issue.get("labels"):
            parts.append(f"Labels: {', '.join(issue['labels'])}")
        if issue.get("author"):
            parts.append(f"Author: @{issue['author']}")
        if issue.get("is_first_time"):
            parts.append("Note: This is the author's first contribution.")

        # Classification context
        parts.append(f"\nTemplate Type: {template_type}")
        parts.append(f"Tone: {tone}")

        # Repository context (RAG)
        if repo_context.get("readme"):
            parts.append(f"\n--- README excerpt ---\n{repo_context['readme'][:1500]}")
        if repo_context.get("contributing"):
            parts.append(
                f"\n--- CONTRIBUTING.md excerpt ---\n{repo_context['contributing'][:1500]}"
            )
        if repo_context.get("past_responses"):
            parts.append(
                f"\n--- Past response examples ---\n{repo_context['past_responses'][:1000]}"
            )

        # Template hint
        template = TEMPLATES.get(template_type)
        if template:
            parts.append(
                f"\nTemplate structure hint:\n"
                f"{template.variants.get(tone, template.variants.get('friendly', ''))}"
            )

        parts.append(
            "\nDraft a response following the template structure. "
            "Incorporate relevant repository context. Adapt the tone as specified."
        )

        return "\n".join(parts)

    def draft(
        self,
        issue: dict[str, Any],
        repo_context: dict[str, str] | None = None,
        config: DrafterConfig | None = None,
    ) -> DraftResult:
        """Draft a response for a GitHub issue.

        Parameters
        ----------
        issue : dict
            Must contain at least ``title`` and ``body``.  Optional keys:
            ``labels``, ``author``, ``is_first_time``, ``category``.
        repo_context : dict | None
            Optional RAG context with keys ``readme``, ``contributing``,
            ``past_responses``.
        config : DrafterConfig | None
            Tone and generation parameters.

        Returns
        -------
        DraftResult
        """
        if config is None:
            config = DrafterConfig()
        if repo_context is None:
            repo_context = {}

        template_type = self._infer_template_type(issue)
        model = self._select_model(template_type)

        # Try local template rendering first for simple cases
        local_result = self._try_local_template(issue, template_type, config.tone)
        if local_result is not None:
            return local_result

        # Fall back to LLM generation
        user_prompt = self._build_user_prompt(
            issue, template_type, repo_context, config.tone
        )

        few_shot = _FEW_SHOT_EXAMPLES.get(config.tone, _FEW_SHOT_EXAMPLES["friendly"])

        messages: list[dict[str, str]] = []
        messages.extend(few_shot)
        messages.append({"role": "user", "content": user_prompt})

        try:
            client = self._get_client()
            response = client.messages.create(
                model=model,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                system=_SYSTEM_PROMPT,
                messages=messages,
            )
            text_parts = [
                block.text for block in response.content if hasattr(block, "text")
            ]
            response_text = "".join(text_parts).strip()
            confidence = 0.90 if template_type in _SIMPLE_TEMPLATES else 0.75
        except Exception as exc:
            logger.error("Anthropic API call failed: %s", exc)
            # Fall back to raw template if API fails
            template = TEMPLATES.get(template_type)
            if template:
                response_text = template.render(
                    tone=config.tone,
                    author=issue.get("author", "contributor"),
                    issue_title=issue.get("title", "this issue"),
                    feature_summary=issue.get("title", "the requested feature"),
                    repo_name=repo_context.get("repo_name", "this project"),
                    contributing_url=repo_context.get("contributing_url", "CONTRIBUTING.md"),
                    resource_name=repo_context.get("resource_name", "documentation"),
                    resource_url=repo_context.get("resource_url", "#"),
                    original_issue_number=issue.get("duplicate_of", "N/A"),
                    original_issue_title=issue.get("duplicate_title", "N/A"),
                )
            else:
                response_text = (
                    f"Thank you for this issue. A maintainer will review it shortly."
                )
            confidence = 0.50
            model = "template_fallback"

        return DraftResult(
            response_text=response_text,
            template_type=template_type,
            confidence=confidence,
            model_used=model,
            metadata={"tone": config.tone, "issue_title": issue.get("title", "")},
        )

    def _infer_template_type(self, issue: dict[str, Any]) -> str:
        """Infer the best template type from issue metadata."""
        category = issue.get("category", "").lower()
        body = (issue.get("body") or "").lower()
        is_first_time = issue.get("is_first_time", False)

        if issue.get("duplicate_of"):
            return "duplicate"
        if is_first_time and issue.get("is_pr", False):
            return "welcome_first_time"
        if category == "question":
            return "question_redirect"
        if category == "feature":
            return "feature_ack"
        if category == "bug":
            # Check if reproduction info is missing
            has_repro = any(
                kw in body
                for kw in ["steps to reproduce", "reproduction", "how to reproduce",
                           "repro steps", "expected behavior", "expected behaviour"]
            )
            has_env = any(
                kw in body
                for kw in ["os:", "operating system", "version:", "environment",
                           "node version", "python version", "runtime"]
            )
            if not has_repro:
                return "missing_info"
            if not has_env:
                return "missing_environment"
            return "missing_info"
        return "missing_info"

    def _try_local_template(
        self,
        issue: dict[str, Any],
        template_type: str,
        tone: str,
    ) -> DraftResult | None:
        """Try to render a fully local template if all placeholders are available.

        Returns ``None`` if the template requires LLM generation.
        """
        template = TEMPLATES.get(template_type)
        if template is None:
            return None

        # Build kwargs from issue data
        kwargs: dict[str, str] = {
            "author": issue.get("author", "contributor"),
            "issue_title": issue.get("title", "this issue"),
            "feature_summary": issue.get("title", "the requested feature"),
            "repo_name": issue.get("repo_name", "this project"),
            "contributing_url": issue.get("contributing_url", ""),
            "resource_name": issue.get("resource_name", ""),
            "resource_url": issue.get("resource_url", ""),
            "original_issue_number": issue.get("duplicate_of", ""),
            "original_issue_title": issue.get("duplicate_title", ""),
        }

        # Only use local template if all required placeholders are filled
        missing = [
            p for p in template.placeholders
            if not kwargs.get(p)
        ]
        if missing:
            return None

        rendered = template.render(tone=tone, **kwargs)

        return DraftResult(
            response_text=rendered,
            template_type=template_type,
            confidence=0.95,
            model_used="local_template",
            metadata={"tone": tone, "issue_title": issue.get("title", "")},
        )
