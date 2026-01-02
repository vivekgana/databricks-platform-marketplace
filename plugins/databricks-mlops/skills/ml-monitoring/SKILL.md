# ML Monitoring Skill

**Last Updated:** 2026-01-01 22:45:49
**Version:** 1.0.0

## Overview

Master model monitoring patterns including drift detection, performance tracking, and alerting for production ML systems.

## Key Patterns

### Pattern 1: Lakehouse Monitor Setup

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import MonitorInferenceLog

w = WorkspaceClient()

monitor = w.quality_monitors.create(
    table_name="catalog.schema.inference_logs",
    assets_dir="/monitoring/model_name",
    output_schema_name="ml_monitoring",
    inference_log=MonitorInferenceLog(
        model_id_col="model_id",
        prediction_col="prediction",
        timestamp_col="timestamp",
        granularities=["1 day"]
    )
)
```

### Pattern 2: Drift Detection

```python
from scipy.stats import ks_2samp

def detect_drift(reference_data, current_data, features: list):
    """Statistical drift detection"""
    drift_results = {}

    for feature in features:
        stat, p_value = ks_2samp(
            reference_data[feature],
            current_data[feature]
        )
        drift_results[feature] = {
            "statistic": stat,
            "p_value": p_value,
            "drift_detected": p_value < 0.05
        }

    return drift_results
```

### Pattern 3: Performance Monitoring

```python
def monitor_model_performance(inference_table: str):
    """Monitor model performance metrics"""

    df = spark.table(inference_table)

    metrics = df.agg({
        "prediction_time_ms": "avg",
        "error": "sum"
    }).collect()[0]

    if metrics["avg(prediction_time_ms)"] > 100:
        send_alert("High latency detected")

    return metrics
```

## Best Practices

1. Log all inference requests
2. Capture predictions and actuals
3. Monitor feature distributions
4. Track performance metrics
5. Set up alerts
6. Create monitoring dashboards

## References

- [Lakehouse Monitoring](https://docs.databricks.com/lakehouse-monitoring/)
