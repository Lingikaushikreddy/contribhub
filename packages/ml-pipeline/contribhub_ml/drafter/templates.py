"""
Predefined response templates for common GitHub issue patterns.

Each template contains placeholders (``{variable}``) that are filled at
draft time.  Three tone variants are provided: formal, friendly, and minimal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResponseTemplate:
    """A single response template with tone variants."""

    name: str
    description: str
    placeholders: list[str]
    variants: dict[str, str] = field(default_factory=dict)

    def render(self, tone: str = "friendly", **kwargs: str) -> str:
        """Render the template with the given tone and placeholder values.

        Parameters
        ----------
        tone : str
            One of ``formal``, ``friendly``, ``minimal``.
        **kwargs : str
            Values for each placeholder defined in ``self.placeholders``.

        Returns
        -------
        str
            The rendered template text.
        """
        variant = self.variants.get(tone, self.variants.get("friendly", ""))
        for key, value in kwargs.items():
            variant = variant.replace(f"{{{key}}}", value)
        return variant

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "placeholders": self.placeholders,
            "variants": self.variants,
        }


# ---------------------------------------------------------------------------
# Template definitions
# ---------------------------------------------------------------------------

MISSING_REPRO_STEPS = ResponseTemplate(
    name="missing_info",
    description="Request missing reproduction steps from the issue author.",
    placeholders=["author", "issue_title"],
    variants={
        "formal": (
            "Thank you for filing this issue, @{author}.\n\n"
            "To help us investigate **{issue_title}**, could you please provide:\n\n"
            "1. Steps to reproduce the issue\n"
            "2. Expected behaviour vs. actual behaviour\n"
            "3. Relevant error messages or stack traces\n\n"
            "This information will allow us to triage and resolve the matter promptly."
        ),
        "friendly": (
            "Hey @{author}, thanks for reporting this! :wave:\n\n"
            "We'd love to look into **{issue_title}** but we need a bit more info:\n\n"
            "- What steps lead to the problem?\n"
            "- What did you expect to happen?\n"
            "- Any error messages or logs?\n\n"
            "Drop those in and we'll jump right on it!"
        ),
        "minimal": (
            "@{author} — please add reproduction steps, expected vs. actual "
            "behaviour, and any error output so we can investigate **{issue_title}**."
        ),
    },
)

MISSING_ENVIRONMENT = ResponseTemplate(
    name="missing_environment",
    description="Request missing environment / system information.",
    placeholders=["author", "issue_title"],
    variants={
        "formal": (
            "Thank you for this report, @{author}.\n\n"
            "To diagnose **{issue_title}** we require additional environment details:\n\n"
            "- Operating system and version\n"
            "- Runtime / language version (e.g. Node 20, Python 3.12)\n"
            "- Package or library version\n"
            "- Any custom configuration that may be relevant\n\n"
            "We appreciate your cooperation."
        ),
        "friendly": (
            "Hi @{author}! Thanks for letting us know about **{issue_title}**.\n\n"
            "Could you share a few environment details?\n\n"
            "- OS & version\n"
            "- Language / runtime version\n"
            "- Package version\n"
            "- Any custom config?\n\n"
            "That'll help us track it down much faster!"
        ),
        "minimal": (
            "@{author} — we need your OS, runtime version, package version, "
            "and any relevant config to diagnose **{issue_title}**."
        ),
    },
)

DUPLICATE_ISSUE = ResponseTemplate(
    name="duplicate",
    description="Notify the author that their issue is a duplicate.",
    placeholders=["author", "original_issue_number", "original_issue_title"],
    variants={
        "formal": (
            "Thank you for your report, @{author}.\n\n"
            "This issue appears to be a duplicate of "
            "#{original_issue_number} (**{original_issue_title}**). "
            "We will continue tracking progress there.\n\n"
            "If you believe this is a distinct issue, please reopen with "
            "additional context explaining the difference."
        ),
        "friendly": (
            "Hey @{author}, thanks for bringing this up!\n\n"
            "Looks like this is already tracked in #{original_issue_number} "
            "(**{original_issue_title}**) — let's keep the conversation there "
            "so everything stays in one place.\n\n"
            "If you think it's actually different, feel free to reopen and "
            "let us know how!"
        ),
        "minimal": (
            "@{author} — duplicate of #{original_issue_number} "
            "({original_issue_title}). Closing; reopen if distinct."
        ),
    },
)

FEATURE_ACK = ResponseTemplate(
    name="feature_ack",
    description="Acknowledge a feature request.",
    placeholders=["author", "feature_summary"],
    variants={
        "formal": (
            "Thank you for the feature request, @{author}.\n\n"
            "We have noted your suggestion: **{feature_summary}**. "
            "The team will evaluate it against the current roadmap. "
            "We will update this issue once a decision has been reached.\n\n"
            "Additional use-case details or upvotes from the community "
            "will help us prioritise."
        ),
        "friendly": (
            "Great idea, @{author}! :bulb:\n\n"
            "We've logged your request for **{feature_summary}**. "
            "The team will take a look and factor it into upcoming planning.\n\n"
            "If others want this too, give the issue a thumbs-up — it "
            "really helps us prioritise!"
        ),
        "minimal": (
            "@{author} — noted! **{feature_summary}** is on our radar. "
            "Upvotes and use-case details help prioritise."
        ),
    },
)

QUESTION_REDIRECT = ResponseTemplate(
    name="question_redirect",
    description="Redirect a question to the appropriate resource.",
    placeholders=["author", "resource_name", "resource_url"],
    variants={
        "formal": (
            "Thank you for your question, @{author}.\n\n"
            "This issue tracker is reserved for bug reports and feature "
            "requests. For general questions, please refer to our "
            "**{resource_name}**: {resource_url}\n\n"
            "We are closing this issue but encourage you to seek help "
            "via the link above."
        ),
        "friendly": (
            "Hi @{author}! Thanks for reaching out.\n\n"
            "For questions like this, the best place is our "
            "**{resource_name}** — check it out here: {resource_url}\n\n"
            "The community there is super helpful! We'll close this for "
            "now, but feel free to open a new issue if you find a bug."
        ),
        "minimal": (
            "@{author} — questions go to {resource_name} ({resource_url}). "
            "Closing this issue."
        ),
    },
)

WELCOME_FIRST_TIME = ResponseTemplate(
    name="welcome_first_time",
    description="Welcome a first-time contributor.",
    placeholders=["author", "repo_name", "contributing_url"],
    variants={
        "formal": (
            "Welcome to **{repo_name}**, @{author}. Thank you for your "
            "first contribution.\n\n"
            "Please review our contributing guidelines at {contributing_url} "
            "to ensure a smooth process. A maintainer will review your "
            "submission shortly."
        ),
        "friendly": (
            "Welcome to **{repo_name}**, @{author}! :tada:\n\n"
            "We're thrilled to have your first contribution here. "
            "If you haven't already, check out our contributing guide: "
            "{contributing_url}\n\n"
            "A maintainer will review your PR soon — hang tight!"
        ),
        "minimal": (
            "Welcome @{author}! See {contributing_url} for guidelines. "
            "A reviewer will be with you shortly."
        ),
    },
)


# Master registry keyed by template name
TEMPLATES: dict[str, ResponseTemplate] = {
    "missing_info": MISSING_REPRO_STEPS,
    "missing_environment": MISSING_ENVIRONMENT,
    "duplicate": DUPLICATE_ISSUE,
    "feature_ack": FEATURE_ACK,
    "question_redirect": QUESTION_REDIRECT,
    "welcome_first_time": WELCOME_FIRST_TIME,
}
