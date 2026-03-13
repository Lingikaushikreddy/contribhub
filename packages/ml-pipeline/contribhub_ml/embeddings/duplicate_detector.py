"""
Duplicate issue detection using pgvector and semantic similarity.

Embeds a new issue, queries pgvector for nearest neighbours within the
same repository, and classifies the match as duplicate, possibly-related,
or unique.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SimilarIssue:
    """A single similar-issue match."""

    issue_id: str
    title: str
    similarity_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "issue_id": self.issue_id,
            "title": self.title,
            "similarity_score": round(self.similarity_score, 4),
        }


@dataclass
class DuplicateResult:
    """Output of the duplicate detector."""

    is_duplicate: bool
    confidence: float
    similar_issues: list[SimilarIssue] = field(default_factory=list)
    explanation: str = ""
    status: str = "unique"  # "duplicate" | "possibly_related" | "unique"

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_duplicate": self.is_duplicate,
            "confidence": round(self.confidence, 4),
            "status": self.status,
            "similar_issues": [si.to_dict() for si in self.similar_issues],
            "explanation": self.explanation,
        }


_DUPLICATE_THRESHOLD = 0.95
_RELATED_THRESHOLD = 0.80


class DuplicateDetector:
    """Detect duplicate or related issues in a repository.

    Uses an ``EmbeddingService`` to embed the incoming issue and queries
    pgvector for nearest neighbours.

    Parameters
    ----------
    embedding_service : EmbeddingService
        An already-configured embedding service instance.
    pg_dsn : str | None
        PostgreSQL DSN for pgvector queries. Falls back to the
        ``DATABASE_URL`` environment variable.
    duplicate_threshold : float
        Cosine similarity above which an issue is declared duplicate.
    related_threshold : float
        Cosine similarity above which an issue is flagged as possibly related.
    top_k : int
        Number of nearest neighbours to retrieve from pgvector.
    """

    def __init__(
        self,
        embedding_service: Any,
        pg_dsn: str | None = None,
        duplicate_threshold: float = _DUPLICATE_THRESHOLD,
        related_threshold: float = _RELATED_THRESHOLD,
        top_k: int = 5,
    ) -> None:
        from contribhub_ml.embeddings.embedding_service import EmbeddingService

        self.embedding_service: EmbeddingService = embedding_service
        self.pg_dsn = pg_dsn or os.environ.get("DATABASE_URL", "")
        self.duplicate_threshold = duplicate_threshold
        self.related_threshold = related_threshold
        self.top_k = top_k
        self._conn: Any = None

    # ------------------------------------------------------------------
    # Database helpers
    # ------------------------------------------------------------------

    def _get_connection(self) -> Any:
        """Lazy-create a psycopg2 connection."""
        if self._conn is None:
            import psycopg2  # type: ignore[import-untyped]

            if not self.pg_dsn:
                raise EnvironmentError(
                    "DATABASE_URL is not set and no pg_dsn was provided."
                )
            self._conn = psycopg2.connect(self.pg_dsn)
        return self._conn

    def _query_pgvector(
        self, embedding: list[float], repo_id: str
    ) -> list[dict[str, Any]]:
        """Query pgvector for the top-k most similar issues.

        Expected table schema::

            CREATE TABLE issue_embeddings (
                id          TEXT PRIMARY KEY,
                repo_id     TEXT NOT NULL,
                title       TEXT NOT NULL,
                embedding   vector(1024)
            );

        Returns a list of dicts with keys: issue_id, title, similarity_score.
        """
        conn = self._get_connection()
        vec_literal = "[" + ",".join(str(v) for v in embedding) + "]"
        query = """
            SELECT id, title,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM issue_embeddings
            WHERE repo_id = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """
        with conn.cursor() as cur:
            cur.execute(query, (vec_literal, repo_id, vec_literal, self.top_k))
            rows = cur.fetchall()

        return [
            {"issue_id": row[0], "title": row[1], "similarity_score": float(row[2])}
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Explanation generation
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_explanation(
        new_title: str,
        similar: list[SimilarIssue],
        status: str,
    ) -> str:
        """Build a human-readable explanation of why issues are similar."""
        if not similar:
            return "No similar issues were found in this repository."

        top = similar[0]
        if status == "duplicate":
            return (
                f"The new issue \"{new_title}\" appears to be a duplicate of "
                f"#{top.issue_id} (\"{top.title}\") with a similarity score "
                f"of {top.similarity_score:.1%}. The titles and descriptions "
                f"share nearly identical semantic meaning."
            )
        if status == "possibly_related":
            related_list = ", ".join(
                f"#{si.issue_id} ({si.similarity_score:.0%})" for si in similar
            )
            return (
                f"The new issue \"{new_title}\" is semantically related to "
                f"existing issues: {related_list}. Consider checking these "
                f"before proceeding."
            )
        return "This issue does not closely match any existing issues."

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check(
        self,
        issue_title: str,
        issue_body: str,
        repo_id: str,
    ) -> DuplicateResult:
        """Check whether an issue is a duplicate or related to existing issues.

        Parameters
        ----------
        issue_title : str
            Title of the new issue.
        issue_body : str
            Body / description of the new issue.
        repo_id : str
            Repository identifier used to scope the pgvector search.

        Returns
        -------
        DuplicateResult
        """
        combined_text = f"{issue_title}\n\n{issue_body}"
        embedding = self.embedding_service.embed_text(combined_text)

        try:
            raw_matches = self._query_pgvector(embedding, repo_id)
        except Exception as exc:
            logger.error("pgvector query failed: %s", exc)
            return DuplicateResult(
                is_duplicate=False,
                confidence=0.0,
                status="unique",
                explanation=f"Could not query pgvector: {exc}",
            )

        similar_issues: list[SimilarIssue] = []
        for match in raw_matches:
            sim_score = match["similarity_score"]
            if sim_score >= self.related_threshold:
                similar_issues.append(
                    SimilarIssue(
                        issue_id=match["issue_id"],
                        title=match["title"],
                        similarity_score=sim_score,
                    )
                )

        # Determine status
        is_duplicate = False
        status = "unique"
        confidence = 0.0

        if similar_issues:
            top_score = similar_issues[0].similarity_score
            confidence = top_score

            if top_score >= self.duplicate_threshold:
                is_duplicate = True
                status = "duplicate"
            elif top_score >= self.related_threshold:
                status = "possibly_related"

        explanation = self._generate_explanation(issue_title, similar_issues, status)

        return DuplicateResult(
            is_duplicate=is_duplicate,
            confidence=confidence,
            similar_issues=similar_issues,
            explanation=explanation,
            status=status,
        )

    def check_against_list(
        self,
        issue_title: str,
        issue_body: str,
        existing_issues: list[dict[str, Any]],
    ) -> DuplicateResult:
        """Check duplicates against an in-memory list instead of pgvector.

        This is useful for testing or repos too small to warrant a database.

        Parameters
        ----------
        issue_title : str
            Title of the new issue.
        issue_body : str
            Body of the new issue.
        existing_issues : list[dict]
            Each dict must have ``issue_id``, ``title``, ``body``, and
            ``embedding`` (list[float]) keys.

        Returns
        -------
        DuplicateResult
        """
        combined_text = f"{issue_title}\n\n{issue_body}"
        query_embedding = self.embedding_service.embed_text(combined_text)

        from contribhub_ml.embeddings.embedding_service import _cosine_similarity

        similar_issues: list[SimilarIssue] = []
        for issue in existing_issues:
            sim = _cosine_similarity(query_embedding, issue["embedding"])
            if sim >= self.related_threshold:
                similar_issues.append(
                    SimilarIssue(
                        issue_id=issue["issue_id"],
                        title=issue["title"],
                        similarity_score=sim,
                    )
                )

        similar_issues.sort(key=lambda s: s.similarity_score, reverse=True)
        similar_issues = similar_issues[: self.top_k]

        is_duplicate = False
        status = "unique"
        confidence = 0.0

        if similar_issues:
            top_score = similar_issues[0].similarity_score
            confidence = top_score
            if top_score >= self.duplicate_threshold:
                is_duplicate = True
                status = "duplicate"
            elif top_score >= self.related_threshold:
                status = "possibly_related"

        explanation = self._generate_explanation(issue_title, similar_issues, status)

        return DuplicateResult(
            is_duplicate=is_duplicate,
            confidence=confidence,
            similar_issues=similar_issues,
            explanation=explanation,
            status=status,
        )
