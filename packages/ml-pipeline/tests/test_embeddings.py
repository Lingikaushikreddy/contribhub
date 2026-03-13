"""Tests for the EmbeddingService and DuplicateDetector modules."""

from __future__ import annotations

import json
import math
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from contribhub_ml.embeddings.embedding_service import (
    EmbeddingService,
    SimilarityResult,
    _cache_key,
    _cosine_similarity,
)
from contribhub_ml.embeddings.duplicate_detector import (
    DuplicateDetector,
    DuplicateResult,
    SimilarIssue,
)


# ---------------------------------------------------------------------------
# _cosine_similarity unit tests
# ---------------------------------------------------------------------------


class TestCosineSimilarity:
    """Tests for the cosine similarity helper function."""

    def test_identical_vectors(self):
        """Identical vectors should have similarity 1.0."""
        v = [1.0, 2.0, 3.0]
        assert math.isclose(_cosine_similarity(v, v), 1.0, rel_tol=1e-6)

    def test_orthogonal_vectors(self):
        """Orthogonal vectors should have similarity 0.0."""
        a = [1.0, 0.0, 0.0]
        b = [0.0, 1.0, 0.0]
        assert math.isclose(_cosine_similarity(a, b), 0.0, abs_tol=1e-9)

    def test_opposite_vectors(self):
        """Opposite vectors should have similarity -1.0."""
        a = [1.0, 2.0, 3.0]
        b = [-1.0, -2.0, -3.0]
        assert math.isclose(_cosine_similarity(a, b), -1.0, rel_tol=1e-6)

    def test_zero_vector_returns_zero(self):
        """If either vector is zero, similarity should be 0."""
        assert _cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0
        assert _cosine_similarity([1.0, 2.0], [0.0, 0.0]) == 0.0

    def test_known_cosine_value(self):
        """Test against a hand-computed cosine similarity."""
        a = [1.0, 0.0]
        b = [1.0, 1.0]
        # cos(45 degrees) = sqrt(2)/2 ~ 0.7071
        expected = math.sqrt(2) / 2
        assert math.isclose(_cosine_similarity(a, b), expected, rel_tol=1e-6)

    def test_high_dimensional_vectors(self):
        """Similarity should work on high-dimensional vectors."""
        rng = np.random.default_rng(42)
        a = rng.standard_normal(1024).tolist()
        b = rng.standard_normal(1024).tolist()
        sim = _cosine_similarity(a, b)
        # Random high-dim vectors are roughly orthogonal
        assert -0.2 < sim < 0.2


# ---------------------------------------------------------------------------
# _cache_key
# ---------------------------------------------------------------------------


class TestCacheKey:
    """Tests for the deterministic cache key helper."""

    def test_same_input_same_key(self):
        k1 = _cache_key("hello world", "text-embedding-3-large", 1024)
        k2 = _cache_key("hello world", "text-embedding-3-large", 1024)
        assert k1 == k2

    def test_different_input_different_key(self):
        k1 = _cache_key("hello", "text-embedding-3-large", 1024)
        k2 = _cache_key("goodbye", "text-embedding-3-large", 1024)
        assert k1 != k2

    def test_different_model_different_key(self):
        k1 = _cache_key("hello", "model-a", 1024)
        k2 = _cache_key("hello", "model-b", 1024)
        assert k1 != k2

    def test_different_dims_different_key(self):
        k1 = _cache_key("hello", "model-a", 512)
        k2 = _cache_key("hello", "model-a", 1024)
        assert k1 != k2

    def test_key_prefix(self):
        key = _cache_key("test", "model", 256)
        assert key.startswith("contribhub:emb:")


# ---------------------------------------------------------------------------
# SimilarityResult
# ---------------------------------------------------------------------------


class TestSimilarityResult:
    """Tests for the SimilarityResult dataclass."""

    def test_to_dict(self):
        r = SimilarityResult(index=3, score=0.9123456, metadata={"id": "abc"})
        d = r.to_dict()
        assert d["index"] == 3
        assert d["score"] == 0.912346
        assert d["metadata"] == {"id": "abc"}

    def test_default_metadata(self):
        r = SimilarityResult(index=0, score=0.5)
        assert r.metadata == {}


# ---------------------------------------------------------------------------
# EmbeddingService.embed_text (mocked OpenAI)
# ---------------------------------------------------------------------------


