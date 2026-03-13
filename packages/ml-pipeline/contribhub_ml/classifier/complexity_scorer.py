"""
Complexity scoring for repository files and issues.

Uses AST-based cyclomatic complexity for Python, regex patterns for JS/TS,
plus cognitive measures like nesting depth, file count, and coupling.
"""

from __future__ import annotations

import ast
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ComplexityResult:
    """Output of the complexity scorer."""

    score: float
    level: str
    factors: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dictionary."""
        return {
            "score": round(self.score, 2),
            "level": self.level,
            "factors": self.factors,
        }


# ---------------------------------------------------------------------------
# Language-specific helpers
# ---------------------------------------------------------------------------

_JS_BRANCH_PATTERN = re.compile(
    r"\b(if|else\s+if|for|while|do|switch|case|catch|&&|\|\||\?)\b"
)
_JS_NESTING_OPEN = re.compile(r"[\{]")
_JS_NESTING_CLOSE = re.compile(r"[\}]")

_PYTHON_EXTENSIONS = frozenset([".py", ".pyi"])
_JS_TS_EXTENSIONS = frozenset([".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"])
_SUPPORTED_EXTENSIONS = _PYTHON_EXTENSIONS | _JS_TS_EXTENSIONS


def _cyclomatic_python(source: str) -> int:
    """Compute cyclomatic complexity of a Python source string.

    Counts decision points in the AST: if, for, while, except, with,
    assert, boolean ops (and/or), and comprehensions.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        logger.debug("SyntaxError while parsing Python source for complexity.")
        return 1  # unparseable defaults to minimal complexity

    complexity = 1  # base path
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.IfExp)):
            complexity += 1
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            complexity += 1
        elif isinstance(node, (ast.While,)):
            complexity += 1
        elif isinstance(node, ast.ExceptHandler):
            complexity += 1
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            complexity += 1
        elif isinstance(node, ast.Assert):
            complexity += 1
        elif isinstance(node, ast.BoolOp):
            # each `and`/`or` adds a branch per extra operand
            complexity += len(node.values) - 1
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
            complexity += sum(1 for _ in node.generators)
    return complexity


def _cyclomatic_js(source: str) -> int:
    """Estimate cyclomatic complexity of JS/TS source via regex counting."""
    return 1 + len(_JS_BRANCH_PATTERN.findall(source))


def _max_nesting_depth(source: str) -> int:
    """Return the maximum brace/indent nesting depth in a source string."""
    max_depth = 0
    current = 0
    for char in source:
        if char == "{":
            current += 1
            max_depth = max(max_depth, current)
        elif char == "}":
            current = max(current - 1, 0)
    return max_depth


def _max_indent_depth_python(source: str) -> int:
    """Return the maximum indentation depth (in 4-space units) for Python."""
    max_depth = 0
    for line in source.splitlines():
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        spaces = len(line) - len(stripped)
        depth = spaces // 4
        max_depth = max(max_depth, depth)
    return max_depth


