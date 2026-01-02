# Setup Monitoring Command

**Last Updated:** 2026-01-01 22:45:49
**Version:** 1.0.0
**Category:** Monitoring

## Overview

Set up comprehensive model monitoring including drift detection, performance tracking, and alerting for production ML models.

## Command Usage

```bash
/databricks-mlops:setup-monitoring --model-name <name> --endpoint <endpoint>
```

## Monitoring Implementation

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import MonitorInferenceLog, MonitorTimeSeries
import mlflow
from pyspark.sql import functions as F
from datetime import datetime, timedelta

w = WorkspaceClient()

def create_inference_table_monitor(
    table_name: str,
    model_name: str,
    baseline_table: str = None
):
    """Create Lakehouse Monitor for model inference logs"""

    monitor_config = MonitorInferenceLog(
        model_id_col="model_id",
        prediction_col="prediction",
        timestamp_col="timestamp",
        granularities=["1 day"],
        baseline_table_name=baseline_table
    )

    monitor = w.quality_monitors.create(
        table_name=table_name,
        assets_dir=f"/Workspace/monitoring/{model_name}",
        output_schema_name="ml_monitoring",
        inference_log=monitor_config
    )

    print(f"✓ Monitor created for {table_name}")
    return monitor

def setup_drift_detection(
    inference_table: str,
    reference_table: str,
    features: list
):
    """Setup statistical drift detection"""

    from scipy.stats import ks_2samp
    import pandas as pd

    # Read data
    inference_df = spark.table(inference_table).toPandas()
    reference_df = spark.table(reference_table).toPandas()

    drift_results = {}

    for feature in features:
        # Kolmogorov-Smirnov test
        statistic, p_value = ks_2samp(
            reference_df[feature],
            inference_df[feature]
        )

        drift_results[feature] = {
            "ks_statistic": statistic,
            "p_value": p_value,
            "is_drift": p_value < 0.05
        }

    # Log to MLflow
    with mlflow.start_run():
        mlflow.log_dict(drift_results, "drift_report.json")

    return drift_results

def create_monitoring_dashboard(model_name: str, endpoint_name: str):
    """Create monitoring dashboard with key metrics"""

    dashboard_config = {
        "name": f"{model_name}_monitoring",
        "widgets": [
            {
                "type": "metric",
                "title": "Prediction Volume",
                "query": f"SELECT COUNT(*) FROM ml_monitoring.{model_name}_metrics"
            },
            {
                "type": "time_series",
                "title": "Model Latency",
                "query": f"SELECT timestamp, AVG(latency_ms) FROM ml_monitoring.{model_name}_metrics GROUP BY timestamp"
            },
            {
                "type": "metric",
                "title": "Drift Score",
                "query": f"SELECT AVG(drift_score) FROM ml_monitoring.{model_name}_drift"
            }
        ]
    }

    print(f"✓ Dashboard configuration created")
    return dashboard_config

def setup_alerting(model_name: str, alert_config: dict):
    """Configure alerts for model performance degradation"""

    alerts = []

    # Performance degradation alert
    if "performance_threshold" in alert_config:
        alerts.append({
            "name": f"{model_name}_performance_alert",
            "condition": f"accuracy < {alert_config['performance_threshold']}",
            "notification": alert_config.get("email", [])
        })

    # Drift alert
    if "drift_threshold" in alert_config:
        alerts.append({
            "name": f"{model_name}_drift_alert",
            "condition": f"drift_score > {alert_config['drift_threshold']}",
            "notification": alert_config.get("email", [])
        })

    print(f"✓ Configured {len(alerts)} alerts")
    return alerts

# Example usage
if __name__ == "__main__":
    MODEL_NAME = "my_classifier"
    INFERENCE_TABLE = "main.ml_monitoring.inference_logs"

    # Create monitor
    monitor = create_inference_table_monitor(
        table_name=INFERENCE_TABLE,
        model_name=MODEL_NAME,
        baseline_table="main.ml_models.training_data"
    )

    # Setup drift detection
    drift = setup_drift_detection(
        inference_table=INFERENCE_TABLE,
        reference_table="main.ml_models.training_data",
        features=["feature1", "feature2", "feature3"]
    )

    # Setup alerts
    alerts = setup_alerting(
        model_name=MODEL_NAME,
        alert_config={
            "performance_threshold": 0.85,
            "drift_threshold": 0.3,
            "email": ["ml-team@company.com"]
        }
    )
```

## Best Practices

1. **Monitoring Strategy**
   - Monitor input/output distributions
   - Track performance metrics
   - Detect data quality issues
   - Monitor system health

2. **Drift Detection**
   - Use statistical tests (KS, PSI)
   - Set appropriate thresholds
   - Monitor feature importance changes
   - Track prediction distribution

3. **Alerting**
   - Define clear alert conditions
   - Avoid alert fatigue
   - Include actionable information
   - Test alert delivery

## References

- [Lakehouse Monitoring](https://docs.databricks.com/lakehouse-monitoring/index.html)
