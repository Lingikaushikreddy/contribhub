"""Embedding services and duplicate detection."""

from contribhub_ml.embeddings.embedding_service import (
    EmbeddingService,
    SimilarityResult,
)
from contribhub_ml.embeddings.duplicate_detector import (
    DuplicateDetector,
    DuplicateResult,
)

__all__ = [
    "EmbeddingService",
    "SimilarityResult",
    "DuplicateDetector",
    "DuplicateResult",
]