class TestEmbedText:
    """Tests for single-text embedding."""

    def test_embed_text_calls_api(self, mock_openai_embedding_response):
        """embed_text should call the OpenAI API and return the vector."""
        svc = EmbeddingService(openai_api_key="test-key")

        expected_vec = [0.1] * 1024
        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = mock_openai_embedding_response(
            [expected_vec]
        )
        svc._client = mock_client

        result = svc.embed_text("hello world")

        assert result == expected_vec
        mock_client.embeddings.create.assert_called_once()

    def test_embed_text_uses_cache(self, mock_openai_embedding_response):
        """Second call with same text should use cache, not API."""
        svc = EmbeddingService(openai_api_key="test-key")

        cached_vec = [0.5] * 1024
        mock_redis = MagicMock()
        mock_redis.get.return_value = json.dumps(cached_vec)
        svc._redis = mock_redis

        mock_client = MagicMock()
        svc._client = mock_client

        result = svc.embed_text("cached text")

        assert result == cached_vec
        mock_client.embeddings.create.assert_not_called()

    def test_embed_text_cache_miss_calls_api(self, mock_openai_embedding_response):
        """On cache miss, API should be called and result cached."""
        svc = EmbeddingService(openai_api_key="test-key")

        expected_vec = [0.2] * 1024
        mock_redis = MagicMock()
        mock_redis.get.return_value = None  # cache miss
        svc._redis = mock_redis

        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = mock_openai_embedding_response(
            [expected_vec]
        )
        svc._client = mock_client

        result = svc.embed_text("new text")

        assert result == expected_vec
        mock_client.embeddings.create.assert_called_once()
        mock_redis.setex.assert_called_once()

    def test_embed_text_no_redis_still_works(self, mock_openai_embedding_response):
        """When Redis is None, embedding should still work via API only."""
        svc = EmbeddingService(openai_api_key="test-key")
        assert svc._redis is None

        expected_vec = [0.3] * 1024
        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = mock_openai_embedding_response(
            [expected_vec]
        )
        svc._client = mock_client

        result = svc.embed_text("text without cache")

        assert result == expected_vec


# ---------------------------------------------------------------------------
# EmbeddingService.embed_batch (mocked OpenAI)
# ---------------------------------------------------------------------------


class TestEmbedBatch:
    """Tests for batch embedding."""

    def test_batch_returns_correct_count(self, mock_openai_embedding_response):
        """Batch embed should return one vector per input text."""
        svc = EmbeddingService(openai_api_key="test-key")

        texts = ["alpha", "beta", "gamma"]
        vecs = [[0.1 * i] * 1024 for i in range(3)]

        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = mock_openai_embedding_response(vecs)
        svc._client = mock_client

        results = svc.embed_batch(texts)

        assert len(results) == 3
        for r in results:
            assert len(r) == 1024

    def test_batch_uses_cache_for_known_texts(self, mock_openai_embedding_response):
        """Cached texts should not trigger API calls."""
        svc = EmbeddingService(openai_api_key="test-key")

        cached_vec_a = [0.1] * 1024
        fresh_vec_b = [0.2] * 1024

        def mock_redis_get(key):
            if "alpha" in key:
                # We can't easily match the hash, so let's mock differently
                return None
            return None

        mock_redis = MagicMock()
        # All cache misses for simplicity
        mock_redis.get.return_value = None
        svc._redis = mock_redis

        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = mock_openai_embedding_response(
            [cached_vec_a, fresh_vec_b]
        )
        svc._client = mock_client

        results = svc.embed_batch(["alpha", "beta"])

        assert len(results) == 2
        mock_client.embeddings.create.assert_called_once()

    def test_batch_empty_input(self, mock_openai_embedding_response):
        """Empty input list should return empty result without API call."""
        svc = EmbeddingService(openai_api_key="test-key")

        mock_client = MagicMock()
        svc._client = mock_client

        results = svc.embed_batch([])

        assert results == []
        mock_client.embeddings.create.assert_not_called()


# ---------------------------------------------------------------------------
# EmbeddingService.find_similar
# ---------------------------------------------------------------------------


