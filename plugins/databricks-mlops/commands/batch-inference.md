# Batch Inference Command

**Last Updated:** 2026-01-01 22:45:49
**Version:** 1.0.0
**Category:** Inference

## Overview

Run batch inference jobs with feature lookup, monitoring, and result persistence for large-scale predictions.

## Command Usage

```bash
/databricks-mlops:batch-inference --model-name <name> --input-table <table> --output-table <table>
```

## Batch Inference Script

```python
import mlflow
from databricks import feature_store
from pyspark.sql import functions as F
from datetime import datetime

fs = feature_store.FeatureStoreClient()

def run_batch_inference(
    model_uri: str,
    input_table: str,
    output_table: str,
    feature_lookups: list = None,
    batch_size: int = 10000
):
    """Run batch inference with feature store integration"""

    # Load input data
    input_df = spark.table(input_table)

    print(f"Processing {input_df.count()} records")

    # Feature lookup if specified
    if feature_lookups:
        inference_df = fs.score_batch(
            model_uri=model_uri,
            df=input_df,
            result_type="string"
        )
    else:
        # Load model and predict
        model = mlflow.pyfunc.spark_udf(spark, model_uri=model_uri)
        feature_cols = [col for col in input_df.columns if col not in ['id', 'timestamp']]

        inference_df = input_df.withColumn(
            'prediction',
            model(*feature_cols)
        )

    # Add metadata
    inference_df = inference_df.withColumn(
        'inference_timestamp',
        F.current_timestamp()
    ).withColumn(
        'model_uri',
        F.lit(model_uri)
    )

    # Write results
    inference_df.write.mode("append").saveAsTable(output_table)

    print(f"✓ Inference completed")
    print(f"✓ Results written to: {output_table}")

    return inference_df

def create_batch_inference_job(
    job_name: str,
    model_name: str,
    input_table: str,
    output_table: str,
    schedule: str = None
):
    """Create scheduled batch inference job"""

    from databricks.sdk import WorkspaceClient
    from databricks.sdk.service import jobs

    w = WorkspaceClient()

    notebook_task = jobs.NotebookTask(
        notebook_path="/Inference/batch_inference",
        base_parameters={
            "model_name": model_name,
            "input_table": input_table,
            "output_table": output_table
        }
    )

    task = jobs.Task(
        task_key="batch_inference",
        description="Batch inference job",
        notebook_task=notebook_task,
        new_cluster={
            "spark_version": "14.3.x-cpu-ml-scala2.12",
            "node_type_id": "i3.xlarge",
            "num_workers": 4
        }
    )

    job_config = {
        "name": job_name,
        "tasks": [task]
    }

    if schedule:
        job_config["schedule"] = jobs.CronSchedule(
            quartz_cron_expression=schedule,
            timezone_id="UTC"
        )

    job = w.jobs.create(**job_config)

    print(f"✓ Batch inference job created: {job.job_id}")

    return job

def monitor_inference_quality(output_table: str, reference_data: str = None):
    """Monitor batch inference quality"""

    inference_df = spark.table(output_table)

    # Prediction distribution
    pred_dist = inference_df.groupBy('prediction').count().toPandas()

    print("\nPrediction Distribution:")
    print(pred_dist)

    # Check for drift if reference data provided
    if reference_data:
        ref_df = spark.table(reference_data)

        print("\nComparing with reference data...")
        # Statistical tests would go here

    return pred_dist

# Example usage
if __name__ == "__main__":
    MODEL_URI = "models:/main.ml_models.churn_classifier/Production"
    INPUT_TABLE = "main.ml_data.customers_to_score"
    OUTPUT_TABLE = "main.ml_predictions.churn_scores"

    # Run batch inference
    results = run_batch_inference(
        model_uri=MODEL_URI,
        input_table=INPUT_TABLE,
        output_table=OUTPUT_TABLE
    )

    # Monitor quality
    monitor_inference_quality(OUTPUT_TABLE)

    # Create scheduled job
    create_batch_inference_job(
        job_name="daily_churn_scoring",
        model_name="main.ml_models.churn_classifier",
        input_table=INPUT_TABLE,
        output_table=OUTPUT_TABLE,
        schedule="0 0 2 * * ?"  # Daily at 2 AM
    )
```

## Best Practices

1. **Performance**
   - Use appropriate batch sizes
   - Enable auto-scaling
   - Partition data efficiently
   - Cache feature lookups

2. **Monitoring**
   - Track inference metrics
   - Monitor data quality
   - Detect distribution shifts
   - Log failures

3. **Data Management**
   - Version input/output data
   - Retain predictions with metadata
   - Implement data retention policies
   - Archive old predictions

## References

- [Databricks Feature Store](https://docs.databricks.com/machine-learning/feature-store/index.html)
