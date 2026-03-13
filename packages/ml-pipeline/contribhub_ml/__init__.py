"""
contribhub_ml — AI-powered GitHub issue triage and contributor matching pipeline.

This package provides:
- Issue classification (SetFit + LLM fallback)
- Complexity scoring for repositories and issues
- Embedding services with caching and similarity search
- Duplicate issue detection via pgvector
- Automated response drafting with tone control
- Contributor skill profiling
- Repository health scoring
- Contributor-to-issue match scoring
- Model evaluation utilities
"""

__version__ = "0.1.0"

from contribhub_ml.classifier.issue_classifier import (
    ClassificationResult,
    IssueClassifier,
)
from contribhub_ml.classifier.complexity_scorer import (
    ComplexityResult,
    ComplexityScorer,
)
from contribhub_ml.embeddings.embedding_service import (
    EmbeddingService,
    SimilarityResult,
)
from contribhub_ml.embeddings.duplicate_detector import (
    DuplicateDetector,
    DuplicateResult,
)
from contribhub_ml.drafter.response_drafter import (
    DraftResult,
    ResponseDrafter,
)
from contribhub_ml.drafter.templates import TEMPLATES, ResponseTemplate
from contribhub_ml.scoring.skill_profiler import (
    SkillProfile,
    SkillProfiler,
)
from contribhub_ml.scoring.health_scorer import (
    HealthScore,
    HealthScorer,
)
from contribhub_ml.scoring.match_scorer import (
    MatchScore,
    MatchScorer,
)
from contribhub_ml.evaluation.evaluator import (
    EvalResult,
    ModelEvaluator,
)

__all__ = [
    # Classifier
    "IssueClassifier",
    "ClassificationResult",
    "ComplexityScorer",
    "ComplexityResult",
    # Embeddings
    "EmbeddingService",
    "SimilarityResult",
    "DuplicateDetector",
    "DuplicateResult",
    # Drafter
    "ResponseDrafter",
    "DraftResult",
    "ResponseTemplate",
    "TEMPLATES",
    # Scoring
    "SkillProfiler",
    "SkillProfile",
    "HealthScorer",
    "HealthScore",
    "MatchScorer",
    "MatchScore",
    # Evaluation
    "ModelEvaluator",
    "EvalResult",
]