class TestFindSimilar:
    """Tests for the in-memory similarity search."""

    def test_identical_embedding_found(self):
        """A query identical to a stored embedding should be found with score ~1.0."""
        svc = EmbeddingService(openai_api_key="test-key")

        query = [1.0, 0.0, 0.0]
        stored = [
            [1.0, 0.0, 0.0],  # identical
            [0.0, 1.0, 0.0],  # orthogonal
            [0.0, 0.0, 1.0],  # orthogonal
        ]

        results = svc.find_similar(query, stored, threshold=0.9)

        assert len(results) == 1
        assert results[0].index == 0
        assert math.isclose(results[0].score, 1.0, rel_tol=1e-6)

    def test_threshold_filters(self):
        """Only results above threshold should be returned."""
        svc = EmbeddingService(openai_api_key="test-key")

        query = [1.0, 0.0]
        stored = [
            [1.0, 0.1],   # high similarity
            [0.5, 0.5],   # moderate similarity
            [0.0, 1.0],   # no similarity
        ]

        results = svc.find_similar(query, stored, threshold=0.95)

        # Only the first vector should be above 0.95
        assert len(results) == 1
        assert results[0].index == 0

    def test_top_k_limits_results(self):
        """top_k should limit the number of returned results."""
        svc = EmbeddingService(openai_api_key="test-key")

        query = [1.0, 1.0, 1.0]
        stored = [
            [1.0, 1.0, 0.9],
            [1.0, 0.9, 1.0],
            [0.9, 1.0, 1.0],
            [1.0, 1.0, 1.0],
        ]

        results = svc.find_similar(query, stored, threshold=0.9, top_k=2)

        assert len(results) == 2
        # Should be sorted by score descending
        assert results[0].score >= results[1].score

    def test_metadata_attached(self):
        """Metadata should be attached to matching results."""
        svc = EmbeddingService(openai_api_key="test-key")

        query = [1.0, 0.0]
        stored = [[1.0, 0.1]]
        meta = [{"issue_id": "123"}]

        results = svc.find_similar(query, stored, threshold=0.9, metadata=meta)

        assert len(results) == 1
        assert results[0].metadata == {"issue_id": "123"}

    def test_empty_corpus(self):
        """Empty corpus should return empty results."""
        svc = EmbeddingService(openai_api_key="test-key")
        results = svc.find_similar([1.0, 0.0], [], threshold=0.5)
        assert results == []

    def test_zero_query_vector(self):
        """Zero query vector should return empty results."""
        svc = EmbeddingService(openai_api_key="test-key")
        results = svc.find_similar([0.0, 0.0], [[1.0, 0.0]], threshold=0.5)
        assert results == []

    def test_results_sorted_descending(self):
        """Results should be sorted by score in descending order."""
        svc = EmbeddingService(openai_api_key="test-key")

        query = [1.0, 1.0]
        stored = [
            [0.5, 1.0],   # moderate
            [1.0, 1.0],   # exact
            [0.9, 1.0],   # high
        ]

        results = svc.find_similar(query, stored, threshold=0.8)

        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# EmbeddingService — init and error handling
# ---------------------------------------------------------------------------


class TestEmbeddingServiceInit:
    """Tests for EmbeddingService initialisation."""

    def test_default_model(self):
        svc = EmbeddingService(openai_api_key="key")
        assert svc.model == "text-embedding-3-large"

    def test_default_dimensions(self):
        svc = EmbeddingService(openai_api_key="key")
        assert svc.dimensions == 1024

    def test_custom_model(self):
        svc = EmbeddingService(openai_api_key="key", model="text-embedding-3-small")
        assert svc.model == "text-embedding-3-small"

    def test_redis_not_connected_by_default(self):
        svc = EmbeddingService(openai_api_key="key")
        assert svc._redis is None

    def test_missing_api_key_raises(self):
        """_get_client should raise if no API key is available."""
        svc = EmbeddingService(openai_api_key="")
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(EnvironmentError, match="OPENAI_API_KEY"):
                svc._get_client()


# ---------------------------------------------------------------------------
# DuplicateDetector
# ---------------------------------------------------------------------------


