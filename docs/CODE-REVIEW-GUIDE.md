# PySpark Code Review Guide

**Document Version:** 1.0
**Last Updated:** 2026-01-17 23:09:43
**Prepared by:** AI-SDLC Platform Team

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Integration with Workflow](#integration-with-workflow)
4. [Code Review Agent](#code-review-agent)
5. [Security Checks](#security-checks)
6. [Performance Checks](#performance-checks)
7. [Logic and Edge Case Checks](#logic-and-edge-case-checks)
8. [CLI Usage](#cli-usage)
9. [Evaluation Criteria](#evaluation-criteria)
10. [Examples](#examples)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

---

## Overview

The AI-SDLC platform includes a comprehensive **PySpark Code Review** system that automatically analyzes code for:

- **Security vulnerabilities** (SQL injection, command injection, eval usage, etc.)
- **Performance anti-patterns** (collect(), cartesian joins, RDD operations, etc.)
- **Logic errors and edge cases** (null handling, division by zero, schema inference, etc.)
- **Best practices violations** (missing docstrings, type hints, etc.)

The code review runs **automatically before unit testing** in the workflow, ensuring code quality before proceeding with testing and deployment.

### Key Benefits

✅ **Automated Security Scanning** - Detects SQL injection, command injection, and other vulnerabilities
✅ **Performance Optimization** - Identifies PySpark anti-patterns that cause slowdowns
✅ **Quality Gates** - Blocks workflow if critical issues are found
✅ **Actionable Recommendations** - Provides specific fixes for each issue
✅ **Workflow Integration** - Seamlessly integrates into CI/CD pipeline

---

## Features

### Comprehensive Analysis

The code review agent analyzes:

1. **Security Vulnerabilities** (Critical/High severity)
   - SQL injection via string concatenation
   - Command injection (os.system, os.popen, etc.)
   - Use of eval() and exec()
   - Unsafe pickle deserialization
   - Path traversal vulnerabilities

2. **Performance Anti-Patterns** (Medium/Low severity)
   - collect() usage (driver OOM risk)
   - UDFs without type hints (slower execution)
   - RDD operations instead of DataFrame API
   - Cartesian joins (N×M explosion)
   - Multiple filter().count() calls

3. **Logic and Edge Cases** (Medium severity)
   - Null value handling in filters
   - Division by zero risks
   - Empty DataFrame checks using count()
   - Schema inference (slow and error-prone)

4. **Best Practices** (Low severity)
   - Missing docstrings
   - Missing type hints
   - Code documentation

### Severity Scoring

Each finding has a severity level that contributes to an overall score:

| Severity | Points | Impact |
|----------|--------|--------|
| Critical | 10 | Security vulnerabilities, data loss risks |
| High | 5 | Performance issues, major bugs |
| Medium | 2 | Logic errors, edge case handling |
| Low | 1 | Best practices, maintainability |

**Quality Gate:** Total score must be < 50 to pass (configurable)

---

## Integration with Workflow

### Workflow Stage Order

The code review stage is integrated into the workflow orchestration:

```
1. Planning
2. Code Generation
3. Code Review ← NEW STAGE
4. Unit Testing
5. QA Testing
6. Integration Testing
7. Performance Testing
8. Evidence Collection
```

### Automatic Execution

Code review runs automatically:
- **After code generation**
- **Before unit testing**
- **Blocks workflow if critical issues found**

### Configuration

In `ai_sdlc/orchestration/state_machine.py`:

```python
WorkflowStage.CODE_REVIEW: StageConfig(
    stage=WorkflowStage.CODE_REVIEW,
    ado_state=ADOState.IN_DEVELOPMENT,
    agent_class_name="CodeReviewAgent",
    eval_class_name="CodeReviewEval",
    evidence_types=["code-review-report.md", "code-review-summary.json"],
    min_eval_score=0.7,
    timeout_minutes=15,
    description="Review code for security, logic, and performance issues",
    dependencies=[WorkflowStage.CODE_GENERATION],
),
```

---

## Code Review Agent

### Architecture

```python
class CodeReviewAgent(BaseAgent):
    """
    Agent for reviewing PySpark code quality, security, and optimization.
    """

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive code review.

        Args:
            input_data: Dictionary with:
                - code_files: List of file paths to review
                - severity_threshold: Minimum severity to report
                - review_type: security, performance, logic, or all

        Returns:
            Result with findings, severity score, and recommendations
        """
```

### Review Types

| Type | Description | Use Case |
|------|-------------|----------|
| `security` | Security vulnerabilities only | Pre-deployment security audit |
| `performance` | Performance anti-patterns only | Performance optimization |
| `logic` | Logic errors and edge cases | Code correctness validation |
| `all` | All checks (default) | Comprehensive review |

---

## Security Checks

### 1. SQL Injection

**Pattern Detected:**
```python
query = "SELECT * FROM users WHERE name = '" + user_input + "'"
```

**Severity:** Critical
**Recommendation:** Use parameterized queries or sanitize input

**Fixed Code:**
```python
# Option 1: Use DataFrame API (safe)
df.filter(col("name") == user_input)

# Option 2: Use parameterized queries
query = "SELECT * FROM users WHERE name = :name"
df = spark.sql(query, {"name": user_input})
```

---

### 2. Command Injection

**Pattern Detected:**
```python
os.system("ls " + user_directory)
os.popen("cat " + filename)
```

**Severity:** Critical
**Recommendation:** Avoid executing shell commands with user input

**Fixed Code:**
```python
# Use safe Python alternatives
import pathlib
pathlib.Path(user_directory).glob("*")
```

---

### 3. Eval/Exec Usage

**Pattern Detected:**
```python
result = eval(user_expression)
exec(user_code)
```

**Severity:** Critical
**Recommendation:** Replace eval() with safer alternatives

**Fixed Code:**
```python
# Use ast.literal_eval for safe evaluation of literals
import ast
result = ast.literal_eval(user_expression)  # Only works for literals
```

---

### 4. Pickle Deserialization

**Pattern Detected:**
```python
data = pickle.loads(untrusted_data)
```

**Severity:** High
**Recommendation:** Use JSON or other safe serialization

**Fixed Code:**
```python
import json
data = json.loads(untrusted_data)
```

---

## Performance Checks

### 1. collect() Usage

**Pattern Detected:**
```python
data = df.collect()  # Brings ALL data to driver
```

**Severity:** Medium
**Recommendation:** Use take(n) or persist() with actions

**Fixed Code:**
```python
# Option 1: Take only what you need
sample = df.take(100)

# Option 2: Process distributed
df.write.parquet("/output/path")

# Option 3: Use aggregations
count = df.count()
```

---

### 2. UDF Without Type Hint

**Pattern Detected:**
```python
@udf
def process(value):
    return value.upper()
```

**Severity:** Low
**Recommendation:** Specify return type for better performance

**Fixed Code:**
```python
from pyspark.sql.types import StringType

@udf(returnType=StringType())
def process(value):
    return value.upper()
```

---

### 3. RDD Operations

**Pattern Detected:**
```python
rdd = df.rdd.map(lambda x: x[0] + x[1])
```

**Severity:** Medium
**Recommendation:** Use DataFrame/Dataset APIs

**Fixed Code:**
```python
# Use DataFrame API (optimized)
result = df.withColumn("sum", col("col1") + col("col2"))
```

---

### 4. Cartesian Join

**Pattern Detected:**
```python
result = df1.crossJoin(df2)  # N×M rows
```

**Severity:** High
**Recommendation:** Add join condition or filter

**Fixed Code:**
```python
# Add proper join condition
result = df1.join(df2, df1.id == df2.id)

# Or filter before join
filtered_df2 = df2.filter(col("active") == True)
result = df1.join(filtered_df2, "id")
```

---

## Logic and Edge Case Checks

### 1. Null Handling

**Pattern Detected:**
```python
df.filter(col("name") == some_value)
```

**Severity:** Medium
**Recommendation:** Use isNull(), isNotNull(), or eqNullSafe()

**Fixed Code:**
```python
# Handle nulls explicitly
df.filter(col("name").isNotNull() & (col("name") == some_value))

# Or use null-safe equality
df.filter(col("name").eqNullSafe(some_value))
```

---

### 2. Division by Zero

**Pattern Detected:**
```python
df.withColumn("ratio", col("numerator") / col("denominator"))
```

**Severity:** Medium
**Recommendation:** Add null/zero check

**Fixed Code:**
```python
from pyspark.sql.functions import when

df.withColumn(
    "ratio",
    when(col("denominator") != 0, col("numerator") / col("denominator"))
    .otherwise(None)
)
```

---

### 3. Empty DataFrame Check

**Pattern Detected:**
```python
if df.count() == 0:  # Expensive!
    print("Empty")
```

**Severity:** Low
**Recommendation:** Use df.head(1) or df.isEmpty()

**Fixed Code:**
```python
# Much faster
if df.head(1) == []:
    print("Empty")

# Or in Spark 3.3+
if df.isEmpty():
    print("Empty")
```

---

### 4. Schema Inference

**Pattern Detected:**
```python
df = spark.read.json("data.json")  # Infers schema by scanning
```

**Severity:** Low
**Recommendation:** Define explicit schema

**Fixed Code:**
```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True),
])

df = spark.read.schema(schema).json("data.json")
```

---

## CLI Usage

### Review Specific Files

```bash
# Review specific files
python -m ai_sdlc.cli.code_review_commands review \
  --files src/main.py src/utils.py

# Review with severity threshold
python -m ai_sdlc.cli.code_review_commands review \
  --files src/*.py \
  --severity high

# Review only security issues
python -m ai_sdlc.cli.code_review_commands review \
  --files src/*.py \
  --type security
```

### Review PR Code

```bash
# Review code for PR (finds all Python files)
python -m ai_sdlc.cli.code_review_commands review-pr 6340168

# Review with high severity threshold
python -m ai_sdlc.cli.code_review_commands review-pr 6340168 --severity high
```

### CLI Options

```bash
Options:
  --files               Files to review (space-separated)
  --work-item-id        Work item ID (optional)
  --severity            Minimum severity: low, medium, high, critical (default: low)
  --type                Review type: security, performance, logic, all (default: all)
  --output-dir          Output directory for reports (default: ./code-review-results)
```

---

## Evaluation Criteria

### Quality Gates

The Code Review Evaluator enforces these quality gates:

| Check | Threshold | Blocking | Description |
|-------|-----------|----------|-------------|
| Critical Issues | = 0 | ✅ Yes | No critical security vulnerabilities allowed |
| Severity Score | < 50 | ✅ Yes | Overall code quality must be acceptable |
| High Issues | < 5 | ⚠️ Warning | Recommended to fix before PR |
| Files Reviewed | > 0 | ✅ Yes | At least one file must be reviewed |

### Scoring Example

```
Critical issues: 2 × 10 = 20 points
High issues:     3 × 5  = 15 points
Medium issues:   4 × 2  = 8 points
Low issues:      5 × 1  = 5 points
─────────────────────────────────
Total Score:              48 points

Status: ✅ PASSED (< 50)
```

---

## Examples

### Example 1: Review Generated Code

```python
from ai_sdlc.agents.code_review_agent import CodeReviewAgent

agent = CodeReviewAgent(work_item_id="6340168")

result = agent.execute({
    "code_files": [
        "./generated/audit_service.py",
        "./generated/data_processor.py",
    ],
    "review_type": "all",
    "severity_threshold": "low",
})

print(f"Files reviewed: {result['data']['files_reviewed']}")
print(f"Total findings: {result['data']['total_findings']}")
print(f"Severity score: {result['data']['severity_score']}")
print(f"Passed: {result['data']['passed']}")
```

### Example 2: Run Evaluation

```python
from ai_sdlc.evals.code_review_eval import CodeReviewEval

evaluator = CodeReviewEval(min_score=0.7)
eval_result = evaluator.evaluate(agent_result)

if not eval_result["passed"]:
    print("Code review failed!")
    for issue in eval_result["issues"]:
        print(f"  [{issue.severity}] {issue.description}")

    print("\nRecommendations:")
    for rec in eval_result["recommendations"]:
        print(f"  • {rec}")
```

### Example 3: Workflow Integration

```python
from ai_sdlc.orchestration import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator(work_item_id="6340168")

# Code review runs automatically between CODE_GENERATION and UNIT_TESTING
result = orchestrator.run_workflow(work_item_id="6340168")

# Check code review stage
code_review_result = result["stages"]["code_review"]
if not code_review_result["passed"]:
    print("⚠️ Code review failed - fix issues before proceeding")
```

---

## Best Practices

### 1. Run Early and Often

- Run code review immediately after code generation
- Re-run after fixing issues
- Include in CI/CD pipeline

### 2. Fix Critical Issues First

Priority order:
1. **Critical** - Security vulnerabilities (blocking)
2. **High** - Performance issues and major bugs
3. **Medium** - Logic errors and edge cases
4. **Low** - Best practices and maintainability

### 3. Use Appropriate Severity Threshold

| Environment | Threshold | Rationale |
|-------------|-----------|-----------|
| Development | `low` | Catch all issues early |
| PR Review | `medium` | Focus on important issues |
| Production | `high` | Only critical/high severity |

### 4. Review Type Selection

| Scenario | Review Type | Why |
|----------|-------------|-----|
| Pre-deployment | `security` | Security audit before production |
| Performance tuning | `performance` | Optimize slow operations |
| Code correctness | `logic` | Validate business logic |
| General review | `all` | Comprehensive analysis |

### 5. Address Recommendations

Each finding includes:
- **Description** - What the issue is
- **Severity** - How critical it is
- **Recommendation** - How to fix it
- **Code snippet** - Context around the issue

Follow recommendations to fix issues effectively.

---

## Troubleshooting

### Issue 1: "No code files provided for review"

**Problem:** No files passed to review

**Solution:**
```bash
# Ensure files exist
ls -la generated/*.py

# Pass correct file paths
python -m ai_sdlc.cli.code_review_commands review \
  --files generated/service.py generated/utils.py
```

---

### Issue 2: High Severity Score

**Problem:** Severity score exceeds 50, blocking workflow

**Solution:**
1. Review findings in `code-review-summary.json`
2. Fix critical issues first (10 points each)
3. Address high severity issues (5 points each)
4. Re-run review after fixes

```bash
# View detailed findings
cat ./code-review-results/code-review-summary.json | jq '.findings'

# Fix issues and re-run
python -m ai_sdlc.cli.code_review_commands review --files fixed_code.py
```

---

### Issue 3: False Positives

**Problem:** Review flags valid code as problematic

**Solution:**
1. **Adjust severity threshold** - Use `--severity high` to ignore low-priority issues
2. **Review specific categories** - Use `--type security` to focus on security only
3. **Update patterns** - Contribute improved patterns to code review agent

---

### Issue 4: Missing Findings

**Problem:** Known issues not detected

**Solution:**
1. **Check review type** - Ensure using `--type all`
2. **Verify severity threshold** - Use `--severity low` to see all findings
3. **Add custom patterns** - Extend `SECURITY_PATTERNS`, `PERFORMANCE_PATTERNS`, or `LOGIC_PATTERNS` in `code_review_agent.py`

---

### Issue 5: Slow Review

**Problem:** Code review takes too long

**Solution:**
```python
# Review only changed files
import subprocess
changed_files = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD~1"],
    text=True
).strip().split("\n")

python_files = [f for f in changed_files if f.endswith(".py")]

# Review only changed Python files
agent.execute({"code_files": python_files})
```

---

## Advanced Usage

### Custom Patterns

Add custom security patterns:

```python
# In code_review_agent.py
SECURITY_PATTERNS = {
    # ... existing patterns ...

    "custom_vulnerability": {
        "pattern": r'dangerous_function\(',
        "severity": "critical",
        "description": "Use of dangerous_function is not allowed",
        "recommendation": "Replace with safe_alternative()",
    },
}
```

### Programmatic Access

```python
from ai_sdlc.agents.code_review_agent import CodeReviewAgent
from ai_sdlc.evals.code_review_eval import CodeReviewEval

def review_and_block(files: List[str]) -> bool:
    """
    Review files and return True if passed, False otherwise.
    """
    agent = CodeReviewAgent(work_item_id="custom")
    result = agent.execute({"code_files": files})

    evaluator = CodeReviewEval(min_score=0.7)
    eval_result = evaluator.evaluate(result)

    return eval_result["passed"]

# Use in CI/CD
if not review_and_block(["src/main.py"]):
    sys.exit(1)  # Fail CI/CD
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-17 | AI-SDLC Platform Team | Initial documentation for code review feature |

---

**For questions or support:**
- Slack: #ai-sdlc-support
- Documentation: `docs/` directory
- Tests: `tests/unit/test_code_review.py`
