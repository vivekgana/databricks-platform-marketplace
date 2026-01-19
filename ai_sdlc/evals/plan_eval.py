"""
Plan Evaluation

Evaluates implementation plans for clarity, completeness, and feasibility.
"""

import re
from typing import Any, Dict, List

from .eval_framework import BaseEval, EvalIssue, IssueSeverity


class PlanEval(BaseEval):
    """
    Evaluation for implementation plans.

    Checks that plans have:
    - Clear implementation approach
    - All requirements covered
    - Risks identified
    - Dependencies listed
    - Reasonable scope
    """

    def evaluate(
        self,
        output_data: Dict[str, Any],
        evidence_paths: List[str],
    ) -> Dict[str, Any]:
        """
        Evaluate an implementation plan.

        Args:
            output_data: Dictionary with plan data
            evidence_paths: Paths to plan documents

        Returns:
            Evaluation result dictionary
        """
        issues = []
        recommendations = []
        score = 1.0

        # Get plan content
        plan_text = output_data.get("plan_text", "")
        if not plan_text:
            # Try to read from evidence files
            for path in evidence_paths:
                if "plan" in path.lower() and path.endswith(".md"):
                    content = self._read_file(path)
                    if content:
                        plan_text = content
                        break

        if not plan_text:
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.CRITICAL,
                    category="missing_plan",
                    message="No implementation plan found",
                    is_blocking=True,
                )
            )
            return self._create_result(
                stage="planning", score=0.0, issues=issues
            ).__dict__

        # Check plan length (should be substantial)
        if len(plan_text) < 200:
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.ERROR,
                    category="insufficient_detail",
                    message="Plan is too short, lacks detail",
                    suggestion="Add more details about implementation approach, steps, and considerations",
                    is_blocking=True,
                )
            )
            score -= 0.3

        # Check for required sections
        required_sections = [
            ("overview", r"##\s*(?:overview|summary)", "Overview/Summary"),
            ("approach", r"##\s*(?:approach|implementation|solution)", "Approach"),
            ("requirements", r"##\s*(?:requirements|acceptance)", "Requirements"),
            ("risks", r"##\s*(?:risks|challenges)", "Risks/Challenges"),
        ]

        missing_sections = []
        for section_name, pattern, display_name in required_sections:
            if not re.search(pattern, plan_text, re.IGNORECASE):
                missing_sections.append(display_name)
                score -= 0.1

        if missing_sections:
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.WARNING,
                    category="missing_sections",
                    message=f"Plan missing sections: {', '.join(missing_sections)}",
                    suggestion="Add sections for: " + ", ".join(missing_sections),
                )
            )

        # Check for dependencies
        has_dependencies = bool(re.search(r"##\s*dependencies", plan_text, re.IGNORECASE))
        if not has_dependencies:
            recommendations.append(
                "Consider adding a Dependencies section to identify external requirements"
            )

        # Check for implementation steps
        has_steps = bool(re.search(r"##\s*(?:steps|tasks|phases)", plan_text, re.IGNORECASE))
        if not has_steps:
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.WARNING,
                    category="missing_steps",
                    message="Plan lacks clear implementation steps",
                    suggestion="Add a step-by-step breakdown of implementation tasks",
                )
            )
            score -= 0.1

        # Check for technical details
        technical_keywords = [
            "api",
            "database",
            "function",
            "class",
            "module",
            "endpoint",
            "query",
            "schema",
        ]
        has_technical_detail = any(
            keyword in plan_text.lower() for keyword in technical_keywords
        )
        if not has_technical_detail:
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.WARNING,
                    category="lacks_technical_detail",
                    message="Plan lacks technical implementation details",
                    suggestion="Add specific technical details about APIs, databases, functions, etc.",
                )
            )
            score -= 0.1

        # Check for acceptance criteria reference
        has_ac_reference = "acceptance criteria" in plan_text.lower() or "AC-" in plan_text
        if not has_ac_reference:
            recommendations.append(
                "Reference specific acceptance criteria from requirements"
            )

        # Check plan structure (should have multiple headings)
        heading_count = len(re.findall(r"^##\s+", plan_text, re.MULTILINE))
        if heading_count < 3:
            issues.append(
                EvalIssue(
                    severity=IssueSeverity.INFO,
                    category="insufficient_structure",
                    message="Plan lacks clear structure (few section headings)",
                    suggestion="Organize plan into clear sections with headings",
                )
            )
            score -= 0.05

        # Check for code examples or pseudocode
        has_code_blocks = "```" in plan_text
        if has_code_blocks:
            # Bonus points for including code examples
            score += 0.05
        else:
            recommendations.append(
                "Consider including code examples or pseudocode for clarity"
            )

        # Ensure score is in valid range
        score = max(0.0, min(1.0, score))

        # Add positive recommendations if plan is good
        if score >= 0.8:
            recommendations.append(
                "Plan structure is solid. Ensure team reviews before implementation."
            )

        metadata = {
            "plan_length": len(plan_text),
            "section_count": heading_count,
            "has_code_examples": has_code_blocks,
            "has_dependencies": has_dependencies,
            "has_steps": has_steps,
        }

        return self._create_result(
            stage="planning",
            score=score,
            issues=issues,
            recommendations=recommendations,
            metadata=metadata,
        ).__dict__
