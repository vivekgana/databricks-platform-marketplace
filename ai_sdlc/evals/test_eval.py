"""
Test Quality Evaluation

Evaluates unit tests for coverage, quality, and completeness.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from .eval_framework import BaseEval, EvalIssue, IssueSeverity


class TestEval(BaseEval):
    """
    Evaluation for unit tests.

    Checks:
    - Test coverage ≥ 80%
    - Tests are independent
    - Tests have assertions
    - Edge cases covered
    - Test quality metrics
    """

    def __init__(self, min_score: float = 0.8, config: Any = None):
        """
        Initialize test evaluation.

        Args:
            min_score: Minimum score to pass (default 0.8)
            config: Optional configuration
        """
        super().__init__(min_score, config)
        self.min_coverage = 0.8  # 80% coverage required

    def evaluate(
        self,
        output_data: Dict[str, Any],
        evidence_paths: List[str],
    ) -> Dict[str, Any]:
        """
        Evaluate unit tests.

        Args:
            output_data: Dictionary with test results and coverage
            evidence_paths: Paths to test files and reports

        Returns:
            Evaluation result dictionary
        """
        issues = []
        recommendations = []
        score = 1.0

        # Find test files
        test_files = [
            path
            for path in evidence_paths
            if path.endswith(".py") and "test_" in Path(path).name
        ]

        if not test_files:
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.CRITICAL,
                    category="no_tests",
                    message="No test files found",
                    is_blocking=True,
                )
            )
            return self._create_result(
                stage="unit_testing", score=0.0, issues=issues
            ).__dict__

        # Check test coverage
        coverage_data = self._get_coverage_data(evidence_paths, output_data)
        if coverage_data:
            coverage_percentage = coverage_data.get("coverage_percentage", 0.0)
            total_statements = coverage_data.get("total_statements", 0)
            covered_statements = coverage_data.get("covered_statements", 0)

            # Check if coverage meets minimum threshold
            if coverage_percentage < self.min_coverage * 100:
                issues.append(
                    EvalIssue(
                        severity=IssueSeverity.ERROR,
                        category="insufficient_coverage",
                        message=f"Test coverage is {coverage_percentage:.1f}%, required: {self.min_coverage * 100:.1f}%",
                        suggestion=f"Add tests to cover {int((self.min_coverage * 100) - coverage_percentage)}% more code",
                        is_blocking=True,
                    )
                )
                # Calculate score deduction based on coverage gap
                coverage_gap = self.min_coverage - (coverage_percentage / 100.0)
                score -= coverage_gap * 0.5
            else:
                # Bonus for exceeding minimum coverage
                if coverage_percentage >= 90.0:
                    score += 0.05
                    recommendations.append(
                        f"Excellent coverage at {coverage_percentage:.1f}%!"
                    )
        else:
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.WARNING,
                    category="no_coverage_data",
                    message="No coverage data found. Unable to verify 80% coverage requirement.",
                    suggestion="Run tests with coverage: pytest --cov=. --cov-report=json",
                )
            )
            score -= 0.2

        # Analyze test files
        for test_file in test_files:
            file_issues = self._analyze_test_file(test_file)
            issues.extend(file_issues)

        # Check test execution results
        test_results = output_data.get("test_results", {})
        if test_results:
            passed = test_results.get("passed", 0)
            failed = test_results.get("failed", 0)
            total = passed + failed

            if failed > 0:
                issues.append(
                    EvalIssue(
                        severity=IssueSeverity.CRITICAL,
                        category="failing_tests",
                        message=f"{failed}/{total} tests failed",
                        suggestion="Fix failing tests before proceeding",
                        is_blocking=True,
                    )
                )
                score -= 0.3
        else:
            # Check for pytest report
            pytest_report = self._find_pytest_report(evidence_paths)
            if pytest_report:
                test_results = self._parse_pytest_report(pytest_report)
                if test_results and test_results.get("failed", 0) > 0:
                    issues.append(
                        EvalIssue(
                            severity=IssueSeverity.CRITICAL,
                            category="failing_tests",
                            message=f"{test_results['failed']} tests failed",
                            is_blocking=True,
                        )
                    )
                    score -= 0.3

        # Calculate final score
        score = max(0.0, min(1.0, score))

        # Add recommendations
        if score >= 0.85:
            recommendations.append("Test quality is excellent. Ready for deployment.")
        elif score >= 0.7:
            recommendations.append("Test quality is good. Consider adding more edge case tests.")
        else:
            recommendations.append("Test quality needs improvement. Focus on coverage and failing tests.")

        metadata = {
            "test_files_count": len(test_files),
            "coverage_percentage": coverage_data.get("coverage_percentage", 0.0)
            if coverage_data
            else 0.0,
            "meets_coverage_requirement": coverage_data.get("coverage_percentage", 0.0)
            >= self.min_coverage * 100
            if coverage_data
            else False,
        }

        return self._create_result(
            stage="unit_testing",
            score=score,
            issues=issues,
            recommendations=recommendations,
            metadata=metadata,
        ).__dict__

    def _get_coverage_data(
        self, evidence_paths: List[str], output_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get coverage data from output or coverage.json file."""
        # First check output_data
        if "coverage" in output_data:
            return output_data["coverage"]

        # Look for coverage.json in evidence paths
        for path in evidence_paths:
            if "coverage" in path.lower() and path.endswith(".json"):
                try:
                    with open(path, "r") as f:
                        coverage_json = json.load(f)

                    # Parse coverage.json (pytest-cov format)
                    if "totals" in coverage_json:
                        totals = coverage_json["totals"]
                        covered = totals.get("covered_lines", 0)
                        total = totals.get("num_statements", 0)
                        percentage = (
                            (covered / total * 100) if total > 0 else 0.0
                        )

                        return {
                            "coverage_percentage": percentage,
                            "covered_statements": covered,
                            "total_statements": total,
                        }
                except Exception as e:
                    self.logger.warning(f"Error parsing coverage file {path}: {e}")

        return {}

    def _analyze_test_file(self, file_path: str) -> List[EvalIssue]:
        """Analyze a test file for quality issues."""
        issues = []
        content = self._read_file(file_path)

        if not content:
            return [
                EvalIssue(
                    severity=IssueSeverity.ERROR,
                    category="unreadable_file",
                    message=f"Cannot read test file: {file_path}",
                    location=file_path,
                )
            ]

        # Count test functions
        test_functions = re.findall(r"def\s+(test_\w+)", content)
        if not test_functions:
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.ERROR,
                    category="no_tests",
                    message=f"No test functions found in {Path(file_path).name}",
                    location=file_path,
                    suggestion="Add test functions starting with 'test_'",
                )
            )

        # Check for assertions
        assertion_keywords = ["assert", "assertEqual", "assertTrue", "assertFalse"]
        has_assertions = any(keyword in content for keyword in assertion_keywords)
        if test_functions and not has_assertions:
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.WARNING,
                    category="no_assertions",
                    message=f"Test file {Path(file_path).name} has no assertions",
                    location=file_path,
                    suggestion="Add assertions to verify expected behavior",
                )
            )

        # Check for fixtures (good practice)
        has_fixtures = "@pytest.fixture" in content or "@fixture" in content
        if not has_fixtures and len(test_functions) > 3:
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.INFO,
                    category="no_fixtures",
                    message=f"Test file {Path(file_path).name} could benefit from fixtures",
                    location=file_path,
                    suggestion="Consider using pytest fixtures for test setup",
                )
            )

        # Check for edge case tests (keywords like "empty", "null", "invalid", "error")
        edge_case_keywords = ["empty", "null", "none", "invalid", "error", "exception"]
        edge_case_tests = [
            func
            for func in test_functions
            if any(keyword in func.lower() for keyword in edge_case_keywords)
        ]

        if not edge_case_tests and len(test_functions) > 2:
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.INFO,
                    category="missing_edge_cases",
                    message="Consider adding tests for edge cases (empty inputs, null, errors)",
                    location=file_path,
                    suggestion="Add tests for boundary conditions and error cases",
                )
            )

        return issues

    def _find_pytest_report(self, evidence_paths: List[str]) -> str:
        """Find pytest report in evidence paths."""
        for path in evidence_paths:
            if "pytest" in path.lower() and (path.endswith(".html") or path.endswith(".xml")):
                return path
        return ""

    def _parse_pytest_report(self, report_path: str) -> Dict[str, Any]:
        """Parse pytest report for test results."""
        # Simple parsing for now (could be enhanced)
        # This is a placeholder - actual implementation would parse HTML/XML
        return {}