def _count_imports_python(source: str) -> int:
    """Count import statements in Python source."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            count += 1
    return count


def _count_imports_js(source: str) -> int:
    """Count import/require statements in JS/TS source."""
    import_pattern = re.compile(r"(?:^|\n)\s*import\s+", re.MULTILINE)
    require_pattern = re.compile(r"\brequire\s*\(")
    return len(import_pattern.findall(source)) + len(require_pattern.findall(source))


class ComplexityScorer:
    """Score the complexity of code touched by a GitHub issue.

    Parameters
    ----------
    max_file_size : int
        Skip files larger than this many bytes (default 512 KB).
    """

    _LEVEL_MAP: list[tuple[float, str]] = [
        (2.0, "beginner"),
        (5.0, "intermediate"),
        (8.0, "advanced"),
    ]

    def __init__(self, max_file_size: int = 512_000) -> None:
        self.max_file_size = max_file_size

    @staticmethod
    def _score_to_level(score: float) -> str:
        """Map a numeric 1-10 score to a human-readable level."""
        if score <= 2.0:
            return "beginner"
        if score <= 5.0:
            return "intermediate"
        if score <= 8.0:
            return "advanced"
        return "expert"

    def score(
        self, repo_path: str, affected_files: list[str] | None = None
    ) -> ComplexityResult:
        """Score the complexity of a repository or a subset of its files.

        Parameters
        ----------
        repo_path : str
            Absolute path to the repository root.
        affected_files : list[str] | None
            Relative paths of files to analyse. If ``None``, all supported
            files in the repo are analysed.

        Returns
        -------
        ComplexityResult
        """
        root = Path(repo_path)

        if affected_files is not None:
            paths = [root / f for f in affected_files if self._is_supported(f)]
        else:
            paths = [
                p
                for p in root.rglob("*")
                if p.is_file()
                and self._is_supported(p.name)
                and "node_modules" not in p.parts
                and ".git" not in p.parts
                and "__pycache__" not in p.parts
            ]

        if not paths:
            return ComplexityResult(score=1.0, level="beginner", factors={
                "file_count": 0,
                "note": "No supported source files found.",
            })

        total_cyclomatic = 0
        total_nesting = 0
        total_imports = 0
        total_loc = 0
        file_count = len(paths)
        files_read = 0

        for p in paths:
            if not p.is_file():
                continue
            if p.stat().st_size > self.max_file_size:
                continue
            try:
                source = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            files_read += 1
            ext = p.suffix.lower()
            loc = len([l for l in source.splitlines() if l.strip()])
            total_loc += loc

            if ext in _PYTHON_EXTENSIONS:
                total_cyclomatic += _cyclomatic_python(source)
                total_nesting += _max_indent_depth_python(source)
                total_imports += _count_imports_python(source)
            elif ext in _JS_TS_EXTENSIONS:
                total_cyclomatic += _cyclomatic_js(source)
                total_nesting += _max_nesting_depth(source)
                total_imports += _count_imports_js(source)

        if files_read == 0:
            return ComplexityResult(score=1.0, level="beginner", factors={
                "file_count": file_count,
                "files_read": 0,
                "note": "Could not read any files.",
            })

        # Normalise per-file averages and map to 1-10 scale
        avg_cyclomatic = total_cyclomatic / files_read
        avg_nesting = total_nesting / files_read
        avg_imports = total_imports / files_read

        # Cognitive score: incorporates nesting + file spread + LOC density
        cognitive_raw = (
            min(avg_nesting / 6.0, 1.0) * 4.0
            + min(file_count / 20.0, 1.0) * 3.0
            + min(total_loc / 5000.0, 1.0) * 3.0
        )
        cognitive = min(cognitive_raw, 10.0)

        # Cyclomatic normalised to 1-10
        cyclomatic_norm = min(avg_cyclomatic / 15.0 * 10.0, 10.0)

        # Coupling: import density as a proxy
        coupling_raw = min(avg_imports / 12.0 * 10.0, 10.0)

        # Composite formula
        composite = (
            0.60 * cognitive
            + 0.25 * cyclomatic_norm
            + 0.15 * coupling_raw
        )
        # Clamp to 1-10
        composite = max(1.0, min(10.0, composite))

        level = self._score_to_level(composite)

        factors = {
            "file_count": file_count,
            "files_analysed": files_read,
            "total_loc": total_loc,
            "avg_cyclomatic_complexity": round(avg_cyclomatic, 2),
            "avg_nesting_depth": round(avg_nesting, 2),
            "avg_import_count": round(avg_imports, 2),
            "cognitive_score": round(cognitive, 2),
            "cyclomatic_normalised": round(cyclomatic_norm, 2),
            "coupling_score": round(coupling_raw, 2),
        }

        return ComplexityResult(score=round(composite, 2), level=level, factors=factors)

    @staticmethod
    def _is_supported(filename: str) -> bool:
        """Check whether a filename has a supported extension."""
        return Path(filename).suffix.lower() in _SUPPORTED_EXTENSIONS
