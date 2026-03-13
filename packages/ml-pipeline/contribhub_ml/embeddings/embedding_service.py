"""
Embedding service wrapping OpenAI text-embedding-3-large with Redis caching.

Provides single and batch embedding, cosine similarity search, and a
transparent caching layer to avoid redundant API calls.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
from dataclasses import dataclass, field
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

_EMBEDDING_MODEL = "text-embedding-3-large"
_EMBEDDING_DIMENSIONS = 1024
_MAX_BATCH_SIZE = 2048
_CACHE_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 days


@dataclass
class SimilarityResult:
    """A single match returned by a similarity search."""

    index: int
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "score": round(self.score, 6),
            "metadata": self.metadata,
        }


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    va = np.asarray(a, dtype=np.float64)
    vb = np.asarray(b, dtype=np.float64)
    dot = float(np.dot(va, vb))
    norm_a = float(np.linalg.norm(va))
    norm_b = float(np.linalg.norm(vb))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _cache_key(text: str, model: str, dimensions: int) -> str:
    """Deterministic cache key from text content."""
    raw = f"{model}:{dimensions}:{text}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"contribhub:emb:{digest}"


class EmbeddingService:
    """High-level embedding service with caching and similarity search.

    Parameters
    ----------
    openai_api_key : str | None
        Explicit API key; falls back to ``OPENAI_API_KEY`` env var.
    redis_url : str | None
        Redis connection URL for the caching layer.  If ``None`` or if
        Redis is unreachable, caching is silently skipped.
    model : str
        OpenAI embedding model name.
    dimensions : int
        Desired embedding dimensionality.
    """

    def __init__(
        self,
        openai_api_key: str | None = None,
        redis_url: str | None = None,
        model: str = _EMBEDDING_MODEL,
        dimensions: int = _EMBEDDING_DIMENSIONS,
    ) -> None:
        self.model = model
        self.dimensions = dimensions
        self._api_key = openai_api_key or os.environ.get("OPENAI_API_KEY", "")
        self._client: Any = None
        self._redis: Any = None

        if redis_url:
            self._init_redis(redis_url)

    # ------------------------------------------------------------------
    # Lazy init helpers
    # ------------------------------------------------------------------

    def _init_redis(self, url: str) -> None:
        """Try to connect to Redis; swallow errors so the service degrades gracefully."""
        try:
            import redis as redis_lib

            self._redis = redis_lib.Redis.from_url(url, decode_responses=True)
            self._redis.ping()
            logger.info("Redis cache connected at %s", url)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Redis unavailable (%s); caching disabled.", exc)
            self._redis = None

    def _get_client(self) -> Any:
        if self._client is None:
            import openai

            if not self._api_key:
                raise EnvironmentError("OPENAI_API_KEY is not set")
            self._client = openai.OpenAI(api_key=self._api_key)
        return self._client

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    def _cache_get(self, key: str) -> list[float] | None:
        """Retrieve a cached embedding vector, or None."""
        if self._redis is None:
            return None
        try:
            raw = self._redis.get(key)
            if raw is not None:
                return json.loads(raw)
        except Exception:  # noqa: BLE001
            logger.debug("Redis read failed for key %s", key)
        return None

    def _cache_set(self, key: str, vector: list[float]) -> None:
        """Store an embedding vector in cache."""
        if self._redis is None:
            return
        try:
            self._redis.setex(key, _CACHE_TTL_SECONDS, json.dumps(vector))
        except Exception:  # noqa: BLE001
            logger.debug("Redis write failed for key %s", key)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed_text(self, text: str) -> list[float]:
        """Embed a single text string, using cache when available.

        Parameters
        ----------
        text : str
            The text to embed.

        Returns
        -------
        list[float]
            Embedding vector of length ``self.dimensions``.
        """
        key = _cache_key(text, self.model, self.dimensions)
        cached = self._cache_get(key)
        if cached is not None:
            return cached

        client = self._get_client()
        response = client.embeddings.create(
            input=[text],
            model=self.model,
            dimensions=self.dimensions,
        )
        vector = response.data[0].embedding
        self._cache_set(key, vector)
        return vector

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts, chunking to stay within API limits.

        Parameters
        ----------
        texts : list[str]
            Texts to embed.

        Returns
        -------
        list[list[float]]
            One embedding vector per input text, in the same order.
        """
        results: list[list[float]] = [[] for _ in texts]
        uncached_indices: list[int] = []
        uncached_texts: list[str] = []

        # Check cache first
        for i, text in enumerate(texts):
            key = _cache_key(text, self.model, self.dimensions)
            cached = self._cache_get(key)
            if cached is not None:
                results[i] = cached
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)

        if not uncached_texts:
            return results

        # Chunk and call API
        client = self._get_client()
        num_chunks = math.ceil(len(uncached_texts) / _MAX_BATCH_SIZE)
        all_vectors: list[list[float]] = []

        for chunk_idx in range(num_chunks):
            start = chunk_idx * _MAX_BATCH_SIZE
            end = start + _MAX_BATCH_SIZE
            chunk = uncached_texts[start:end]
            response = client.embeddings.create(
                input=chunk,
                model=self.model,
                dimensions=self.dimensions,
            )
            # Sort by index to maintain order (API may return out of order)
            sorted_data = sorted(response.data, key=lambda d: d.index)
            all_vectors.extend([d.embedding for d in sorted_data])

        # Populate results and cache
        for offset, orig_idx in enumerate(uncached_indices):
            vector = all_vectors[offset]
            results[orig_idx] = vector
            key = _cache_key(texts[orig_idx], self.model, self.dimensions)
            self._cache_set(key, vector)

        return results

    def find_similar(
        self,
        query_embedding: list[float],
        stored_embeddings: list[list[float]],
        threshold: float = 0.85,
        top_k: int | None = None,
        metadata: list[dict[str, Any]] | None = None,
    ) -> list[SimilarityResult]:
        """Find embeddings most similar to the query.

        Parameters
        ----------
        query_embedding : list[float]
            The query vector.
        stored_embeddings : list[list[float]]
            The corpus of vectors to search.
        threshold : float
            Minimum cosine similarity to include a result.
        top_k : int | None
            Maximum number of results to return (``None`` = no limit).
        metadata : list[dict] | None
            Optional per-embedding metadata to attach to results.

        Returns
        -------
        list[SimilarityResult]
            Results sorted by descending similarity score.
        """
        if not stored_embeddings:
            return []

        # Vectorised cosine similarity for speed
        query_vec = np.asarray(query_embedding, dtype=np.float64)
        corpus_matrix = np.asarray(stored_embeddings, dtype=np.float64)

        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0.0:
            return []

        corpus_norms = np.linalg.norm(corpus_matrix, axis=1)
        # Avoid division by zero
        safe_norms = np.where(corpus_norms == 0.0, 1.0, corpus_norms)
        similarities = corpus_matrix @ query_vec / (safe_norms * query_norm)

        results: list[SimilarityResult] = []
        for idx in range(len(similarities)):
            sim = float(similarities[idx])
            if sim >= threshold:
                meta = metadata[idx] if metadata else {}
                results.append(SimilarityResult(index=idx, score=sim, metadata=meta))

        results.sort(key=lambda r: r.score, reverse=True)

        if top_k is not None:
            results = results[:top_k]

        return results