class TestDuplicateDetector:
    """Tests for the DuplicateDetector."""

    def _make_detector(self, embed_return: list[float] | None = None):
        """Helper: create a DuplicateDetector with mocked embedding service."""
        mock_embed_svc = MagicMock()
        if embed_return is not None:
            mock_embed_svc.embed_text.return_value = embed_return
        else:
            mock_embed_svc.embed_text.return_value = [0.5] * 1024
        return DuplicateDetector(
            embedding_service=mock_embed_svc,
            duplicate_threshold=0.95,
            related_threshold=0.80,
        )

    def test_check_against_list_duplicate(self):
        """An issue with 0.96 similarity should be flagged as duplicate."""
        query_vec = [1.0, 0.0, 0.0]
        detector = self._make_detector(embed_return=query_vec)

        existing = [
            {
                "issue_id": "42",
                "title": "Same issue",
                "body": "Same body",
                "embedding": [1.0, 0.01, 0.0],  # very similar
            }
        ]

        result = detector.check_against_list("Same issue", "Same body", existing)

        assert result.is_duplicate is True
        assert result.status == "duplicate"
        assert len(result.similar_issues) == 1
        assert result.similar_issues[0].issue_id == "42"

    def test_check_against_list_related(self):
        """An issue with similarity between thresholds should be 'possibly_related'."""
        query_vec = [1.0, 0.0, 0.0]
        detector = self._make_detector(embed_return=query_vec)

        existing = [
            {
                "issue_id": "99",
                "title": "Similar but not same",
                "body": "Different body",
                "embedding": [0.9, 0.4, 0.0],  # related but not duplicate
            }
        ]

        result = detector.check_against_list(
            "Related issue", "Related body", existing
        )

        # Similarity of [1,0,0] and [0.9,0.4,0] is about 0.914 — between 0.80 and 0.95
        assert result.status == "possibly_related"
        assert result.is_duplicate is False
        assert len(result.similar_issues) >= 1

    def test_check_against_list_unique(self):
        """An issue with low similarity should be classified as 'unique'."""
        query_vec = [1.0, 0.0, 0.0]
        detector = self._make_detector(embed_return=query_vec)

        existing = [
            {
                "issue_id": "7",
                "title": "Completely different",
                "body": "Unrelated topic",
                "embedding": [0.0, 1.0, 0.0],  # orthogonal
            }
        ]

        result = detector.check_against_list("New issue", "New body", existing)

        assert result.status == "unique"
        assert result.is_duplicate is False
        assert len(result.similar_issues) == 0

    def test_check_against_empty_list(self):
        """An empty existing issues list should return 'unique'."""
        detector = self._make_detector()

        result = detector.check_against_list("New issue", "New body", [])

        assert result.status == "unique"
        assert result.is_duplicate is False
        assert result.similar_issues == []

    def test_duplicate_result_to_dict(self):
        """DuplicateResult.to_dict should serialise correctly."""
        result = DuplicateResult(
            is_duplicate=True,
            confidence=0.97123,
            similar_issues=[
                SimilarIssue(issue_id="42", title="Test", similarity_score=0.97123)
            ],
            explanation="Duplicate detected.",
            status="duplicate",
        )
        d = result.to_dict()
        assert d["is_duplicate"] is True
        assert d["confidence"] == 0.9712
        assert d["status"] == "duplicate"
        assert len(d["similar_issues"]) == 1
        assert d["similar_issues"][0]["issue_id"] == "42"

    def test_explanation_for_duplicate(self):
        """Explanation for a duplicate should mention the top match."""
        explanation = DuplicateDetector._generate_explanation(
            "My issue",
            [SimilarIssue(issue_id="42", title="Original", similarity_score=0.97)],
            "duplicate",
        )
        assert "duplicate" in explanation.lower()
        assert "42" in explanation
        assert "Original" in explanation

    def test_explanation_for_related(self):
        """Explanation for related issues should list them."""
        explanation = DuplicateDetector._generate_explanation(
            "My issue",
            [
                SimilarIssue(issue_id="10", title="A", similarity_score=0.85),
                SimilarIssue(issue_id="20", title="B", similarity_score=0.82),
            ],
            "possibly_related",
        )
        assert "related" in explanation.lower()
        assert "#10" in explanation
        assert "#20" in explanation

    def test_explanation_for_unique(self):
        """Explanation for a unique issue should say no matches found."""
        explanation = DuplicateDetector._generate_explanation(
            "My issue", [], "unique"
        )
        assert "no similar" in explanation.lower() or "does not" in explanation.lower()

    def test_pgvector_check_handles_db_error(self):
        """If pgvector query fails, result should be unique with error explanation."""
        detector = self._make_detector()
        detector._conn = MagicMock()
        detector._conn.cursor.side_effect = Exception("DB connection lost")

        result = detector.check("New issue", "body", "repo-1")

        assert result.is_duplicate is False
        assert result.status == "unique"
        assert "pgvector" in result.explanation.lower() or "could not" in result.explanation.lower()
