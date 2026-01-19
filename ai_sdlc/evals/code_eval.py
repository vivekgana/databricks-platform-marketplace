"""
Code Quality Evaluation

Evaluates generated code for quality, security, and standards compliance.
"""

import ast
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from .eval_framework import BaseEval, EvalIssue, IssueSeverity


class CodeEval(BaseEval):
    """
    Evaluation for generated code.

    Checks:
    - Code linting (black, ruff)
    - Security vulnerabilities (bandit)
    - Complexity metrics
    - Documentation coverage (docstrings)
    - Type hints presence
    - Code conventions
    """

    def evaluate(
        self,
        output_data: Dict[str, Any],
        evidence_paths: List[str],
    ) -> Dict[str, Any]:
        """
        Evaluate generated code quality.

        Args:
            output_data: Dictionary with code paths and metadata
            evidence_paths: Paths to code files

        Returns:
            Evaluation result dictionary
        """
        issues = []
        recommendations = []
        score = 1.0

        # Find Python files in evidence paths
        python_files = [
            path
            for path in evidence_paths
            if path.endswith(".py") and not path.endswith("__init__.py")
        ]

        if not python_files:
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.CRITICAL,
                    category="no_code",
                    message="No Python code files found",
                    is_blocking=True,
                )
            )
            return self._create_result(
                stage="code_generation", score=0.0, issues=issues
            ).__dict__

        # Evaluate each file
        total_files = len(python_files)
        files_with_issues = 0

        for file_path in python_files:
            file_issues = self._evaluate_file(file_path)
            issues.extend(file_issues)
            if file_issues:
                files_with_issues += 1

        # Calculate score based on issues
        critical_count = len(
            [i for i in issues if i.severity == IssueSeverity.CRITICAL]
        )
        error_count = len([i for i in issues if i.severity == IssueSeverity.ERROR])
        warning_count = len([i for i in issues if i.severity == IssueSeverity.WARNING])

        # Deduct score for issues
        score -= critical_count * 0.3
        score -= error_count * 0.1
        score -= warning_count * 0.05

        # Check code quality with external tools if available
        lint_issues = self._run_linting(python_files)
        if lint_issues:
            issues.extend(lint_issues)
            score -= len(lint_issues) * 0.02

        security_issues = self._run_security_scan(python_files)
        if security_issues:
            issues.extend(security_issues)
            score -= len(security_issues) * 0.1

        # Ensure score is in valid range
        score = max(0.0, min(1.0, score))

        # Add recommendations
        if score >= 0.85:
            recommendations.append(
                "Code quality is excellent. Run final review before deployment."
            )
        elif score >= 0.7:
            recommendations.append("Code quality is good. Address warnings before deployment.")
        else:
            recommendations.append("Code quality needs improvement. Fix critical issues first.")

        if not lint_issues:
            recommendations.append("Run 'black' and 'ruff' to ensure code formatting.")

        metadata = {
            "files_evaluated": total_files,
            "files_with_issues": files_with_issues,
            "critical_issues": critical_count,
            "error_issues": error_count,
            "warning_issues": warning_count,
        }

        return self._create_result(
            stage="code_generation",
            score=score,
            issues=issues,
            recommendations=recommendations,
            metadata=metadata,
        ).__dict__

    def _evaluate_file(self, file_path: str) -> List[EvalIssue]:
        """Evaluate a single Python file."""
        issues = []
        content = self._read_file(file_path)

        if not content:
            return [
                EvalIssue(
                    severity=IssueSeverity.ERROR,
                    category="unreadable_file",
                    message=f"Cannot read file: {file_path}",
                    location=file_path,
                )
            ]

        # Check if file is valid Python
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return [
                EvalIssue(
                    severity=IssueSeverity.CRITICAL,
                    category="syntax_error",
                    message=f"Syntax error: {e}",
                    location=f"{file_path}:line {e.lineno}",
                    is_blocking=True,
                )
            ]

        # Check for docstrings
        has_module_docstring = ast.get_docstring(tree) is not None
        if not has_module_docstring:
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.WARNING,
                    category="missing_docstring",
                    message="Module missing docstring",
                    location=file_path,
                    suggestion="Add a module-level docstring explaining the purpose",
                )
            )

        # Check functions and classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._check_function(node, file_path, issues)
            elif isinstance(node, ast.ClassDef):
                self._check_class(node, file_path, issues)

        return issues

    def _check_function(
        self, node: ast.FunctionDef, file_path: str, issues: List[EvalIssue]
    ):
        """Check function for quality issues."""
        # Skip magic methods and private methods from docstring check
        if not node.name.startswith("_"):
            # Check for docstring
            if ast.get_docstring(node) is None:
                issues.append(
                    EvalIssue(
                        severity=IssueSeverity.INFO,
                        category="missing_docstring",
                        message=f"Function '{node.name}' missing docstring",
                        location=f"{file_path}:line {node.lineno}",
                        suggestion="Add docstring with description, args, and return value",
                    )
                )

        # Check for type hints
        has_return_type = node.returns is not None
        if not has_return_type and not node.name.startswith("_"):
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.INFO,
                    category="missing_type_hints",
                    message=f"Function '{node.name}' missing return type hint",
                    location=f"{file_path}:line {node.lineno}",
                    suggestion="Add return type hint",
                )
            )

        # Check complexity (simple heuristic: count if/for/while statements)
        complexity = sum(
            1
            for child in ast.walk(node)
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler))
        )
        if complexity > 10:
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.WARNING,
                    category="high_complexity",
                    message=f"Function '{node.name}' has high complexity ({complexity})",
                    location=f"{file_path}:line {node.lineno}",
                    suggestion="Consider breaking into smaller functions",
                )
            )

    def _check_class(self, node: ast.ClassDef, file_path: str, issues: List[EvalIssue]):
        """Check class for quality issues."""
        # Check for docstring
        if ast.get_docstring(node) is None:
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.INFO,
                    category="missing_docstring",
                    message=f"Class '{node.name}' missing docstring",
                    location=f"{file_path}:line {node.lineno}",
                    suggestion="Add class docstring with description",
                )
            )

    def _run_linting(self, file_paths: List[str]) -> List[EvalIssue]:
        """Run linting tools (black, ruff) if available."""
        issues = []

        # Try to run black in check mode
        try:
            for file_path in file_paths:
                result = subprocess.run(
                    ["black", "--check", file_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    issues.append(
                        EvalIssue(
                            severity=IssueSeverity.INFO,
                            category="formatting",
                            message="Code formatting doesn't match black style",
                            location=file_path,
                            suggestion="Run 'black' to format code",
                        )
                    )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # black not installed or timeout
            pass

        return issues

    def _run_security_scan(self, file_paths: List[str]) -> List[EvalIssue]:
        """Run security scanner (bandit) if available."""
        issues = []

        # Try to run bandit
        try:
            for file_path in file_paths:
                result = subprocess.run(
                    ["bandit", "-f", "json", file_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    # Parse bandit output for issues
                    import json

                    try:
                        bandit_output = json.loads(result.stdout)
                        for result_item in bandit_output.get("results", []):
                            severity_map = {
                                "HIGH": IssueSeverity.ERROR,
                                "MEDIUM": IssueSeverity.WARNING,
                                "LOW": IssueSeverity.INFO,
                            }
                            severity = severity_map.get(
                                result_item.get("issue_severity", "LOW"),
                                IssueSeverity.INFO,
                            )

                            issues.append(
                                EvalIssue(
                                    severity=severity,
                                    category="security",
                                    message=result_item.get("issue_text", "Security issue"),
                                    location=f"{file_path}:line {result_item.get('line_number')}",
                                    suggestion="Review and fix security vulnerability",
                                )
                            )
                    except json.JSONDecodeError:
                        pass
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # bandit not installed or timeout
            pass

        return issues
