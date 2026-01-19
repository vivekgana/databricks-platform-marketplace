"""
PySpark Code Review Agent

Performs comprehensive code review for PySpark applications covering:
- Logic errors and edge cases
- Security vulnerabilities
- Performance optimization opportunities
- Best practices violations
"""

import ast
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .base_agent import BaseAgent


class CodeReviewAgent(BaseAgent):
    """
    Agent for reviewing PySpark code quality, security, and optimization.

    Performs static analysis and pattern matching to identify:
    - Logic errors and edge cases
    - Security vulnerabilities (SQL injection, path traversal, etc.)
    - Performance anti-patterns
    - Best practices violations
    """

    # Security patterns to detect
    SECURITY_PATTERNS = {
        "sql_injection": {
            "pattern": r'\.sql\(["\'].*?\+.*?["\']',
            "severity": "critical",
            "description": "Potential SQL injection vulnerability",
            "recommendation": "Use parameterized queries or sanitize input",
        },
        "command_injection": {
            "pattern": r"os\.(system|popen|exec|spawn)",
            "severity": "critical",
            "description": "Potential command injection vulnerability",
            "recommendation": "Avoid executing shell commands with user input",
        },
        "path_traversal": {
            "pattern": r'open\(["\'].*?\+.*?["\']',
            "severity": "high",
            "description": "Potential path traversal vulnerability",
            "recommendation": "Validate and sanitize file paths",
        },
        "eval_usage": {
            "pattern": r"\beval\(",
            "severity": "critical",
            "description": "Use of eval() can execute arbitrary code",
            "recommendation": "Replace eval() with safer alternatives",
        },
        "pickle_usage": {
            "pattern": r"pickle\.(load|loads)",
            "severity": "high",
            "description": "Unpickling untrusted data can execute arbitrary code",
            "recommendation": "Use JSON or other safe serialization formats",
        },
    }

    # PySpark performance anti-patterns
    PERFORMANCE_PATTERNS = {
        "collect_usage": {
            "pattern": r"\.collect\(\)",
            "severity": "medium",
            "description": "collect() brings all data to driver, may cause OOM",
            "recommendation": "Use take(n) or persist() with actions instead",
        },
        "udf_without_hint": {
            "pattern": r"@udf\s*\n\s*def",
            "severity": "low",
            "description": "UDF without return type hint (slower execution)",
            "recommendation": "Specify return type: @udf(returnType=StringType())",
        },
        "rdd_operations": {
            "pattern": r"\.rdd\.",
            "severity": "medium",
            "description": "RDD operations are slower than DataFrame operations",
            "recommendation": "Use DataFrame/Dataset APIs when possible",
        },
        "cartesian_join": {
            "pattern": r"\.crossJoin\(",
            "severity": "high",
            "description": "Cartesian join creates N×M rows, very expensive",
            "recommendation": "Add join condition or filter before join",
        },
        "count_after_filter": {
            "pattern": r"\.filter\(.*?\)\.count\(\)",
            "severity": "low",
            "description": "Multiple filter().count() calls scan data multiple times",
            "recommendation": "Cache filtered DataFrame if used multiple times",
        },
    }

    # Logic and edge case patterns
    LOGIC_PATTERNS = {
        "null_check_missing": {
            "pattern": r"\.filter\([^)]*==",
            "severity": "medium",
            "description": "Equality check without null handling",
            "recommendation": "Use isNull(), isNotNull(), or eqNullSafe()",
        },
        "division_by_zero": {
            "pattern": r"/\s*\w+\s*(?![\s\)])",
            "severity": "medium",
            "description": "Potential division by zero",
            "recommendation": "Add null/zero check before division",
        },
        "empty_dataframe_check": {
            "pattern": r"df\.count\(\)\s*==\s*0",
            "severity": "low",
            "description": "Expensive empty check using count()",
            "recommendation": "Use df.head(1) or df.isEmpty() instead",
        },
        "schema_inference": {
            "pattern": r"\.read\.(json|csv|parquet)\([^)]*\)",
            "severity": "low",
            "description": "Reading without explicit schema (slow and error-prone)",
            "recommendation": "Define explicit schema for better performance",
        },
    }

    def execute(
        self,
        input_data: Dict[str, Any],
        timeout_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive code review.

        Args:
            input_data: Dictionary with:
                - code_files: List of file paths to review
                - severity_threshold: Minimum severity to report (optional)
                - review_type: Type of review (security, performance, logic, all)

        Returns:
            Result dictionary with review findings
        """
        self._log_start()

        try:
            code_files = input_data.get("code_files", [])
            severity_threshold = input_data.get("severity_threshold", "low")
            review_type = input_data.get("review_type", "all")

            if not code_files:
                return self._create_result(
                    success=False,
                    error_message="No code files provided for review",
                )

            # Review each file
            all_findings = []
            files_reviewed = 0

            for file_path in code_files:
                if not Path(file_path).exists():
                    self.logger.warning(f"File not found: {file_path}")
                    continue

                # Only review Python files
                if not file_path.endswith(".py"):
                    continue

                findings = self._review_file(file_path, review_type, severity_threshold)
                all_findings.extend(findings)
                files_reviewed += 1

            # Categorize findings
            categorized = self._categorize_findings(all_findings)

            # Calculate severity scores
            severity_score = self._calculate_severity_score(all_findings)

            # Generate review report
            report = self._generate_review_report(
                categorized, severity_score, files_reviewed
            )
            report_file = self._save_evidence_file("code-review-report.md", report)

            # Generate JSON summary
            summary = {
                "files_reviewed": files_reviewed,
                "total_findings": len(all_findings),
                "critical_count": categorized["critical"],
                "high_count": categorized["high"],
                "medium_count": categorized["medium"],
                "low_count": categorized["low"],
                "severity_score": severity_score,
                "passed": severity_score < 50,  # Configurable threshold
                "findings": [
                    {
                        "file": f["file"],
                        "line": f["line"],
                        "severity": f["severity"],
                        "category": f["category"],
                        "description": f["description"],
                        "recommendation": f["recommendation"],
                    }
                    for f in all_findings
                ],
            }

            summary_file = self._save_evidence_file(
                "code-review-summary.json",
                json.dumps(summary, indent=2),
            )

            evidence_paths = [report_file, summary_file]

            self._log_complete(True)

            return self._create_result(
                success=True,
                data={
                    "files_reviewed": files_reviewed,
                    "total_findings": len(all_findings),
                    "severity_score": severity_score,
                    "passed": summary["passed"],
                    "categorized": categorized,
                    "summary": summary,
                    "report_file": report_file,
                },
                evidence_paths=evidence_paths,
            )

        except Exception as e:
            self.logger.error(f"Error during code review: {e}")
            return self._create_result(
                success=False,
                error_message=f"Code review failed: {e}",
            )

    def _review_file(
        self, file_path: str, review_type: str, severity_threshold: str
    ) -> List[Dict[str, Any]]:
        """
        Review a single file.

        Args:
            file_path: Path to file
            review_type: Type of review (security, performance, logic, all)
            severity_threshold: Minimum severity to report

        Returns:
            List of findings
        """
        findings = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

            # Run security checks
            if review_type in ["security", "all"]:
                findings.extend(
                    self._check_security(file_path, code, severity_threshold)
                )

            # Run performance checks
            if review_type in ["performance", "all"]:
                findings.extend(
                    self._check_performance(file_path, code, severity_threshold)
                )

            # Run logic checks
            if review_type in ["logic", "all"]:
                findings.extend(self._check_logic(file_path, code, severity_threshold))

            # Run best practices checks
            if review_type in ["all"]:
                findings.extend(
                    self._check_best_practices(file_path, code, severity_threshold)
                )

        except Exception as e:
            self.logger.error(f"Error reviewing {file_path}: {e}")

        return findings

    def _check_security(
        self, file_path: str, code: str, severity_threshold: str
    ) -> List[Dict[str, Any]]:
        """Check for security vulnerabilities."""
        findings = []

        for pattern_name, pattern_info in self.SECURITY_PATTERNS.items():
            matches = re.finditer(pattern_info["pattern"], code, re.MULTILINE)

            for match in matches:
                line_num = code[: match.start()].count("\n") + 1

                if self._meets_severity_threshold(
                    pattern_info["severity"], severity_threshold
                ):
                    findings.append(
                        {
                            "file": file_path,
                            "line": line_num,
                            "severity": pattern_info["severity"],
                            "category": "security",
                            "issue": pattern_name,
                            "description": pattern_info["description"],
                            "recommendation": pattern_info["recommendation"],
                            "code_snippet": self._get_code_snippet(code, line_num),
                        }
                    )

        return findings

    def _check_performance(
        self, file_path: str, code: str, severity_threshold: str
    ) -> List[Dict[str, Any]]:
        """Check for performance anti-patterns."""
        findings = []

        for pattern_name, pattern_info in self.PERFORMANCE_PATTERNS.items():
            matches = re.finditer(pattern_info["pattern"], code, re.MULTILINE)

            for match in matches:
                line_num = code[: match.start()].count("\n") + 1

                if self._meets_severity_threshold(
                    pattern_info["severity"], severity_threshold
                ):
                    findings.append(
                        {
                            "file": file_path,
                            "line": line_num,
                            "severity": pattern_info["severity"],
                            "category": "performance",
                            "issue": pattern_name,
                            "description": pattern_info["description"],
                            "recommendation": pattern_info["recommendation"],
                            "code_snippet": self._get_code_snippet(code, line_num),
                        }
                    )

        return findings

    def _check_logic(
        self, file_path: str, code: str, severity_threshold: str
    ) -> List[Dict[str, Any]]:
        """Check for logic errors and edge cases."""
        findings = []

        for pattern_name, pattern_info in self.LOGIC_PATTERNS.items():
            matches = re.finditer(pattern_info["pattern"], code, re.MULTILINE)

            for match in matches:
                line_num = code[: match.start()].count("\n") + 1

                if self._meets_severity_threshold(
                    pattern_info["severity"], severity_threshold
                ):
                    findings.append(
                        {
                            "file": file_path,
                            "line": line_num,
                            "severity": pattern_info["severity"],
                            "category": "logic",
                            "issue": pattern_name,
                            "description": pattern_info["description"],
                            "recommendation": pattern_info["recommendation"],
                            "code_snippet": self._get_code_snippet(code, line_num),
                        }
                    )

        return findings

    def _check_best_practices(
        self, file_path: str, code: str, severity_threshold: str
    ) -> List[Dict[str, Any]]:
        """Check for best practices violations."""
        findings = []

        # Check for docstrings
        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        findings.append(
                            {
                                "file": file_path,
                                "line": node.lineno,
                                "severity": "low",
                                "category": "best_practices",
                                "issue": "missing_docstring",
                                "description": f"{node.__class__.__name__} '{node.name}' missing docstring",
                                "recommendation": "Add docstring documenting purpose and parameters",
                                "code_snippet": self._get_code_snippet(
                                    code, node.lineno
                                ),
                            }
                        )

        except Exception as e:
            self.logger.warning(f"AST parsing failed for {file_path}: {e}")

        return findings

    def _meets_severity_threshold(self, severity: str, threshold: str) -> bool:
        """Check if severity meets threshold."""
        severity_levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        return severity_levels.get(severity, 0) >= severity_levels.get(threshold, 0)

    def _get_code_snippet(self, code: str, line_num: int, context: int = 2) -> str:
        """Get code snippet around line number."""
        lines = code.split("\n")
        start = max(0, line_num - context - 1)
        end = min(len(lines), line_num + context)

        snippet_lines = []
        for i in range(start, end):
            marker = ">>>" if i == line_num - 1 else "   "
            snippet_lines.append(f"{marker} {i+1}: {lines[i]}")

        return "\n".join(snippet_lines)

    def _categorize_findings(self, findings: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize findings by severity."""
        categorized = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        for finding in findings:
            severity = finding.get("severity", "low")
            if severity in categorized:
                categorized[severity] += 1

        return categorized

    def _calculate_severity_score(self, findings: List[Dict[str, Any]]) -> float:
        """
        Calculate overall severity score.

        Score calculation:
        - Critical: 10 points each
        - High: 5 points each
        - Medium: 2 points each
        - Low: 1 point each
        """
        severity_weights = {
            "critical": 10,
            "high": 5,
            "medium": 2,
            "low": 1,
        }

        total_score = sum(
            severity_weights.get(f.get("severity", "low"), 0) for f in findings
        )

        return total_score

    def _generate_review_report(
        self,
        categorized: Dict[str, int],
        severity_score: float,
        files_reviewed: int,
    ) -> str:
        """Generate comprehensive review report."""
        report = f"""# PySpark Code Review Report

**Work Item ID:** {self.work_item_id}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Files Reviewed:** {files_reviewed}

---

## Summary

**Total Findings:** {sum(categorized.values())}
**Severity Score:** {severity_score} / 100
**Review Status:** {'❌ FAILED' if severity_score >= 50 else '✅ PASSED'}

### Findings by Severity

| Severity | Count |
|----------|-------|
| 🔴 Critical | {categorized['critical']} |
| 🟠 High | {categorized['high']} |
| 🟡 Medium | {categorized['medium']} |
| 🟢 Low | {categorized['low']} |

---

## Severity Score Calculation

- Critical issues: {categorized['critical']} × 10 = {categorized['critical'] * 10} points
- High issues: {categorized['high']} × 5 = {categorized['high'] * 5} points
- Medium issues: {categorized['medium']} × 2 = {categorized['medium'] * 2} points
- Low issues: {categorized['low']} × 1 = {categorized['low']} points

**Total Score:** {severity_score}
**Threshold:** 50 (score >= 50 fails review)

---

## Recommendations

"""

        if severity_score >= 50:
            report += """
### 🚨 Action Required

The code review has identified significant issues that must be addressed before proceeding:

1. **Fix all critical issues immediately** - These represent security vulnerabilities or major bugs
2. **Address high-severity issues** - These can cause performance problems or errors
3. **Review medium-severity issues** - Consider fixing these before PR submission
4. **Low-severity issues can be addressed later** - Track as technical debt

"""
        else:
            report += """
### ✅ Code Quality Acceptable

The code review passed with acceptable quality. However, consider addressing:

1. **Any remaining high-severity issues** for improved robustness
2. **Medium-severity issues** to prevent future problems
3. **Low-severity issues** to improve code maintainability

"""

        report += """
---

## Detailed Findings

See `code-review-summary.json` for complete findings with:
- File locations
- Line numbers
- Code snippets
- Specific recommendations

---

**Review Completed**
**Generated by:** AI-SDLC Code Review Agent
"""

        return report
