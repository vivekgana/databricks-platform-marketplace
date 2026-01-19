# AI-SDLC Evaluation Framework Guide

**Document Version:** 1.0
**Last Updated:** 2026-01-17
**Prepared by:** AI-SDLC Platform Team

---

## Table of Contents

1. [Overview](#overview)
2. [Evaluation Architecture](#evaluation-architecture)
3. [Creating Evaluators](#creating-evaluators)
4. [Built-in Evaluators](#built-in-evaluators)
5. [Scoring System](#scoring-system)
6. [Quality Gates](#quality-gates)
7. [Custom Evaluators](#custom-evaluators)
8. [Testing Evaluators](#testing-evaluators)
9. [Best Practices](#best-practices)
10. [Reference](#reference)

---

## Overview

### What is the Evaluation Framework?

The AI-SDLC Evaluation Framework provides **quality gates** that validate the output of each workflow stage before allowing progression to the next stage. Each evaluator:

- Analyzes agent output and evidence
- Assigns a quality score (0.0 to 1.0)
- Identifies issues and blocking problems
- Provides actionable recommendations
- Determines pass/fail based on thresholds

### Why Evaluations Matter

**Without Evals:**
- Low-quality code proceeds to production
- Tests with poor coverage are accepted
- Performance issues go undetected
- Security vulnerabilities slip through

**With Evals:**
- Quality gates enforce standards
- Automated validation catches issues early
- Consistent quality across all work items
- Audit trail of quality metrics

### Evaluation Philosophy

1. **Automated Quality:** Machines enforce standards consistently
2. **Early Detection:** Catch issues before they propagate
3. **Actionable Feedback:** Provide specific recommendations
4. **Configurable Standards:** Adapt thresholds to your needs

---

## Evaluation Architecture

### Component Hierarchy

```
BaseEval (Abstract)
├── PlanEval
├── CodeEval
├── TestEval
├── QAEval
├── IntegrationEval
├── PerformanceEval
└── EvidenceEval
```

### Evaluation Flow

```
Agent completes execution
    ↓
Agent returns result dictionary
    ↓
Orchestrator calls evaluator.evaluate(result)
    ↓
Evaluator analyzes output and evidence
    ↓
Evaluator returns evaluation result
    ↓
Orchestrator checks: score >= threshold?
    ├─ YES → Proceed to next stage
    └─ NO → Stop workflow, report issues
```

### Evaluation Result Structure

```python
{
    "passed": bool,           # Overall pass/fail
    "score": float,           # 0.0 to 1.0
    "issues": [               # List of problems found
        {
            "severity": str,  # "critical", "high", "medium", "low"
            "category": str,  # "code_quality", "coverage", etc.
            "message": str,   # Human-readable description
            "location": str,  # Where the issue was found
        }
    ],
    "recommendations": [      # Suggestions for improvement
        str
    ],
    "metrics": {              # Stage-specific metrics
        str: Any
    },
    "blocking_issues": [      # Issues that must be fixed
        str
    ]
}
```

---

## Evaluation Architecture

### BaseEval Class

All evaluators extend the `BaseEval` abstract class:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseEval(ABC):
    """Base class for all evaluators."""

    def __init__(self, min_score: float = 0.7, config: Any = None):
        """
        Initialize evaluator.

        Args:
            min_score: Minimum passing score (0.0-1.0)
            config: Optional configuration
        """
        self.min_score = min_score
        self.config = config or {}

    @abstractmethod
    def evaluate(self, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate agent output.

        Args:
            agent_result: Agent execution result containing:
                - success: bool
                - output_data: Dict with agent outputs
                - evidence_files: List of evidence file paths

        Returns:
            Evaluation result dictionary
        """
        pass

    def _create_issue(
        self,
        severity: str,
        category: str,
        message: str,
        location: str = ""
    ) -> Dict[str, str]:
        """Create a standardized issue dictionary."""
        return {
            "severity": severity,
            "category": category,
            "message": message,
            "location": location,
        }

    def _is_passing_score(self, score: float) -> bool:
        """Check if score meets minimum threshold."""
        return score >= self.min_score
```

---

## Creating Evaluators

### Step 1: Define Evaluator Class

```python
from ai_sdlc.evals.base_eval import BaseEval
from typing import Any, Dict, List

class MyCustomEval(BaseEval):
    """
    Evaluator for [specific purpose].

    Validates [what it validates].
    """

    def __init__(self, min_score: float = 0.7, config: Any = None):
        super().__init__(min_score, config)

        # Load configuration
        self.custom_threshold = config.get("custom_threshold", 100) if config else 100

    def evaluate(self, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate agent output.

        Args:
            agent_result: Agent execution result

        Returns:
            Evaluation result
        """
        # Initialize evaluation state
        score = 0.0
        max_score = 1.0
        issues = []
        recommendations = []
        metrics = {}

        # Check if agent succeeded
        if not agent_result.get("success", False):
            return {
                "passed": False,
                "score": 0.0,
                "issues": [
                    self._create_issue(
                        "critical",
                        "execution",
                        "Agent execution failed",
                        ""
                    )
                ],
                "recommendations": ["Fix agent execution errors"],
                "metrics": {},
                "blocking_issues": ["Agent execution failed"],
            }

        # Extract output data
        output_data = agent_result.get("output_data", {})
        evidence_files = agent_result.get("evidence_files", [])

        # Perform evaluations
        score += self._evaluate_criteria_1(output_data, issues, recommendations)
        score += self._evaluate_criteria_2(output_data, issues, recommendations)
        score += self._evaluate_criteria_3(evidence_files, issues, recommendations)

        # Normalize score
        score = min(score, max_score)

        # Collect metrics
        metrics = self._collect_metrics(output_data)

        # Determine blocking issues
        blocking_issues = [
            issue["message"]
            for issue in issues
            if issue["severity"] == "critical"
        ]

        # Check if passed
        passed = self._is_passing_score(score) and len(blocking_issues) == 0

        return {
            "passed": passed,
            "score": score,
            "issues": issues,
            "recommendations": recommendations,
            "metrics": metrics,
            "blocking_issues": blocking_issues,
        }

    def _evaluate_criteria_1(
        self,
        output_data: Dict[str, Any],
        issues: List[Dict],
        recommendations: List[str]
    ) -> float:
        """Evaluate first criteria."""
        score = 0.0

        # Your evaluation logic
        value = output_data.get("metric_1", 0)
        if value >= self.custom_threshold:
            score = 0.3
        else:
            issues.append(
                self._create_issue(
                    "high",
                    "quality",
                    f"Metric 1 ({value}) below threshold ({self.custom_threshold})",
                    "output_data.metric_1"
                )
            )
            recommendations.append(f"Increase metric_1 to at least {self.custom_threshold}")

        return score
```

### Step 2: Register with Orchestrator

```python
from ai_sdlc.orchestration import WorkflowOrchestrator, WorkflowStage

orchestrator = WorkflowOrchestrator(...)

orchestrator.register_evaluator(
    stage=WorkflowStage.CUSTOM_STAGE,
    evaluator_class=MyCustomEval,
    eval_config={
        "min_score": 0.7,
        "custom_threshold": 100,
    }
)
```

---

## Built-in Evaluators

### 1. PlanEval

**Purpose:** Validate implementation plans

**Criteria:**
- Plan structure is complete
- Requirements are addressed
- Risks are identified
- Dependencies are listed
- Approach is clear

**Weights:**
- Structure completeness: 20%
- Requirements coverage: 30%
- Risk identification: 20%
- Dependencies: 15%
- Clarity: 15%

**Example:**
```python
from ai_sdlc.evals import PlanEval

eval = PlanEval(min_score=0.7)
result = eval.evaluate(agent_result)

# result = {
#     "passed": True,
#     "score": 0.85,
#     "issues": [],
#     "recommendations": ["Consider edge case X"],
#     "metrics": {
#         "requirements_covered": 8,
#         "requirements_total": 8,
#         "risks_identified": 3,
#     }
# }
```

### 2. CodeEval

**Purpose:** Validate generated code quality

**Criteria:**
- Passes linting (black, ruff)
- No security vulnerabilities (bandit)
- Has docstrings
- Has type hints
- Follows project conventions
- Complexity within limits

**Weights:**
- Linting: 20%
- Security: 25%
- Documentation: 20%
- Type hints: 15%
- Conventions: 10%
- Complexity: 10%

**Configuration:**
```python
code_eval = CodeEval(
    min_score=0.7,
    config={
        "max_complexity": 10,
        "require_docstrings": True,
        "require_type_hints": True,
    }
)
```

**Checks Performed:**
```bash
# Linting
black --check generated_code.py
ruff check generated_code.py

# Security
bandit -r generated_code.py

# Complexity
radon cc generated_code.py -a

# Documentation coverage
interrogate generated_code.py
```

### 3. TestEval

**Purpose:** Validate test quality and coverage

**Criteria:**
- Test coverage ≥ 80% (REQUIRED)
- All tests pass
- Tests have assertions
- Tests are independent
- Edge cases covered

**Weights:**
- Coverage: 40% (blocking if < 80%)
- Pass rate: 30%
- Assertions: 15%
- Independence: 10%
- Edge cases: 5%

**Critical Requirement:**
```python
# Test coverage MUST be >= 80%
if coverage < 0.80:
    return {
        "passed": False,
        "score": 0.0,
        "blocking_issues": [
            f"Test coverage {coverage:.1%} below minimum 80%"
        ]
    }
```

### 4. QAEval

**Purpose:** Validate UI testing results

**Criteria:**
- All UI tests pass
- Screenshots captured
- No console errors
- UI is responsive
- Evidence is complete

**Weights:**
- Test pass rate: 40%
- Screenshot evidence: 25%
- Console errors: 20%
- Responsiveness: 10%
- Evidence completeness: 5%

**Example:**
```python
qa_eval = QAEval(min_score=0.7)
result = qa_eval.evaluate(agent_result)

# Checks:
# - playwright_report.html: All tests passed?
# - screenshots/: At least 3 screenshots?
# - console-logs.txt: No critical errors?
```

### 5. IntegrationEval

**Purpose:** Validate integration testing

**Criteria:**
- API endpoints work
- Database operations succeed
- External integrations functional
- Data validation passes
- Error handling works

**Weights:**
- API tests: 30%
- Database tests: 30%
- External integrations: 20%
- Data validation: 10%
- Error handling: 10%

### 6. PerformanceEval

**Purpose:** Validate performance requirements

**Criteria:**
- Response time < 2s (REQUIRED)
- Success rate ≥ 95%
- No memory leaks
- Handles concurrent load
- Resource usage acceptable

**Weights:**
- Response time: 40% (blocking if > 2s)
- Success rate: 30%
- Memory usage: 15%
- Concurrency: 10%
- Resources: 5%

**Critical Requirement:**
```python
# Response time MUST be < 2000ms
if max_response_time_ms >= 2000:
    return {
        "passed": False,
        "score": 0.0,
        "blocking_issues": [
            f"Max response time {max_response_time_ms}ms exceeds 2000ms limit"
        ]
    }
```

### 7. EvidenceEval

**Purpose:** Validate evidence completeness

**Criteria:**
- All required artifacts present
- Metadata is complete
- Files are accessible
- Storage upload successful
- ADO updates successful

**Weights:**
- Artifacts present: 30%
- Metadata complete: 20%
- Accessibility: 20%
- Storage upload: 15%
- ADO updates: 15%

---

## Scoring System

### Score Ranges

| Score    | Grade | Meaning                              |
|----------|-------|--------------------------------------|
| 0.90-1.0 | A     | Excellent - Exceeds expectations     |
| 0.80-0.89| B     | Good - Meets expectations            |
| 0.70-0.79| C     | Acceptable - Minimum requirements    |
| 0.60-0.69| D     | Below standard - Needs improvement   |
| 0.0-0.59 | F     | Failing - Does not meet requirements |

### Default Threshold

**Minimum passing score: 0.7** (70%)

This can be configured per evaluator:
```python
evaluator = MyEval(min_score=0.8)  # Require 80%
```

### Score Calculation

Scores are typically weighted sums:

```python
# Example: CodeEval scoring
score = 0.0

# Linting (20%)
if passes_linting:
    score += 0.20

# Security (25%)
if no_vulnerabilities:
    score += 0.25

# Documentation (20%)
doc_coverage = count_docstrings / count_functions
score += 0.20 * doc_coverage

# Type hints (15%)
type_coverage = count_type_hints / count_functions
score += 0.15 * type_coverage

# Conventions (10%)
if follows_conventions:
    score += 0.10

# Complexity (10%)
if complexity <= max_complexity:
    score += 0.10

# Total: 0.0 to 1.0
return score
```

### Partial Credit

Evaluators award partial credit for incomplete compliance:

```python
# Example: Partial credit for coverage
if coverage >= 0.80:
    score += 0.40  # Full credit
elif coverage >= 0.70:
    score += 0.30  # Partial credit
elif coverage >= 0.60:
    score += 0.20  # Minimal credit
else:
    score += 0.0   # No credit
```

---

## Quality Gates

### What is a Quality Gate?

A **quality gate** is a decision point where evaluation results determine if the workflow can proceed.

### Gate Conditions

A stage passes the quality gate if:
1. **Score meets threshold:** `score >= min_score`
2. **No blocking issues:** `len(blocking_issues) == 0`
3. **Agent succeeded:** `agent_result["success"] == True`

### Blocking vs Non-Blocking Issues

**Blocking Issues (Critical):**
- Test coverage < 80%
- Response time > 2s
- Security vulnerabilities
- Agent execution failure

**Non-Blocking Issues (Warnings):**
- Missing docstrings on some functions
- Minor code style violations
- Non-critical console warnings
- Suggestions for improvement

### Example Quality Gate Check

```python
def check_quality_gate(eval_result: Dict[str, Any]) -> bool:
    """Check if evaluation passes quality gate."""

    # Must have passing score
    if not eval_result["passed"]:
        return False

    # Must have no blocking issues
    if len(eval_result["blocking_issues"]) > 0:
        return False

    # Must meet minimum score
    if eval_result["score"] < 0.7:
        return False

    return True
```

### Handling Gate Failures

When a quality gate fails:

1. **Stop workflow** (if `stop_on_failure=True`)
2. **Save checkpoint** at last successful stage
3. **Report issues** to user
4. **Update ADO** with failure details
5. **Provide recommendations** for fixing

**User can then:**
- Review issues and recommendations
- Fix problems manually
- Re-run the failed stage
- Resume workflow from checkpoint

---

## Custom Evaluators

### Use Case: Custom Metric Validation

```python
from ai_sdlc.evals.base_eval import BaseEval
from typing import Any, Dict

class CustomMetricEval(BaseEval):
    """Validates custom business metrics."""

    def __init__(self, min_score: float = 0.7, config: Any = None):
        super().__init__(min_score, config)

        # Custom thresholds
        self.min_data_quality = config.get("min_data_quality", 0.95)
        self.max_error_rate = config.get("max_error_rate", 0.01)

    def evaluate(self, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        output_data = agent_result.get("output_data", {})

        score = 0.0
        issues = []
        recommendations = []

        # Evaluate data quality (50%)
        data_quality = output_data.get("data_quality_score", 0.0)
        if data_quality >= self.min_data_quality:
            score += 0.5
        else:
            issues.append(
                self._create_issue(
                    "high",
                    "data_quality",
                    f"Data quality {data_quality:.2%} below {self.min_data_quality:.2%}",
                    "data_quality_score"
                )
            )
            recommendations.append("Improve data validation and cleaning")

        # Evaluate error rate (50%)
        error_rate = output_data.get("error_rate", 1.0)
        if error_rate <= self.max_error_rate:
            score += 0.5
        else:
            issues.append(
                self._create_issue(
                    "high",
                    "error_rate",
                    f"Error rate {error_rate:.2%} exceeds {self.max_error_rate:.2%}",
                    "error_rate"
                )
            )
            recommendations.append("Add error handling and retry logic")

        passed = score >= self.min_score

        return {
            "passed": passed,
            "score": score,
            "issues": issues,
            "recommendations": recommendations,
            "metrics": {
                "data_quality": data_quality,
                "error_rate": error_rate,
            },
            "blocking_issues": [],
        }
```

### Use Case: External Tool Integration

```python
import subprocess
import json
from ai_sdlc.evals.base_eval import BaseEval

class SonarQubeEval(BaseEval):
    """Evaluates code using SonarQube."""

    def __init__(self, min_score: float = 0.7, config: Any = None):
        super().__init__(min_score, config)
        self.sonar_url = config.get("sonar_url", "http://localhost:9000")
        self.sonar_token = config.get("sonar_token")

    def evaluate(self, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        evidence_files = agent_result.get("evidence_files", [])

        # Find code files
        code_files = [f for f in evidence_files if f.endswith(".py")]

        if not code_files:
            return {
                "passed": False,
                "score": 0.0,
                "issues": [
                    self._create_issue("high", "missing_code", "No code files found", "")
                ],
                "recommendations": ["Ensure code is generated"],
                "metrics": {},
                "blocking_issues": ["No code files found"],
            }

        # Run SonarQube scan
        scan_result = self._run_sonar_scan(code_files)

        # Analyze results
        score = self._calculate_score_from_sonar(scan_result)
        issues = self._extract_issues_from_sonar(scan_result)

        passed = score >= self.min_score

        return {
            "passed": passed,
            "score": score,
            "issues": issues,
            "recommendations": self._generate_recommendations(issues),
            "metrics": scan_result.get("metrics", {}),
            "blocking_issues": [i["message"] for i in issues if i["severity"] == "critical"],
        }

    def _run_sonar_scan(self, code_files: List[str]) -> Dict[str, Any]:
        """Run SonarQube scanner on code files."""
        # Implementation details...
        pass
```

---

## Testing Evaluators

### Unit Testing Evaluators

```python
import pytest
from my_custom_eval import MyCustomEval

class TestMyCustomEval:
    @pytest.fixture
    def evaluator(self):
        return MyCustomEval(min_score=0.7, config={})

    def test_evaluate_success(self, evaluator):
        """Test evaluation with good output."""
        agent_result = {
            "success": True,
            "output_data": {
                "metric_1": 100,
                "metric_2": 0.95,
            },
            "evidence_files": ["report.txt", "data.json"],
        }

        result = evaluator.evaluate(agent_result)

        assert result["passed"] is True
        assert result["score"] >= 0.7
        assert len(result["blocking_issues"]) == 0

    def test_evaluate_failure(self, evaluator):
        """Test evaluation with poor output."""
        agent_result = {
            "success": True,
            "output_data": {
                "metric_1": 10,  # Below threshold
                "metric_2": 0.50,  # Below threshold
            },
            "evidence_files": [],
        }

        result = evaluator.evaluate(agent_result)

        assert result["passed"] is False
        assert result["score"] < 0.7
        assert len(result["issues"]) > 0

    def test_evaluate_agent_failure(self, evaluator):
        """Test evaluation when agent fails."""
        agent_result = {
            "success": False,
            "output_data": {},
            "evidence_files": [],
            "error_message": "Agent failed",
        }

        result = evaluator.evaluate(agent_result)

        assert result["passed"] is False
        assert result["score"] == 0.0
        assert "Agent execution failed" in result["blocking_issues"]
```

### Integration Testing

```python
def test_evaluator_with_real_agent():
    """Test evaluator with real agent output."""
    from my_agent import MyAgent
    from my_custom_eval import MyCustomEval

    # Run agent
    agent = MyAgent(work_item_id="TEST-123", config={}, evidence_path="./test_evidence")
    agent_result = agent.execute({"work_item_title": "Test", "work_item_description": "Test"})

    # Run evaluator
    evaluator = MyCustomEval(min_score=0.7)
    eval_result = evaluator.evaluate(agent_result)

    # Verify evaluation
    assert "passed" in eval_result
    assert "score" in eval_result
    assert "issues" in eval_result
    assert "recommendations" in eval_result
```

---

## Best Practices

### 1. Evaluator Design

- **Single Purpose:** Each evaluator validates one aspect
- **Clear Criteria:** Document what you're evaluating
- **Weighted Scoring:** Assign importance to different criteria
- **Actionable Issues:** Provide specific, fixable problems
- **Helpful Recommendations:** Guide users toward solutions

### 2. Scoring

- **Fair Weights:** More important criteria get higher weights
- **Partial Credit:** Reward progress toward goals
- **Consistent Scale:** Always 0.0 to 1.0
- **Documented Thresholds:** Make pass/fail criteria clear

### 3. Issues and Recommendations

- **Severity Levels:** Use consistent severity classification
- **Location Info:** Tell users where the problem is
- **Fix Suggestions:** Recommend concrete actions
- **Prioritization:** List critical issues first

### 4. Performance

- **Fast Evaluation:** Keep evals under 30 seconds
- **Caching:** Cache expensive operations
- **Incremental:** Only re-evaluate what changed
- **Async:** Use async for I/O-bound evaluations

### 5. Testing

- **Test Pass Cases:** Verify good output passes
- **Test Fail Cases:** Verify bad output fails
- **Test Edge Cases:** Handle missing data gracefully
- **Integration Tests:** Test with real agent output

---

## Reference

### Complete Evaluator Template

```python
"""
Custom Evaluator Template

Replace [EVAL_NAME] with your evaluator name.
Replace [DESCRIPTION] with detailed description.
"""

from typing import Any, Dict, List
from ai_sdlc.evals.base_eval import BaseEval


class [EVAL_NAME](BaseEval):
    """
    [DESCRIPTION]

    Validates [what it validates].

    Scoring:
    - [Criterion 1]: X%
    - [Criterion 2]: Y%
    - [Criterion 3]: Z%
    """

    def __init__(self, min_score: float = 0.7, config: Any = None):
        """
        Initialize [EVAL_NAME].

        Args:
            min_score: Minimum passing score (default: 0.7)
            config: Optional configuration with:
                - [list config options]
        """
        super().__init__(min_score, config)

        # Load configuration
        self.threshold_a = config.get("threshold_a", 100) if config else 100
        self.threshold_b = config.get("threshold_b", 0.8) if config else 0.8

    def evaluate(self, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate agent output against criteria.

        Args:
            agent_result: Agent execution result

        Returns:
            Evaluation result dictionary
        """
        # Initialize evaluation state
        score = 0.0
        issues = []
        recommendations = []
        metrics = {}

        # Check agent success
        if not agent_result.get("success", False):
            return self._failure_result("Agent execution failed")

        # Extract data
        output_data = agent_result.get("output_data", {})
        evidence_files = agent_result.get("evidence_files", [])

        # Evaluate criteria
        score += self._eval_criterion_1(output_data, issues, recommendations)
        score += self._eval_criterion_2(output_data, issues, recommendations)
        score += self._eval_criterion_3(evidence_files, issues, recommendations)

        # Collect metrics
        metrics = {
            "metric_a": output_data.get("metric_a", 0),
            "metric_b": output_data.get("metric_b", 0),
        }

        # Determine blocking issues
        blocking = [i["message"] for i in issues if i["severity"] == "critical"]

        # Final pass/fail
        passed = self._is_passing_score(score) and len(blocking) == 0

        return {
            "passed": passed,
            "score": score,
            "issues": issues,
            "recommendations": recommendations,
            "metrics": metrics,
            "blocking_issues": blocking,
        }

    def _eval_criterion_1(
        self,
        output_data: Dict[str, Any],
        issues: List[Dict],
        recommendations: List[str]
    ) -> float:
        """Evaluate criterion 1 (weight: X%)."""
        score = 0.0
        value = output_data.get("value_1", 0)

        if value >= self.threshold_a:
            score = 0.X  # X% weight
        else:
            issues.append(
                self._create_issue(
                    "high",
                    "criterion_1",
                    f"Value 1 ({value}) below threshold ({self.threshold_a})",
                    "output_data.value_1"
                )
            )
            recommendations.append(f"Increase value_1 to at least {self.threshold_a}")

        return score

    def _failure_result(self, message: str) -> Dict[str, Any]:
        """Return a failed evaluation result."""
        return {
            "passed": False,
            "score": 0.0,
            "issues": [
                self._create_issue("critical", "execution", message, "")
            ],
            "recommendations": ["Fix execution errors"],
            "metrics": {},
            "blocking_issues": [message],
        }
```

---

## Document History

| Version | Date       | Author                | Changes                       |
|---------|------------|-----------------------|-------------------------------|
| 1.0     | 2026-01-17 | AI-SDLC Platform Team | Initial evaluation framework  |

---

**Need Help?**
- Report issues: [GitHub Issues](https://github.com/your-org/ai-sdlc/issues)
- Slack: #ai-sdlc-support
- Email: ai-sdlc-support@yourcompany.com
