"""ML Monitoring Setup Template"""

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import MonitorInferenceLog

w = WorkspaceClient()

def setup_model_monitoring(
    inference_table: str,
    model_name: str,
    baseline_table: str = None
):
    """Setup Lakehouse Monitor for model inference"""

    monitor_config = MonitorInferenceLog(
        model_id_col="model_id",
        prediction_col="prediction",
        timestamp_col="timestamp",
        granularities=["1 hour", "1 day"],
        baseline_table_name=baseline_table
    )

    monitor = w.quality_monitors.create(
        table_name=inference_table,
        assets_dir=f"/monitoring/{model_name}",
        output_schema_name="ml_monitoring",
        inference_log=monitor_config
    )

    print(f"✓ Monitor created for {model_name}")
    return monitor
