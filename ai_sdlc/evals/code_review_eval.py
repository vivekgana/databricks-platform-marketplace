"""
Code Review Evaluator

Validates code review results and enforces quality gates.
"""

from typing import Any, Dict, List

from .base_eval import BaseEval, EvalIssue


class CodeReviewEval(BaseEval):
    """
    Evaluator for code review results.

    Quality Gates:
    - No critical severity issues (blocking)
    - Severity score < 50 (blocking)
    - High severity issues < 5 (warning)
    """

    def evaluate(self, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate code review results.

        Args:
            agent_result: Result from CodeReviewAgent

        Returns:
            Evaluation result with score and issues
        """
        if not agent_result.get("success"):
            return self._create_failure_result(
                "Code review agent failed",
                [
                    EvalIssue(
                        severity="critical",
                        category="agent_failure",
                        description=agent_result.get("error_message", "Unknown error"),
                        location="N/A",
                        recommendation="Review agent logs and fix errors",
                        blocking=True,
                    )
                ],
            )

        data = agent_result.get("data", {})
        summary = data.get("summary", {})

        issues = []
        score = 1.0  # Start with perfect score

        # Check for critical severity issues (blocking)
        critical_count = summary.get("critical_count", 0)
        if critical_count > 0:
            issues.append(
                EvalIssue(
                    severity="critical",
                    category="security",
                    description=f"Found {critical_count} critical severity issues",
                    location="Multiple files",
                    recommendation="Fix all critical issues before proceeding",
                    blocking=True,
                )
            )
            score -= 0.5

        # Check severity score (blocking if >= 50)
        severity_score = data.get("severity_score", 0)
        if severity_score >= 50:
            issues.append(
                EvalIssue(
                    severity="critical",
                    category="quality",
                    description=f"Severity score {severity_score} exceeds threshold (50)",
                    location="Overall codebase",
                    recommendation="Address high and critical issues to reduce score",
                    blocking=True,
                )
            )
            score -= 0.3

        # Check high severity issues (warning if >= 5)
        high_count = summary.get("high_count", 0)
        if high_count >= 5:
            issues.append(
                EvalIssue(
                    severity="high",
                    category="quality",
                    description=f"Found {high_count} high severity issues",
                    location="Multiple files",
                    recommendation="Consider fixing high severity issues before PR",
                    blocking=False,
                )
            )
            score -= 0.1

        # Check if files were actually reviewed
        files_reviewed = data.get("files_reviewed", 0)
        if files_reviewed == 0:
            issues.append(
                EvalIssue(
                    severity="high",
                    category="coverage",
                    description="No files were reviewed",
                    location="N/A",
                    recommendation="Ensure code files are provided for review",
                    blocking=True,
                )
            )
            score = 0.0

        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))

        # Check if passed (no blocking issues)
        blocking_issues = [issue for issue in issues if issue.blocking]
        passed = len(blocking_issues) == 0 and score >= self.min_score

        return self._create_result(
            score=score,
            passed=passed,
            issues=issues,
            metrics={
                "files_reviewed": files_reviewed,
                "total_findings": summary.get("total_findings", 0),
                "critical_count": critical_count,
                "high_count": high_count,
                "medium_count": summary.get("medium_count", 0),
                "low_count": summary.get("low_count", 0),
                "severity_score": severity_score,
            },
            recommendations=self._generate_recommendations(summary, issues),
        )

    def _generate_recommendations(
        self, summary: Dict[str, Any], issues: List[EvalIssue]
    ) -> List[str]:
        """Generate recommendations based on review results."""
        recommendations = []

        critical_count = summary.get("critical_count", 0)
        high_count = summary.get("high_count", 0)
        severity_score = summary.get("severity_score", 0)

        if critical_count > 0:
            recommendations.append(
                f"Fix {critical_count} critical security/logic issues immediately"
            )

        if high_count > 0:
            recommendations.append(
                f"Address {high_count} high severity issues before PR submission"
            )

        if severity_score >= 50:
            recommendations.append(
                "Overall code quality needs improvement before proceeding"
            )

        if not recommendations:
            recommendations.append("Code review passed - proceed with PR creation")

        return recommendations
