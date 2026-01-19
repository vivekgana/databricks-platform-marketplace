# Performance Analyzer Guide

**Document Version:** 1.0
**Prepared by:** AI-SDLC Development Team
**Last Updated:** January 17, 2026 11:37 PM
**Contact:** AI-SDLC Support Team

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Performance Patterns](#performance-patterns)
- [CLI Usage](#cli-usage)
- [Agent Integration](#agent-integration)
- [Analysis Types](#analysis-types)
- [Performance Scoring](#performance-scoring)
- [Optimization Scripts](#optimization-scripts)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## Overview

The Performance Analyzer agent provides comprehensive performance analysis for Apache Spark applications running on Databricks. It analyzes event logs, query execution plans, and performance metrics to identify bottlenecks, detect anti-patterns, and generate actionable optimization recommendations.

### Key Capabilities

- **Event Log Analysis**: Parse Spark event logs to detect data skew, spills, and resource issues
- **Query Plan Analysis**: Examine physical and logical plans for optimization opportunities
- **Metrics Analysis**: Analyze performance metrics against configurable thresholds
- **Bottleneck Detection**: Identify performance bottlenecks using pattern matching
- **Optimization Generation**: Create executable Python scripts with optimization code
- **Comprehensive Reports**: Generate detailed markdown reports with findings

### Use Cases

1. **Performance Troubleshooting**: Identify why jobs are running slowly
2. **Optimization Reviews**: Proactive analysis before production deployment
3. **Capacity Planning**: Understand resource utilization patterns
4. **Cost Optimization**: Detect inefficiencies that waste compute resources
5. **SLA Monitoring**: Ensure performance meets service level agreements

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Performance Analyzer Agent                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Event Log   │  │  Query Plan  │  │   Metrics    │      │
│  │   Analyzer   │  │   Analyzer   │  │   Analyzer   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │  Pattern Matcher │                        │
│                   │  & Issue Detector│                        │
│                   └────────┬────────┘                        │
│                            │                                 │
│         ┌──────────────────┼──────────────────┐              │
│         │                  │                  │              │
│  ┌──────▼──────┐  ┌────────▼────────┐  ┌─────▼─────┐       │
│  │ Performance │  │  Optimization   │  │  Report   │       │
│  │   Scorer    │  │    Generator    │  │ Generator │       │
│  └─────────────┘  └─────────────────┘  └───────────┘       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
  ┌───────────┐      ┌───────────────┐    ┌──────────────┐
  │  Score    │      │ optimize_*.py │    │  report.md   │
  │  0-100    │      │    Script     │    │   Evidence   │
  └───────────┘      └───────────────┘    └──────────────┘
```

## Key Features

### 1. Multi-Source Analysis

The analyzer supports three primary data sources:

#### Event Logs
- Spark event logs from Databricks clusters
- Task-level metrics (duration, memory, shuffle)
- Stage-level aggregations
- Application-level summaries

#### Query Plans
- Physical execution plans
- Logical query plans
- Join strategies
- Predicate pushdown analysis
- Broadcast join detection

#### Performance Metrics
- Response times
- Memory usage
- CPU utilization
- Task success/failure rates
- Data read/write volumes
- Shuffle statistics

### 2. Pattern-Based Detection

The analyzer uses regex patterns to detect known performance issues:

| Pattern Category | Patterns | Severity |
|-----------------|----------|----------|
| Data Issues | Data skew, skewed partitions | High |
| Memory Issues | Spill to disk, OOM errors | Critical |
| Shuffle Issues | Excessive shuffle, large shuffle blocks | High |
| Join Issues | Cartesian products, broadcast failures | Critical |
| Query Issues | Missing predicate pushdown, no partition pruning | Medium |
| Resource Issues | Executor failures, task failures | High |

### 3. Performance Scoring

Performance is scored on a 0-100 scale:

- **90-100**: Excellent - No significant issues
- **70-89**: Good - Minor optimizations possible
- **50-69**: Fair - Moderate issues need attention
- **30-49**: Poor - Significant problems
- **0-29**: Critical - Major performance issues

Scoring factors:
- Issue severity (Critical: -15, High: -10, Medium: -5, Low: -2)
- Resource utilization
- Task failure rates
- Memory spills
- Data skew levels

### 4. Evidence Generation

All analyses generate comprehensive evidence:

1. **Performance Report** (`performance-report.md`)
   - Executive summary
   - Detailed findings
   - Severity breakdowns
   - Recommendations

2. **Optimization Script** (`optimize_<timestamp>.py`)
   - Executable Python code
   - Configuration adjustments
   - Code refactoring suggestions
   - Testing templates

3. **Metrics Summary** (`metrics-summary.json`)
   - Structured data for automation
   - Time-series compatible
   - Dashboard integration ready

## Performance Patterns

### Data Skew

**Detection**: Task duration variance > 3x median

```python
# Pattern Detection
max_duration = 50000ms
median_duration = 5000ms
ratio = max_duration / median_duration  # 10x - SKEWED!
```

**Impact**: Some tasks take 10x longer, wasting resources

**Recommendations**:
- Add salting to skewed keys
- Use `repartition()` with higher partition count
- Consider broadcast joins for smaller tables
- Use `skewJoin` optimization hint

**Example Fix**:
```python
# Before: Skewed join
df1.join(df2, "user_id")

# After: Salted join
from pyspark.sql.functions import concat, lit, rand
df1_salted = df1.withColumn("salt", (rand() * 10).cast("int"))
df2_salted = df2.withColumn("salt", lit(None).cast("int"))
result = df1_salted.join(df2_salted, ["user_id", "salt"])
```

### Memory Spill

**Detection**: Memory bytes spilled > 100MB

```python
# Pattern Detection
spill_amount = task["Metrics"]["Memory Bytes Spilled"]
if spill_amount > 100 * 1024 * 1024:  # 100MB
    # SPILL DETECTED!
```

**Impact**: Disk I/O significantly slower than memory (10-100x)

**Recommendations**:
- Increase executor memory
- Reduce partition size via repartitioning
- Use `.persist()` strategically
- Enable memory compression

**Example Fix**:
```python
# Configuration adjustments
spark.conf.set("spark.executor.memory", "16g")
spark.conf.set("spark.memory.fraction", "0.8")
spark.conf.set("spark.memory.storageFraction", "0.3")

# Code optimization
df.repartition(200)  # Reduce partition size
df.persist(StorageLevel.MEMORY_AND_DISK)  # Spill to disk explicitly
```

### Excessive Shuffle

**Detection**: Shuffle data > 10x input data

```python
# Pattern Detection
shuffle_read = 500GB
input_data = 50GB
ratio = shuffle_read / input_data  # 10x - EXCESSIVE!
```

**Impact**: Network and disk I/O overhead

**Recommendations**:
- Use broadcast joins for small tables
- Filter data earlier in the pipeline
- Reduce shuffle partitions
- Use `coalesce()` to reduce partitions

**Example Fix**:
```python
# Before: Shuffle join
large_df.join(small_df, "key")

# After: Broadcast join
from pyspark.sql.functions import broadcast
large_df.join(broadcast(small_df), "key")

# Reduce shuffle partitions
spark.conf.set("spark.sql.shuffle.partitions", "200")  # Default: 200
```

### Cartesian Product

**Detection**: `CartesianProduct` in physical plan

```python
# Pattern Detection
if "CartesianProduct" in query_plan:
    # CARTESIAN JOIN DETECTED!
```

**Impact**: Exploding data (N × M rows), often unintentional

**Recommendations**:
- Add explicit join condition
- Use broadcast join if intentional
- Verify join logic

**Example Fix**:
```python
# Before: Accidental cartesian
df1.crossJoin(df2)  # N * M rows!

# After: Proper join
df1.join(df2, df1.id == df2.id)
```

### Missing Predicate Pushdown

**Detection**: No filters in scan operations

```python
# Pattern Detection
if "Scan" in plan and "Filter" not in plan:
    # NO PREDICATE PUSHDOWN!
```

**Impact**: Reading unnecessary data from storage

**Recommendations**:
- Add WHERE clauses
- Use partition pruning
- Filter early in the pipeline

**Example Fix**:
```python
# Before: Scan all data
df = spark.read.parquet("s3://bucket/data/")
df.filter(col("date") == "2026-01-01")

# After: Partition pruning
df = spark.read.parquet("s3://bucket/data/date=2026-01-01/")
```

### Large Collect Operations

**Detection**: `CollectLimit` > 10,000 rows

```python
# Pattern Detection
if "CollectLimit" in plan:
    limit = extract_limit(plan)
    if limit > 10000:
        # LARGE COLLECT!
```

**Impact**: OOM errors, driver memory pressure

**Recommendations**:
- Use `.take(n)` instead of `.collect()`
- Sample data with `.sample()`
- Write to storage and read incrementally

**Example Fix**:
```python
# Before: Dangerous collect
all_data = df.collect()  # Could be millions of rows!

# After: Safe alternatives
sample = df.take(100)  # Just 100 rows
df.sample(0.01).show()  # 1% sample
df.write.parquet("output/")  # Write to storage
```

### Task Failures

**Detection**: Failed tasks > 5% of total tasks

```python
# Pattern Detection
failure_rate = failed_tasks / total_tasks
if failure_rate > 0.05:  # 5%
    # HIGH FAILURE RATE!
```

**Impact**: Job retries, wasted resources, eventual failure

**Recommendations**:
- Check for data quality issues
- Increase task retry limits
- Add error handling
- Investigate root cause (memory, network, data corruption)

**Example Fix**:
```python
# Configuration adjustments
spark.conf.set("spark.task.maxFailures", "8")  # Default: 4

# Add error handling
from pyspark.sql.functions import when, col
df_safe = df.withColumn(
    "value_safe",
    when(col("value").isNotNull(), col("value")).otherwise(0)
)
```

## CLI Usage

### Command: analyze-logs

Analyze Spark event logs for performance issues.

**Syntax**:
```bash
python -m ai_sdlc.cli.performance_commands analyze-logs \
  --log-path <path> \
  [--work-item-id <id>] \
  [--output-dir <dir>] \
  [--skew-threshold <float>] \
  [--spill-threshold-mb <int>]
```

**Parameters**:
- `--log-path`: Path to Spark event log (required)
  - Local: `/tmp/eventlog-app-123`
  - DBFS: `dbfs:/databricks/eventlogs/cluster-123/eventlog`
  - S3: `s3://bucket/logs/eventlog`
- `--work-item-id`: Azure DevOps work item ID (optional)
- `--output-dir`: Output directory for evidence (default: `./performance-analysis`)
- `--skew-threshold`: Data skew threshold multiplier (default: 3.0)
- `--spill-threshold-mb`: Memory spill threshold in MB (default: 100)

**Example**:
```bash
python -m ai_sdlc.cli.performance_commands analyze-logs \
  --log-path "dbfs:/databricks/eventlogs/0123-456789-abc123/eventlog" \
  --work-item-id "12345" \
  --skew-threshold 5.0 \
  --spill-threshold-mb 500
```

**Output**:
```
🔍 Analyzing Spark event logs: dbfs:/databricks/eventlogs/0123-456789-abc123/eventlog
   Skew threshold: 5.0x
   Spill threshold: 500MB

======================================================================
📊 Performance Analysis Summary
======================================================================

Performance Score: 65/100
Issues Found:      8
Bottlenecks:       3

🟠 High Severity:   3
   • Data skew detected in stage 2 (max 45s, median 5s)
   • Memory spill to disk: 2.3GB across 150 tasks
   • Excessive shuffle: 50GB for 5GB input

💡 Top Recommendations:
   • Use salting or repartitioning to address data skew
   • Increase executor memory to reduce spills
   • Consider broadcast join to reduce shuffle
   • Optimize partition size for better parallelism

📄 Performance report:     ./performance-analysis/performance-report.md
📄 Optimization script:    ./performance-analysis/optimize_20260117_233702.py
📄 Metrics summary:        ./performance-analysis/metrics-summary.json
```

### Command: analyze-query

Analyze Spark query execution plan.

**Syntax**:
```bash
python -m ai_sdlc.cli.performance_commands analyze-query \
  --query-plan-file <file> \
  [--work-item-id <id>] \
  [--output-dir <dir>]
```

**Parameters**:
- `--query-plan-file`: Path to query plan text file (required)
- `--work-item-id`: Azure DevOps work item ID (optional)
- `--output-dir`: Output directory (default: `./performance-analysis`)

**Getting Query Plans**:
```python
# In Databricks notebook
df = spark.sql("SELECT * FROM table WHERE date = '2026-01-01'")
plan = df._jdf.queryExecution().toString()
with open("/tmp/query_plan.txt", "w") as f:
    f.write(plan)
```

**Example**:
```bash
python -m ai_sdlc.cli.performance_commands analyze-query \
  --query-plan-file "query_plan.txt" \
  --work-item-id "12345"
```

**Output**:
```
🔍 Analyzing query execution plan: query_plan.txt

======================================================================
📊 Query Plan Analysis Summary
======================================================================

Performance Score: 75/100
Issues Found:      4
Optimizations:     6

⚠️  Issues Detected:
   [HIGH] Cartesian product detected in join operation
   💡 Add explicit join condition or use broadcast join

   [MEDIUM] Missing predicate pushdown for partition filter
   💡 Use partition pruning by filtering on partition columns

   [MEDIUM] Large broadcast table (500MB)
   💡 Consider standard shuffle join or increase broadcast threshold

📄 Performance report:     ./performance-analysis/performance-report.md
📄 Optimization script:    ./performance-analysis/optimize_20260117_233702.py
```

### Command: analyze-metrics

Analyze performance metrics from JSON file.

**Syntax**:
```bash
python -m ai_sdlc.cli.performance_commands analyze-metrics \
  --metrics-file <file> \
  [--work-item-id <id>] \
  [--output-dir <dir>] \
  [--response-time-threshold-ms <int>] \
  [--memory-threshold-gb <int>]
```

**Parameters**:
- `--metrics-file`: Path to metrics JSON file (required)
- `--work-item-id`: Azure DevOps work item ID (optional)
- `--output-dir`: Output directory (default: `./performance-analysis`)
- `--response-time-threshold-ms`: Response time threshold (default: 2000ms)
- `--memory-threshold-gb`: Memory threshold (default: 10GB)

**Metrics File Format**:
```json
{
  "response_time_ms": 3500,
  "memory_usage_gb": 12.5,
  "cpu_usage_percent": 85.3,
  "total_tasks": 1000,
  "failed_tasks": 5,
  "data_read_gb": 100.0,
  "data_written_gb": 50.0,
  "shuffle_read_gb": 25.0,
  "shuffle_write_gb": 25.0
}
```

**Example**:
```bash
python -m ai_sdlc.cli.performance_commands analyze-metrics \
  --metrics-file "metrics.json" \
  --work-item-id "12345" \
  --response-time-threshold-ms 1000 \
  --memory-threshold-gb 8
```

### Command: analyze-full

Comprehensive analysis with all data sources.

**Syntax**:
```bash
python -m ai_sdlc.cli.performance_commands analyze-full \
  --log-path <path> \
  [--work-item-id <id>] \
  [--output-dir <dir>] \
  [--query-plan-file <file>] \
  [--metrics-file <file>]
```

**Example**:
```bash
python -m ai_sdlc.cli.performance_commands analyze-full \
  --log-path "dbfs:/databricks/eventlogs/cluster-123/eventlog" \
  --query-plan-file "query_plan.txt" \
  --metrics-file "metrics.json" \
  --work-item-id "12345"
```

## Agent Integration

### Direct Agent Usage

```python
from ai_sdlc.agents.performance_analyzer_agent import PerformanceAnalyzerAgent

# Initialize agent
agent = PerformanceAnalyzerAgent(
    work_item_id="12345",
    evidence_base_path="./performance-analysis"
)

# Analyze event logs
result = agent.execute({
    "analysis_type": "logs",
    "log_path": "dbfs:/databricks/eventlogs/cluster-123/eventlog",
    "thresholds": {
        "skew_threshold": 3.0,
        "spill_threshold_mb": 100
    }
})

if result["success"]:
    data = result["data"]
    print(f"Performance Score: {data['performance_score']}/100")
    print(f"Issues Found: {len(data['issues'])}")

    for issue in data["issues"]:
        print(f"[{issue['severity'].upper()}] {issue['description']}")
        print(f"  → {issue['recommendation']}")
```

### Workflow Orchestration Integration

The Performance Analyzer can be integrated into the workflow orchestration:

```python
# In workflow configuration
from ai_sdlc.orchestration.state_machine import WorkflowStage, StageConfig

STAGE_CONFIGS = {
    WorkflowStage.PERFORMANCE_ANALYSIS: StageConfig(
        stage=WorkflowStage.PERFORMANCE_ANALYSIS,
        ado_state=ADOState.TESTING,
        agent_class_name="PerformanceAnalyzerAgent",
        eval_class_name="PerformanceEval",
        evidence_types=[
            "performance-report.md",
            "optimization-script.py",
            "metrics-summary.json"
        ],
        min_eval_score=0.7,
        timeout_minutes=30,
        description="Analyze Spark performance and identify optimizations",
        dependencies=[WorkflowStage.INTEGRATION_TESTING],
    )
}
```

## Analysis Types

### 1. Event Log Analysis

**Purpose**: Analyze Spark event logs for task-level performance issues

**Input Data**:
```python
{
    "analysis_type": "logs",
    "log_path": "dbfs:/path/to/eventlog",
    "thresholds": {
        "skew_threshold": 3.0,  # Task duration variance threshold
        "spill_threshold_mb": 100,  # Memory spill threshold
        "task_failure_threshold": 0.05  # 5% failure rate
    }
}
```

**Detected Issues**:
- Data skew across partitions
- Memory spills to disk
- Task failures and retries
- Stage execution times
- Executor resource usage

**Generated Evidence**:
- Task duration histograms
- Skew analysis charts
- Stage timeline visualization
- Resource utilization graphs

### 2. Query Plan Analysis

**Purpose**: Analyze execution plans for optimization opportunities

**Input Data**:
```python
{
    "analysis_type": "query_plan",
    "query_plan": "== Physical Plan ==\n..."
}
```

**Detected Issues**:
- Cartesian products
- Missing predicate pushdown
- Large broadcast tables
- Inefficient join strategies
- Missing partition pruning

**Generated Evidence**:
- Annotated query plan
- Join strategy recommendations
- Optimization opportunities

### 3. Metrics Analysis

**Purpose**: Analyze performance metrics against thresholds

**Input Data**:
```python
{
    "analysis_type": "metrics",
    "metrics": {
        "response_time_ms": 3500,
        "memory_usage_gb": 12.5,
        "cpu_usage_percent": 85.3,
        "total_tasks": 1000,
        "failed_tasks": 5
    },
    "thresholds": {
        "response_time_threshold_ms": 2000,
        "memory_threshold_gb": 10,
        "cpu_threshold_percent": 80,
        "failure_rate_threshold": 0.05
    }
}
```

**Detected Issues**:
- High response times
- Memory pressure
- CPU bottlenecks
- High task failure rates

**Generated Evidence**:
- Metrics comparison chart
- Threshold violations
- Trend analysis

### 4. Comprehensive Analysis

**Purpose**: Multi-source analysis for complete picture

**Input Data**:
```python
{
    "analysis_type": "full",
    "log_path": "dbfs:/path/to/eventlog",
    "query_plan": "== Physical Plan ==\n...",
    "metrics": {...}
}
```

**Benefits**:
- Cross-reference findings
- Root cause analysis
- Comprehensive recommendations
- Prioritized action items

## Performance Scoring

### Scoring Algorithm

```python
def calculate_performance_score(issues, metrics):
    base_score = 100

    # Deduct points for issues by severity
    for issue in issues:
        if issue["severity"] == "critical":
            base_score -= 15
        elif issue["severity"] == "high":
            base_score -= 10
        elif issue["severity"] == "medium":
            base_score -= 5
        elif issue["severity"] == "low":
            base_score -= 2

    # Additional deductions for metrics
    if metrics.get("task_failure_rate", 0) > 0.05:
        base_score -= 10

    if metrics.get("memory_spill_gb", 0) > 1.0:
        base_score -= 5

    # Cap at 0-100 range
    return max(0, min(100, base_score))
```

### Score Interpretation

| Score Range | Rating | Description | Action Required |
|-------------|--------|-------------|-----------------|
| 90-100 | Excellent | No significant issues | Monitor only |
| 70-89 | Good | Minor optimizations possible | Optional improvements |
| 50-69 | Fair | Moderate issues | Recommended optimizations |
| 30-49 | Poor | Significant problems | Required optimizations |
| 0-29 | Critical | Major issues | Immediate action |

### Quality Gates

Performance analysis can block workflow progression:

```python
# In evaluation
class PerformanceEval(BaseEval):
    def evaluate(self, agent_result):
        score = agent_result["data"]["performance_score"]
        critical_issues = [
            i for i in agent_result["data"]["issues"]
            if i["severity"] == "critical"
        ]

        # Block if critical issues or score too low
        passed = score >= 50 and len(critical_issues) == 0

        return EvalResult(
            stage="performance_analysis",
            passed=passed,
            score=score / 100.0,
            issues=[],
            blocking_issues=critical_issues
        )
```

## Optimization Scripts

The agent generates executable Python scripts with optimization code:

### Script Structure

```python
"""
Spark Performance Optimization Script
Generated: 2026-01-17 23:37:02
Performance Score: 65/100

This script contains optimization recommendations based on performance analysis.
Review and test each optimization before applying to production.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *

def optimize_spark_config(spark):
    """Apply optimized Spark configurations."""
    # Memory optimization
    spark.conf.set("spark.executor.memory", "16g")
    spark.conf.set("spark.memory.fraction", "0.8")
    spark.conf.set("spark.memory.storageFraction", "0.3")

    # Shuffle optimization
    spark.conf.set("spark.sql.shuffle.partitions", "200")
    spark.conf.set("spark.sql.adaptive.enabled", "true")
    spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

    # Broadcast optimization
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")  # 10MB

def optimize_data_skew(df, skew_column):
    """Add salting to address data skew."""
    from pyspark.sql.functions import concat, lit, rand

    # Add salt column
    df_salted = df.withColumn(
        "salt",
        (rand() * 10).cast("int")
    )

    return df_salted

def optimize_memory_spill(df):
    """Reduce memory spills through repartitioning."""
    # Increase partition count to reduce partition size
    num_partitions = df.rdd.getNumPartitions() * 2
    return df.repartition(num_partitions)

def optimize_shuffle(large_df, small_df, join_key):
    """Use broadcast join to reduce shuffle."""
    from pyspark.sql.functions import broadcast

    # Broadcast small table
    return large_df.join(broadcast(small_df), join_key)

# Main optimization function
def apply_optimizations(spark, df):
    """Apply all recommended optimizations."""
    # 1. Optimize Spark config
    optimize_spark_config(spark)

    # 2. Address data skew
    df = optimize_data_skew(df, "user_id")

    # 3. Reduce memory spills
    df = optimize_memory_spill(df)

    # 4. Cache frequently accessed data
    df.persist()

    return df

if __name__ == "__main__":
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("PerformanceOptimization") \
        .getOrCreate()

    # Apply optimizations
    # df = spark.read.parquet("s3://bucket/data/")
    # df_optimized = apply_optimizations(spark, df)
    # df_optimized.write.parquet("s3://bucket/data_optimized/")

    print("✅ Optimization script ready")
    print("Review the functions above and integrate into your pipeline")
```

### Using Optimization Scripts

1. **Review**: Read through all recommendations
2. **Test**: Apply optimizations in development environment
3. **Measure**: Compare performance before and after
4. **Iterate**: Adjust parameters based on results
5. **Deploy**: Roll out to production incrementally

## Best Practices

### 1. Regular Performance Reviews

- Analyze performance after every major change
- Establish performance baselines
- Track metrics over time
- Set up automated monitoring

### 2. Proactive Optimization

- Review query plans before execution
- Profile queries in development
- Test with production-like data volumes
- Use explain() to understand execution

### 3. Evidence Collection

- Capture event logs for all production jobs
- Store query plans with job metadata
- Collect metrics at regular intervals
- Link evidence to work items

### 4. Threshold Configuration

Customize thresholds based on your requirements:

```python
# Conservative thresholds (catch more issues)
thresholds = {
    "skew_threshold": 2.0,  # 2x variance
    "spill_threshold_mb": 50,  # 50MB
    "response_time_threshold_ms": 1000,  # 1s
}

# Relaxed thresholds (fewer false positives)
thresholds = {
    "skew_threshold": 5.0,  # 5x variance
    "spill_threshold_mb": 500,  # 500MB
    "response_time_threshold_ms": 5000,  # 5s
}
```

### 5. Automation

Integrate into CI/CD pipeline:

```yaml
# Azure DevOps pipeline
- task: PythonScript@0
  displayName: 'Analyze Performance'
  inputs:
    scriptSource: 'inline'
    script: |
      python -m ai_sdlc.cli.performance_commands analyze-logs \
        --log-path "$(EventLogPath)" \
        --work-item-id "$(System.WorkItemId)" \
        --output-dir "$(Build.ArtifactStagingDirectory)/performance"

- task: PublishBuildArtifacts@1
  displayName: 'Publish Performance Report'
  inputs:
    PathtoPublish: '$(Build.ArtifactStagingDirectory)/performance'
    ArtifactName: 'performance-analysis'
```

## Troubleshooting

### Issue: Event log file not found

**Symptoms**:
```
❌ Analysis failed: Event log file not found: dbfs:/path/to/eventlog
```

**Solutions**:
1. Verify path with `databricks fs ls dbfs:/databricks/eventlogs/`
2. Check cluster ID in path
3. Ensure log delivery is enabled: `spark.conf.set("spark.eventLog.enabled", "true")`
4. Wait for logs to be written (can take 5-10 minutes after job completion)

### Issue: Query plan is empty

**Symptoms**:
```
Performance Score: 100/100
Issues Found: 0
```

**Solutions**:
1. Ensure you captured the physical plan: `df.explain("extended")`
2. Save full output including "== Physical Plan ==" header
3. Check that query actually executed (lazy evaluation)

### Issue: Low performance score with no obvious issues

**Symptoms**:
```
Performance Score: 45/100
Issues Found: 2 (both low severity)
```

**Solutions**:
1. Check metrics for threshold violations
2. Review task failure rates
3. Look for accumulated low-severity issues
4. Consider adjusting scoring thresholds

### Issue: Optimization script doesn't apply

**Symptoms**: Script runs but performance doesn't improve

**Solutions**:
1. Verify changes actually applied: `spark.conf.get("spark.executor.memory")`
2. Check if cluster overrides configurations
3. Test with smaller dataset first
4. Measure before and after metrics

### Issue: Memory errors during analysis

**Symptoms**:
```
MemoryError: Unable to allocate array
```

**Solutions**:
1. Analyze in smaller chunks
2. Increase analyzer process memory
3. Use sampling for large logs
4. Process on Databricks cluster instead of local machine

## Examples

### Example 1: Analyze Slow Job

**Scenario**: Production job taking 2 hours instead of 30 minutes

**Steps**:

1. Get event log path:
```python
# In Databricks notebook
cluster_id = "0123-456789-abc123"
log_path = f"dbfs:/databricks/eventlogs/{cluster_id}/eventlog"
```

2. Run analysis:
```bash
python -m ai_sdlc.cli.performance_commands analyze-logs \
  --log-path "dbfs:/databricks/eventlogs/0123-456789-abc123/eventlog" \
  --work-item-id "PBI-12345"
```

3. Review findings:
```
Performance Score: 35/100
Issues Found: 12

🔴 Critical Issues: 2
   • Cartesian product causing data explosion
   • OOM errors in executor (5GB spill to disk)

🟠 High Severity: 4
   • Data skew: max task 45min, median 2min (22x)
   • Excessive shuffle: 500GB for 50GB input
```

4. Apply optimizations:
```python
# From generated optimize_*.py script
spark.conf.set("spark.executor.memory", "32g")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

# Fix cartesian join
# Before: df1.join(df2, how="cross")
# After: df1.join(df2, df1.id == df2.id)

# Address data skew with salting
df1 = df1.withColumn("salt", (rand() * 20).cast("int"))
df2 = df2.withColumn("salt", lit(1))  # Replicate
```

5. Re-analyze:
```
Performance Score: 85/100
Issues Found: 3 (all low severity)
Job Duration: 28 minutes ✅
```

### Example 2: Pre-Production Performance Review

**Scenario**: Validate new feature before production deployment

**Steps**:

1. Run comprehensive analysis:
```bash
python -m ai_sdlc.cli.performance_commands analyze-full \
  --log-path "dbfs:/test-logs/eventlog" \
  --query-plan-file "query_plan.txt" \
  --metrics-file "metrics.json" \
  --work-item-id "PBI-67890"
```

2. Review score:
```
Performance Score: 72/100

🟡 Medium Severity: 5
   • Missing partition pruning on date column
   • Broadcast table size (200MB) near threshold
   • No caching for repeated DataFrame access
```

3. Apply recommendations before production:
```python
# Add partition pruning
df = spark.read.parquet("s3://data/") \
    .filter(col("date").between("2026-01-01", "2026-01-31"))

# Increase broadcast threshold
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "250m")

# Cache frequently used data
dim_customers.cache()
```

4. Update work item with evidence:
```python
from ai_sdlc.integrations.ado_integration import update_work_item_with_evidence

update_work_item_with_evidence(
    work_item_id="PBI-67890",
    evidence_dir="./performance-analysis",
    comment="Performance analysis completed. Score: 72/100. "
            "Applied 3 optimizations before deployment."
)
```

### Example 3: Troubleshoot OOM Errors

**Scenario**: Job failing with "Container killed by YARN for exceeding memory limits"

**Steps**:

1. Analyze event log for memory patterns:
```bash
python -m ai_sdlc.cli.performance_commands analyze-logs \
  --log-path "dbfs:/failed-job/eventlog" \
  --spill-threshold-mb 50 \
  --work-item-id "BUG-11111"
```

2. Review memory issues:
```
🔴 Critical Issues: 1
   • Executor OOM: 15GB spill across 200 tasks

🟠 High Severity: 2
   • Large partition size: 8GB per partition
   • Collect operation on 50M rows
```

3. Fix memory issues:
```python
# Increase executor memory
spark.conf.set("spark.executor.memory", "32g")
spark.conf.set("spark.executor.memoryOverhead", "8g")

# Reduce partition size
df = df.repartition(400)  # Was 200, now 400

# Remove dangerous collect
# Before: results = df.collect()
# After: df.write.parquet("s3://output/results/")
```

4. Validate fix:
```bash
# Re-run with increased memory
# Check performance score improves
```

### Example 4: Cost Optimization Analysis

**Scenario**: Reduce Databricks costs by optimizing resource usage

**Steps**:

1. Analyze resource utilization:
```bash
python -m ai_sdlc.cli.performance_commands analyze-metrics \
  --metrics-file "monthly_metrics.json" \
  --work-item-id "TASK-99999"
```

2. Identify waste:
```
📊 Resource Utilization:
   Average CPU: 35% (Overprovisioned!)
   Memory Usage: 40% (Overprovisioned!)
   Idle Time: 45% of cluster runtime
```

3. Right-size cluster:
```python
# Old cluster config
cluster_config = {
    "node_type_id": "Standard_D32_v3",  # 32 cores, 128GB
    "num_workers": 10
}

# Optimized cluster config
cluster_config = {
    "node_type_id": "Standard_D16_v3",  # 16 cores, 64GB
    "num_workers": 6,
    "autoscale": {
        "min_workers": 2,
        "max_workers": 6
    }
}
```

4. Measure savings:
```
Cost Before: $500/day
Cost After:  $200/day
Savings:     $300/day (60% reduction)
```

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-17 | AI-SDLC Team | Initial version - comprehensive performance analyzer guide |
