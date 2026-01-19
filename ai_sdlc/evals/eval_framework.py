"""
Base Evaluation Framework

Provides base classes and interfaces for stage evaluations.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class IssueSeverity(Enum):
    """Severity levels for evaluation issues."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class EvalIssue:
    """Represents an issue found during evaluation."""

    severity: IssueSeverity
    category: str
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None
    is_blocking: bool = False

    def __str__(self) -> str:
        location_str = f" ({self.location})" if self.location else ""
        return f"[{self.severity.value.upper()}] {self.category}: {self.message}{location_str}"


@dataclass
class EvalResult:
    """
    Result from an evaluation.

    Contains pass/fail status, score, issues, and recommendations.
    """

    stage: str
    passed: bool
    score: float  # 0.0 to 1.0
    issues: List[EvalIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    blocking_issues: List[EvalIssue] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    evaluation_time_seconds: float = 0.0

    def __post_init__(self):
        """Post-initialization processing."""
        # Extract blocking issues
        self.blocking_issues = [issue for issue in self.issues if issue.is_blocking]

        # Ensure score is in valid range
        self.score = max(0.0, min(1.0, self.score))

    def get_issues_by_severity(self, severity: IssueSeverity) -> List[EvalIssue]:
        """Get all issues of a specific severity."""
        return [issue for issue in self.issues if issue.severity == severity]

    def has_critical_issues(self) -> bool:
        """Check if there are any critical issues."""
        return any(
            issue.severity == IssueSeverity.CRITICAL for issue in self.issues
        )

    def get_summary(self) -> str:
        """Get a human-readable summary of the evaluation."""
        status = "✅ PASSED" if self.passed else "❌ FAILED"
        summary = f"{status} - Score: {self.score:.2f}\n"

        if self.issues:
            summary += f"Issues: {len(self.issues)} "
            summary += f"(Critical: {len(self.get_issues_by_severity(IssueSeverity.CRITICAL))}, "
            summary += f"Error: {len(self.get_issues_by_severity(IssueSeverity.ERROR))}, "
            summary += f"Warning: {len(self.get_issues_by_severity(IssueSeverity.WARNING))})\n"

        if self.blocking_issues:
            summary += f"Blocking Issues: {len(self.blocking_issues)}\n"

        return summary


class BaseEval(ABC):
    """
    Base class for all evaluations.

    Subclasses must implement the evaluate() method to perform stage-specific evaluation.
    """

    def __init__(
        self,
        min_score: float = 0.7,
        config: Optional[Any] = None,
    ):
        """
        Initialize the evaluation.

        Args:
            min_score: Minimum score required to pass (0.0 to 1.0)
            config: Optional configuration object
        """
        self.min_score = min_score
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def evaluate(
        self,
        output_data: Dict[str, Any],
        evidence_paths: List[str],
    ) -> Dict[str, Any]:
        """
        Evaluate the output of a workflow stage.

        Args:
            output_data: Output data from the agent
            evidence_paths: Paths to evidence files

        Returns:
            Dictionary with evaluation results:
            {
                "passed": bool,
                "score": float (0.0 to 1.0),
                "issues": List[Dict],
                "recommendations": List[str],
                ...
            }
        """
        pass

    def _create_result(
        self,
        stage: str,
        score: float,
        issues: Optional[List[EvalIssue]] = None,
        recommendations: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EvalResult:
        """
        Create an EvalResult.

        Args:
            stage: The stage name
            score: The evaluation score (0.0 to 1.0)
            issues: List of issues found
            recommendations: List of recommendations
            metadata: Optional metadata

        Returns:
            EvalResult object
        """
        passed = score >= self.min_score

        return EvalResult(
            stage=stage,
            passed=passed,
            score=score,
            issues=issues or [],
            recommendations=recommendations or [],
            metadata=metadata or {},
        )

    def _check_file_exists(self, file_path: str) -> bool:
        """Check if a file exists."""
        from pathlib import Path

        return Path(file_path).exists()

    def _read_file(self, file_path: str) -> Optional[str]:
        """
        Read a file and return its contents.

        Args:
            file_path: Path to the file

        Returns:
            File contents or None if error
        """
        try:
            from pathlib import Path

            return Path(file_path).read_text()
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return None


class EvalRunner:
    """
    Runner for executing evaluations.

    Manages evaluation execution and result aggregation.
    """

    def __init__(self):
        """Initialize the eval runner."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.eval_registry: Dict[str, BaseEval] = {}

    def register_eval(self, name: str, eval_instance: BaseEval):
        """
        Register an evaluation.

        Args:
            name: Name of the evaluation
            eval_instance: Evaluation instance
        """
        self.eval_registry[name] = eval_instance
        self.logger.info(f"Registered evaluation: {name}")

    def run_eval(
        self,
        eval_name: str,
        output_data: Dict[str, Any],
        evidence_paths: List[str],
    ) -> EvalResult:
        """
        Run a specific evaluation.

        Args:
            eval_name: Name of the evaluation to run
            output_data: Output data from agent
            evidence_paths: Paths to evidence files

        Returns:
            EvalResult

        Raises:
            ValueError: If evaluation not registered
        """
        if eval_name not in self.eval_registry:
            raise ValueError(f"Evaluation {eval_name} not registered")

        eval_instance = self.eval_registry[eval_name]

        self.logger.info(f"Running evaluation: {eval_name}")

        try:
            import time

            start_time = time.time()

            # Run evaluation
            eval_dict = eval_instance.evaluate(output_data, evidence_paths)

            # Convert to EvalResult if not already
            if isinstance(eval_dict, EvalResult):
                result = eval_dict
            else:
                # Convert dict to EvalResult
                result = EvalResult(
                    stage=eval_dict.get("stage", eval_name),
                    passed=eval_dict.get("passed", False),
                    score=eval_dict.get("score", 0.0),
                    issues=[
                        EvalIssue(**issue) if isinstance(issue, dict) else issue
                        for issue in eval_dict.get("issues", [])
                    ],
                    recommendations=eval_dict.get("recommendations", []),
                    metadata=eval_dict.get("metadata", {}),
                )

            result.evaluation_time_seconds = time.time() - start_time

            self.logger.info(f"Evaluation {eval_name} completed: {result.get_summary()}")

            return result

        except Exception as e:
            self.logger.error(f"Evaluation {eval_name} failed with error: {e}")
            return EvalResult(
                stage=eval_name,
                passed=False,
                score=0.0,
                issues=[
                    EvalIssue(
                        severity=IssueSeverity.CRITICAL,
                        category="evaluation_error",
                        message=f"Evaluation failed: {e}",
                        is_blocking=True,
                    )
                ],
            )

    def run_multiple_evals(
        self,
        eval_names: List[str],
        output_data: Dict[str, Any],
        evidence_paths: List[str],
    ) -> List[EvalResult]:
        """
        Run multiple evaluations.

        Args:
            eval_names: List of evaluation names
            output_data: Output data from agent
            evidence_paths: Paths to evidence files

        Returns:
            List of EvalResults
        """
        results = []
        for eval_name in eval_names:
            result = self.run_eval(eval_name, output_data, evidence_paths)
            results.append(result)
        return results
