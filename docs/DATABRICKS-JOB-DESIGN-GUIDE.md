# Databricks Job Design Guide

**Document Version:** 1.0
**Last Updated:** 2026-01-17 23:18:11
**Prepared by:** AI-SDLC Platform Team

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Job Design Agent](#job-design-agent)
5. [Cluster Configurations](#cluster-configurations)
6. [Task Types](#task-types)
7. [Workflow Dependencies](#workflow-dependencies)
8. [CLI Usage](#cli-usage)
9. [Best Practices](#best-practices)
10. [Examples](#examples)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The AI-SDLC platform includes a **Databricks Job Design Agent** that automatically generates optimized Databricks job configurations from requirements. The agent creates production-ready job definitions with:

- **Multiple task types** (notebook, Python wheel, JAR, SQL, DLT)
- **Auto-scaling cluster configurations** with cost optimization
- **Workflow dependencies** and orchestration
- **Best practices** for performance and reliability
- **Email notifications** and scheduling

### Key Benefits

✅ **Automated Configuration** - Generate complete job definitions from simple task specs
✅ **Cost Optimized** - Spot instances, auto-scaling, Photon runtime
✅ **Production Ready** - Retry logic, timeouts, notifications built-in
✅ **Multi-Task Workflows** - Complex dependencies and orchestration
✅ **Validation** - Automatic checks for circular dependencies and misconfigurations

---

## Features

### Comprehensive Job Design

The job design agent creates complete job configurations including:

1. **Task Definitions**
   - Notebook tasks with parameters
   - Python wheel tasks with entry points
   - Spark JAR tasks with main classes
   - SQL tasks with warehouse integration
   - DLT pipeline tasks

2. **Cluster Management**
   - Pre-configured cluster size presets (small, medium, large, xlarge)
   - Auto-scaling for cost optimization
   - Spot instances with fallback to on-demand
   - Photon runtime for performance
   - Custom Spark configurations

3. **Workflow Orchestration**
   - Task dependencies (DAG)
   - Circular dependency detection
   - Parallel and sequential execution
   - Max concurrent runs control

4. **Reliability Features**
   - Automatic retries with configurable attempts
   - Timeout controls at job and task level
   - Min retry intervals
   - Retry on timeout

5. **Notifications and Scheduling**
   - Email notifications (on start, success, failure)
   - Quartz cron scheduling
   - Timezone configuration
   - Pause/unpause capability

6. **Validation and Documentation**
   - Configuration validation before creation
   - Comprehensive job documentation
   - Workflow diagrams
   - Best practices checklist

---

## Architecture

### Agent Design

```python
class DatabricksJobDesignAgent(BaseAgent):
    """
    Agent for designing Databricks job configurations.

    Generates:
    - Task configurations
    - Cluster specifications
    - Workflow dependencies
    - Schedules and notifications
    """
```

### Cluster Presets

| Preset | Node Type | Workers (Min-Max) | Use Case |
|--------|-----------|-------------------|----------|
| small | Standard_DS3_v2 | 1-4 | Development, small datasets |
| medium | Standard_DS4_v2 | 2-8 | Standard ETL, reporting |
| large | Standard_DS5_v2 | 4-16 | Large data processing |
| xlarge | Standard_E8s_v3 | 8-32 | Very large datasets, ML training |

All presets include:
- Photon runtime for 2-3x performance boost
- Spot instances with fallback for 60-80% cost savings
- Adaptive query execution
- Delta Lake optimizations

---

## Job Design Agent

### Input Specification

```python
input_data = {
    "job_name": "ETL Pipeline",
    "job_description": "Daily ETL job",
    "tasks": [
        {
            "task_name": "extract",
            "task_type": "notebook",
            "notebook_path": "/Workspace/notebooks/extract",
            "parameters": {"source": "s3://bucket/data"},
            "max_retries": 2,
            "timeout_seconds": 3600
        },
        {
            "task_name": "transform",
            "task_type": "python",
            "package_name": "data_processor",
            "entry_point": "main",
            "parameters": ["--mode", "batch"],
            "depends_on": ["extract"],
            "max_retries": 2,
            "timeout_seconds": 7200
        }
    ],
    "cluster_size": "medium",
    "schedule": {
        "quartz_cron_expression": "0 0 2 * * ?",
        "timezone_id": "UTC",
        "pause_status": "UNPAUSED"
    },
    "notification_emails": ["data-team@example.com"],
    "max_concurrent_runs": 1,
    "timeout_seconds": 14400
}
```

### Output

The agent generates:
1. **Complete JSON job configuration** - Ready to submit to Databricks
2. **Comprehensive documentation** - Job overview, tasks, dependencies, best practices
3. **Validation results** - Errors and warnings before deployment

---

## Cluster Configurations

### New Cluster Configuration

Each task can use a new job cluster with these features:

**Auto-scaling:**
```json
{
  "autoscale": {
    "min_workers": 2,
    "max_workers": 8
  }
}
```

**Cost Optimization:**
```json
{
  "aws_attributes": {
    "availability": "SPOT_WITH_FALLBACK",
    "spot_bid_price_percent": 100,
    "zone_id": "auto"
  }
}
```

**Performance:**
```json
{
  "runtime_engine": "PHOTON",
  "spark_conf": {
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true",
    "spark.databricks.delta.preview.enabled": "true"
  }
}
```

### Existing Cluster

Use an existing cluster instead:

```python
task_spec = {
    "task_name": "my_task",
    "existing_cluster_id": "1234-567890-abc123",
    # ... other task config
}
```

### Custom Spark Configuration

Add custom Spark settings:

```python
task_spec = {
    "task_name": "my_task",
    "spark_conf": {
        "spark.sql.shuffle.partitions": "200",
        "spark.executor.memory": "4g",
        "spark.sql.files.maxPartitionBytes": "134217728"
    },
    "spark_env_vars": {
        "ENV_VAR_1": "value1",
        "ENV_VAR_2": "value2"
    }
}
```

---

## Task Types

### 1. Notebook Task

**Use Case:** Run Databricks notebooks with parameters

```python
{
    "task_name": "notebook_etl",
    "task_type": "notebook",
    "description": "Extract and transform data",
    "notebook_path": "/Workspace/notebooks/etl",
    "parameters": {
        "source_path": "s3://bucket/data",
        "target_table": "prod.sales",
        "date": "{{ job.start_time }}"
    },
    "max_retries": 2,
    "timeout_seconds": 3600
}
```

**Generated Configuration:**
```json
{
  "notebook_task": {
    "notebook_path": "/Workspace/notebooks/etl",
    "source": "WORKSPACE",
    "base_parameters": {
      "source_path": "s3://bucket/data",
      "target_table": "prod.sales",
      "date": "{{ job.start_time }}"
    }
  }
}
```

---

### 2. Python Wheel Task

**Use Case:** Run Python packages with entry points

```python
{
    "task_name": "python_processor",
    "task_type": "python",
    "description": "Process data with Python package",
    "package_name": "data_processor",
    "entry_point": "main",
    "parameters": ["--mode", "batch", "--date", "2024-01-01"],
    "max_retries": 3,
    "timeout_seconds": 7200
}
```

**Generated Configuration:**
```json
{
  "python_wheel_task": {
    "package_name": "data_processor",
    "entry_point": "main",
    "parameters": ["--mode", "batch", "--date", "2024-01-01"]
  }
}
```

---

### 3. Spark JAR Task

**Use Case:** Run Spark applications packaged as JARs

```python
{
    "task_name": "jar_processor",
    "task_type": "jar",
    "description": "Process with Spark JAR",
    "main_class_name": "com.example.DataProcessor",
    "parameters": ["input=s3://bucket/data", "output=s3://bucket/output"],
    "max_retries": 2,
    "timeout_seconds": 5400
}
```

**Generated Configuration:**
```json
{
  "spark_jar_task": {
    "main_class_name": "com.example.DataProcessor",
    "parameters": ["input=s3://bucket/data", "output=s3://bucket/output"]
  }
}
```

---

### 4. SQL Task

**Use Case:** Run SQL queries on SQL warehouses

```python
{
    "task_name": "sql_report",
    "task_type": "sql",
    "description": "Generate report with SQL",
    "query_id": "abc123-def456-789",
    "warehouse_id": "xyz789-uvw456-123",
    "max_retries": 1,
    "timeout_seconds": 1800
}
```

**Generated Configuration:**
```json
{
  "sql_task": {
    "query": {
      "query_id": "abc123-def456-789"
    },
    "warehouse_id": "xyz789-uvw456-123"
  }
}
```

---

### 5. Delta Live Tables (DLT) Task

**Use Case:** Run DLT pipelines

```python
{
    "task_name": "dlt_pipeline",
    "task_type": "dlt",
    "description": "Run DLT pipeline",
    "pipeline_id": "pipeline-abc123",
    "max_retries": 1,
    "timeout_seconds": 7200
}
```

**Generated Configuration:**
```json
{
  "pipeline_task": {
    "pipeline_id": "pipeline-abc123"
  }
}
```

---

## Workflow Dependencies

### Simple Linear Workflow

```python
tasks = [
    {
        "task_name": "task1",
        "task_type": "notebook",
        "notebook_path": "/notebooks/task1"
    },
    {
        "task_name": "task2",
        "task_type": "notebook",
        "notebook_path": "/notebooks/task2",
        "depends_on": ["task1"]
    },
    {
        "task_name": "task3",
        "task_type": "notebook",
        "notebook_path": "/notebooks/task3",
        "depends_on": ["task2"]
    }
]
```

**Workflow:**
```
[START] → task1 → task2 → task3 → [END]
```

---

### Parallel Tasks with Join

```python
tasks = [
    {
        "task_name": "extract",
        "task_type": "notebook",
        "notebook_path": "/notebooks/extract"
    },
    {
        "task_name": "process_sales",
        "task_type": "notebook",
        "notebook_path": "/notebooks/process_sales",
        "depends_on": ["extract"]
    },
    {
        "task_name": "process_inventory",
        "task_type": "notebook",
        "notebook_path": "/notebooks/process_inventory",
        "depends_on": ["extract"]
    },
    {
        "task_name": "load",
        "task_type": "notebook",
        "notebook_path": "/notebooks/load",
        "depends_on": ["process_sales", "process_inventory"]
    }
]
```

**Workflow:**
```
           ┌─→ process_sales ─┐
[START] → extract             → load → [END]
           └─→ process_inventory ─┘
```

---

### Circular Dependency Detection

The agent automatically detects circular dependencies:

**Invalid Configuration:**
```python
tasks = [
    {"task_name": "task1", "depends_on": ["task2"]},
    {"task_name": "task2", "depends_on": ["task3"]},
    {"task_name": "task3", "depends_on": ["task1"]}  # Creates cycle!
]
```

**Error:**
```
❌ Circular dependencies detected in task workflow
```

---

## CLI Usage

### Generate Sample Tasks File

```bash
# Create sample tasks JSON file
python -m ai_sdlc.cli.databricks_job_commands generate-sample \
  --output tasks.json \
  --count 3

# Output:
# ✅ Sample tasks file created: tasks.json
#    Task count: 3
#
# Edit this file to customize tasks, then use:
#   python -m ai_sdlc.cli.databricks_job_commands design --job-name "My Job" --tasks tasks.json
```

---

### Design a Simple Job

```bash
# Design a simple job with default settings
python -m ai_sdlc.cli.databricks_job_commands design \
  --job-name "ETL Pipeline" \
  --description "Daily ETL job" \
  --tasks tasks.json \
  --cluster-size medium
```

**Output:**
```
🔧 Designing Databricks job: ETL Pipeline
   Cluster size: medium
   Task count: 3
   Max concurrent runs: 1

======================================================================
📊 Job Design Summary
======================================================================

Job name:           ETL Pipeline
Task count:         3
Cluster size:       medium
Has schedule:       No
Max concurrent:     1

✅ Configuration validation: PASSED

📄 Configuration file: ./databricks-job-designs/job-etl-pipeline-config.json
📄 Documentation file: ./databricks-job-designs/job-etl-pipeline-design.md

Next steps:
1. Review the generated job configuration
2. Customize cluster settings if needed
3. Create the job in Databricks:
   databricks jobs create --json-file ./databricks-job-designs/job-etl-pipeline-config.json
```

---

### Design a Scheduled Job with Notifications

```bash
# Design job with schedule and email notifications
python -m ai_sdlc.cli.databricks_job_commands design \
  --job-name "Daily Report" \
  --description "Generate daily reports at 2 AM EST" \
  --tasks tasks.json \
  --cluster-size small \
  --schedule "0 0 2 * * ?" \
  --timezone "America/New_York" \
  --emails data-team@example.com ops-team@example.com \
  --max-concurrent 1
```

---

### Design Job with Custom Timeout

```bash
# Design job with custom timeouts
python -m ai_sdlc.cli.databricks_job_commands design \
  --job-name "Long Running Job" \
  --tasks tasks.json \
  --cluster-size large \
  --timeout 28800 \
  --max-concurrent 3
```

---

### Validate Job Configuration

```bash
# Validate an existing job configuration
python -m ai_sdlc.cli.databricks_job_commands validate \
  --config job-etl-pipeline-config.json
```

**Output:**
```
🔍 Validating job configuration: job-etl-pipeline-config.json

✅ Configuration is valid
```

---

### Design Job with Work Item ID

```bash
# Link job design to Azure DevOps work item
python -m ai_sdlc.cli.databricks_job_commands design \
  --job-name "Feature Pipeline" \
  --tasks tasks.json \
  --cluster-size medium \
  --work-item-id 6340168
```

---

## Best Practices

### 1. Cluster Sizing

**Choose the right cluster size for your workload:**

| Workload | Cluster Size | Rationale |
|----------|--------------|-----------|
| Development/Testing | small | Cost-effective, fast startup |
| Standard ETL | medium | Balanced performance and cost |
| Large data processing | large | More compute power |
| ML training, very large datasets | xlarge | Maximum performance |

**Pro Tip:** Start with `medium` and adjust based on performance metrics.

---

### 2. Task Retries

**Configure appropriate retry settings:**

```python
{
    "max_retries": 2,                    # Retry up to 2 times
    "min_retry_interval_millis": 2000,   # Wait 2 seconds between retries
    "retry_on_timeout": True             # Retry if task times out
}
```

**Best Practices:**
- Use `max_retries: 2-3` for transient failures
- Set longer `min_retry_interval` for rate-limited APIs
- Always enable `retry_on_timeout` for long-running tasks

---

### 3. Timeouts

**Set appropriate timeouts to prevent runaway jobs:**

```python
{
    "timeout_seconds": 3600,  # Task timeout: 1 hour
}

# Job-level timeout
{
    "job_name": "My Job",
    "timeout_seconds": 14400,  # Job timeout: 4 hours
}
```

**Guidelines:**
- Set task timeouts based on expected duration + 50% buffer
- Set job timeout to sum of task timeouts + overhead
- Use `0` for no timeout (not recommended for production)

---

### 4. Notifications

**Configure email notifications for job monitoring:**

```python
{
    "notification_emails": [
        "data-team@example.com",
        "ops-team@example.com"
    ]
}
```

**Notifications are sent:**
- **On Start:** Job begins execution
- **On Success:** All tasks complete successfully
- **On Failure:** Any task fails after retries

---

### 5. Scheduling

**Use Quartz cron expressions for scheduling:**

| Schedule | Cron Expression | Description |
|----------|----------------|-------------|
| Daily at 2 AM | `0 0 2 * * ?` | Every day at 2:00 AM |
| Hourly | `0 0 * * * ?` | Every hour on the hour |
| Every 15 minutes | `0 */15 * * * ?` | Every 15 minutes |
| Weekdays at 9 AM | `0 0 9 ? * MON-FRI` | Monday-Friday at 9:00 AM |
| First of month | `0 0 0 1 * ?` | 12:00 AM on 1st day of month |

**Timezone Considerations:**
- Always specify timezone explicitly
- Use IANA timezone names (e.g., `America/New_York`, `Europe/London`)
- Consider daylight saving time transitions

---

### 6. Dependencies

**Design clean dependency graphs:**

✅ **Good - Linear Dependencies:**
```
extract → transform → load
```

✅ **Good - Parallel with Join:**
```
        ┌─→ process_sales ─┐
extract                    → load
        └─→ process_inventory ─┘
```

❌ **Bad - Circular Dependencies:**
```
task1 → task2 → task3 → task1  # Creates infinite loop!
```

---

### 7. Cost Optimization

**Built-in cost optimizations:**
- ✅ Spot instances with fallback (60-80% cost savings)
- ✅ Auto-scaling (scale down when idle)
- ✅ Photon runtime (2-3x faster = less runtime)
- ✅ Job clusters (terminate after job completion)

**Additional Recommendations:**
- Use `existing_cluster_id` for development/testing
- Set appropriate `max_workers` limits
- Use smaller clusters for smaller datasets
- Monitor cluster utilization metrics

---

### 8. Parameter Passing

**Use task parameters for flexibility:**

```python
{
    "notebook_path": "/Workspace/notebooks/etl",
    "parameters": {
        "date": "{{ job.start_time }}",           # Databricks variable
        "source": "s3://bucket/data",
        "target": "prod.sales",
        "mode": "overwrite"
    }
}
```

**Common Parameters:**
- Date/timestamp for incremental processing
- Source/target paths
- Processing mode (append, overwrite)
- Feature flags

---

## Examples

### Example 1: Simple ETL Pipeline

```python
from ai_sdlc.agents.databricks_job_design_agent import DatabricksJobDesignAgent

# Define tasks
tasks = [
    {
        "task_name": "extract",
        "task_type": "notebook",
        "notebook_path": "/Workspace/notebooks/extract",
        "parameters": {"source": "s3://bucket/data"},
        "max_retries": 2,
        "timeout_seconds": 3600
    },
    {
        "task_name": "transform",
        "task_type": "notebook",
        "notebook_path": "/Workspace/notebooks/transform",
        "parameters": {"format": "delta"},
        "depends_on": ["extract"],
        "max_retries": 2,
        "timeout_seconds": 3600
    },
    {
        "task_name": "load",
        "task_type": "notebook",
        "notebook_path": "/Workspace/notebooks/load",
        "parameters": {"target": "prod.sales"},
        "depends_on": ["transform"],
        "max_retries": 1,
        "timeout_seconds": 1800
    }
]

# Create agent
agent = DatabricksJobDesignAgent(work_item_id="6340168")

# Design job
result = agent.execute({
    "job_name": "Sales ETL Pipeline",
    "job_description": "Daily sales data ETL",
    "tasks": tasks,
    "cluster_size": "medium",
    "notification_emails": ["data-team@example.com"]
})

print(f"Job designed: {result['data']['job_name']}")
print(f"Config file: {result['data']['config_file']}")
```

---

### Example 2: Scheduled Data Processing

```python
# Design scheduled job with cron
agent = DatabricksJobDesignAgent(work_item_id="6340168")

result = agent.execute({
    "job_name": "Daily Report Generation",
    "job_description": "Generate daily reports at 2 AM EST",
    "tasks": [
        {
            "task_name": "generate_report",
            "task_type": "notebook",
            "notebook_path": "/Workspace/notebooks/report",
            "parameters": {"date": "{{ job.start_time }}"},
            "max_retries": 1,
            "timeout_seconds": 3600
        }
    ],
    "cluster_size": "small",
    "schedule": {
        "quartz_cron_expression": "0 0 2 * * ?",
        "timezone_id": "America/New_York",
        "pause_status": "UNPAUSED"
    },
    "notification_emails": ["reports@example.com"],
    "max_concurrent_runs": 1
})
```

---

### Example 3: Complex Multi-Task Workflow

```python
# Design complex workflow with parallel tasks
tasks = [
    {
        "task_name": "ingest_raw_data",
        "task_type": "notebook",
        "notebook_path": "/Workspace/notebooks/ingest",
        "parameters": {"source": "s3://bucket/raw"},
        "max_retries": 3,
        "timeout_seconds": 7200
    },
    {
        "task_name": "process_sales",
        "task_type": "python",
        "package_name": "sales_processor",
        "entry_point": "main",
        "parameters": ["--mode", "batch"],
        "depends_on": ["ingest_raw_data"],
        "max_retries": 2,
        "timeout_seconds": 5400
    },
    {
        "task_name": "process_inventory",
        "task_type": "python",
        "package_name": "inventory_processor",
        "entry_point": "main",
        "parameters": ["--mode", "batch"],
        "depends_on": ["ingest_raw_data"],
        "max_retries": 2,
        "timeout_seconds": 5400
    },
    {
        "task_name": "validate_data",
        "task_type": "notebook",
        "notebook_path": "/Workspace/notebooks/validate",
        "parameters": {"threshold": "0.95"},
        "depends_on": ["process_sales", "process_inventory"],
        "max_retries": 1,
        "timeout_seconds": 1800
    },
    {
        "task_name": "generate_report",
        "task_type": "sql",
        "query_id": "report-query-123",
        "warehouse_id": "warehouse-456",
        "depends_on": ["validate_data"],
        "max_retries": 1,
        "timeout_seconds": 1800
    }
]

agent = DatabricksJobDesignAgent(work_item_id="6340168")

result = agent.execute({
    "job_name": "Multi-Source Data Pipeline",
    "job_description": "Process sales and inventory data with validation",
    "tasks": tasks,
    "cluster_size": "large",
    "max_concurrent_runs": 2,
    "timeout_seconds": 21600,
    "notification_emails": ["data-team@example.com", "ops-team@example.com"]
})
```

**Workflow Diagram:**
```
                        ┌─→ process_sales ─┐
[START] → ingest_raw_data                  → validate_data → generate_report → [END]
                        └─→ process_inventory ─┘
```

---

### Example 4: Using Existing Cluster

```python
# Design job that uses existing cluster
tasks = [
    {
        "task_name": "quick_analysis",
        "task_type": "notebook",
        "notebook_path": "/Workspace/notebooks/analysis",
        "parameters": {"dataset": "test"},
        "existing_cluster_id": "1234-567890-abc123",  # Use existing cluster
        "max_retries": 1,
        "timeout_seconds": 1800
    }
]

agent = DatabricksJobDesignAgent(work_item_id="6340168")

result = agent.execute({
    "job_name": "Quick Analysis",
    "tasks": tasks,
    # cluster_size not needed when using existing cluster
})
```

---

### Example 5: Custom Spark Configuration

```python
# Design job with custom Spark settings
tasks = [
    {
        "task_name": "large_join",
        "task_type": "notebook",
        "notebook_path": "/Workspace/notebooks/join",
        "parameters": {"tables": "sales,inventory"},
        "spark_conf": {
            "spark.sql.shuffle.partitions": "400",
            "spark.sql.adaptive.coalescePartitions.enabled": "true",
            "spark.sql.adaptive.skewJoin.enabled": "true",
            "spark.executor.memory": "8g",
            "spark.driver.memory": "4g"
        },
        "spark_env_vars": {
            "PYSPARK_PYTHON": "/databricks/python3/bin/python3",
            "CUSTOM_VAR": "value"
        },
        "max_retries": 2,
        "timeout_seconds": 7200
    }
]

agent = DatabricksJobDesignAgent(work_item_id="6340168")

result = agent.execute({
    "job_name": "Large Join Processing",
    "tasks": tasks,
    "cluster_size": "xlarge"
})
```

---

## Troubleshooting

### Issue 1: "Job name is required"

**Problem:** No job name provided

**Solution:**
```bash
# Ensure --job-name is provided
python -m ai_sdlc.cli.databricks_job_commands design \
  --job-name "My Job" \
  --tasks tasks.json
```

---

### Issue 2: "At least one task is required"

**Problem:** Empty tasks array or invalid tasks file

**Solution:**
```bash
# Verify tasks.json has at least one task
cat tasks.json

# Generate sample tasks file
python -m ai_sdlc.cli.databricks_job_commands generate-sample \
  --output tasks.json
```

---

### Issue 3: "Invalid cluster size"

**Problem:** Cluster size not one of: small, medium, large, xlarge

**Solution:**
```bash
# Use valid cluster size
python -m ai_sdlc.cli.databricks_job_commands design \
  --job-name "My Job" \
  --tasks tasks.json \
  --cluster-size medium  # Valid: small, medium, large, xlarge
```

---

### Issue 4: "Circular dependencies detected"

**Problem:** Tasks have circular dependencies (A depends on B, B depends on C, C depends on A)

**Solution:**
```python
# Fix tasks.json to remove circular dependencies
# BAD:
[
  {"task_name": "task1", "depends_on": ["task2"]},
  {"task_name": "task2", "depends_on": ["task3"]},
  {"task_name": "task3", "depends_on": ["task1"]}  # Creates cycle!
]

# GOOD:
[
  {"task_name": "task1"},
  {"task_name": "task2", "depends_on": ["task1"]},
  {"task_name": "task3", "depends_on": ["task2"]}
]
```

---

### Issue 5: "Task must have a task type configuration"

**Problem:** Task missing required task type fields

**Solution:**
```python
# Ensure each task has appropriate task type configuration
{
  "task_name": "my_task",
  "task_type": "notebook",
  "notebook_path": "/Workspace/notebooks/my_notebook",  # Required for notebook tasks
  "parameters": {}
}
```

---

### Issue 6: "Task must have cluster configuration"

**Problem:** Task missing both `new_cluster` and `existing_cluster_id`

**Solution:**
```python
# Option 1: Let agent generate new_cluster (default)
{
  "task_name": "my_task",
  "task_type": "notebook",
  "notebook_path": "/test"
  # cluster_size parameter will generate new_cluster
}

# Option 2: Specify existing cluster
{
  "task_name": "my_task",
  "task_type": "notebook",
  "notebook_path": "/test",
  "existing_cluster_id": "1234-567890-abc123"
}
```

---

### Issue 7: Job Creation Fails in Databricks

**Problem:** Job configuration valid but fails to create in Databricks

**Solution:**
```bash
# 1. Validate configuration first
python -m ai_sdlc.cli.databricks_job_commands validate \
  --config job-config.json

# 2. Check Databricks CLI configuration
databricks configure --token

# 3. Verify notebook paths exist
databricks workspace ls /Workspace/notebooks/

# 4. Check warehouse IDs for SQL tasks
databricks sql warehouses list

# 5. Verify pipeline IDs for DLT tasks
databricks pipelines list
```

---

### Issue 8: Schedule Not Triggering

**Problem:** Job created but schedule doesn't run

**Solution:**
```python
# 1. Verify cron expression syntax
# Use: https://www.freeformatter.com/cron-expression-generator-quartz.html

# 2. Check timezone
{
  "schedule": {
    "quartz_cron_expression": "0 0 2 * * ?",
    "timezone_id": "America/New_York",  # Ensure correct timezone
    "pause_status": "UNPAUSED"  # Must be UNPAUSED
  }
}

# 3. Verify job isn't paused in Databricks UI
# Jobs → [Your Job] → Schedule → Status
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-17 | AI-SDLC Platform Team | Initial documentation for Databricks job design feature |

---

**For questions or support:**
- Slack: #ai-sdlc-support
- Documentation: `docs/` directory
- Tests: `tests/unit/test_databricks_job_design.py`
