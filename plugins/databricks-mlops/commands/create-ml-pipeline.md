# Create ML Pipeline Command

**Last Updated:** 2026-01-01 22:45:49
**Version:** 1.0.0
**Category:** Pipeline

## Overview

Create end-to-end ML pipelines with feature engineering, training, validation, and deployment orchestration.

## Command Usage

```bash
/databricks-mlops:create-ml-pipeline --pipeline-name <name> --config <config.yaml>
```

## ML Pipeline Implementation

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs
from databricks import feature_store
import mlflow

w = WorkspaceClient()

def create_ml_pipeline_workflow(
    pipeline_name: str,
    cluster_config: dict,
    tasks_config: list
):
    """Create Databricks workflow for ML pipeline"""

    tasks = []

    # Task 1: Feature Engineering
    tasks.append(
        jobs.Task(
            task_key="feature_engineering",
            description="Compute and store features in Feature Store",
            notebook_task=jobs.NotebookTask(
                notebook_path="/Pipelines/feature_engineering",
                base_parameters={"catalog": "main", "schema": "features"}
            ),
            new_cluster=cluster_config
        )
    )

    # Task 2: Model Training
    tasks.append(
        jobs.Task(
            task_key="model_training",
            description="Train ML model with hyperparameter tuning",
            depends_on=[jobs.TaskDependency(task_key="feature_engineering")],
            notebook_task=jobs.NotebookTask(
                notebook_path="/Pipelines/train_model",
                base_parameters={"experiment_name": f"/ml-experiments/{pipeline_name}"}
            ),
            new_cluster=cluster_config
        )
    )

    # Task 3: Model Validation
    tasks.append(
        jobs.Task(
            task_key="model_validation",
            description="Validate model performance and quality",
            depends_on=[jobs.TaskDependency(task_key="model_training")],
            notebook_task=jobs.NotebookTask(
                notebook_path="/Pipelines/validate_model",
                base_parameters={"min_accuracy": "0.85"}
            ),
            new_cluster=cluster_config
        )
    )

    # Task 4: Model Registration
    tasks.append(
        jobs.Task(
            task_key="model_registration",
            description="Register model to MLflow Registry",
            depends_on=[jobs.TaskDependency(task_key="model_validation")],
            notebook_task=jobs.NotebookTask(
                notebook_path="/Pipelines/register_model",
                base_parameters={"model_name": pipeline_name}
            ),
            new_cluster=cluster_config
        )
    )

    # Task 5: Deploy to Staging
    tasks.append(
        jobs.Task(
            task_key="deploy_staging",
            description="Deploy model to staging endpoint",
            depends_on=[jobs.TaskDependency(task_key="model_registration")],
            notebook_task=jobs.NotebookTask(
                notebook_path="/Pipelines/deploy_model",
                base_parameters={
                    "endpoint_name": f"{pipeline_name}_staging",
                    "environment": "staging"
                }
            ),
            new_cluster=cluster_config
        )
    )

    # Create job
    job = w.jobs.create(
        name=pipeline_name,
        tasks=tasks,
        schedule=jobs.CronSchedule(
            quartz_cron_expression="0 0 2 * * ?",  # Daily at 2 AM
            timezone_id="UTC"
        ),
        email_notifications=jobs.JobEmailNotifications(
            on_failure=["ml-team@company.com"]
        )
    )

    print(f"✓ ML Pipeline created: {pipeline_name}")
    print(f"✓ Job ID: {job.job_id}")

    return job

def create_feature_engineering_notebook():
    """Generate feature engineering notebook content"""

    notebook_content = """
# Feature Engineering Pipeline

from databricks import feature_store
from pyspark.sql import functions as F

# Initialize Feature Store
fs = feature_store.FeatureStoreClient()

# Load raw data
df = spark.table("main.bronze.raw_data")

# Feature transformations
features = df.groupBy("entity_id").agg(
    F.avg("metric1").alias("avg_metric1"),
    F.max("metric2").alias("max_metric2"),
    F.count("*").alias("record_count"),
    F.stddev("metric1").alias("std_metric1")
)

# Write to Feature Store
fs.write_table(
    name="main.features.ml_features",
    df=features,
    mode="merge"
)

print("✓ Features computed and stored")
"""
    return notebook_content

def create_training_notebook():
    """Generate model training notebook content"""

    notebook_content = """
# Model Training Pipeline

import mlflow
from databricks import feature_store
from sklearn.ensemble import RandomForestClassifier

fs = feature_store.FeatureStoreClient()

# Load training data with features
training_df = spark.table("main.ml_data.training_set")

training_set = fs.create_training_set(
    df=training_df,
    feature_lookups=[
        feature_store.FeatureLookup(
            table_name="main.features.ml_features",
            lookup_key="entity_id"
        )
    ],
    label="target"
)

# Train model
with mlflow.start_run():
    X = training_set.load_df().drop("target")
    y = training_set.load_df().select("target")

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)

    mlflow.sklearn.log_model(model, "model")

print("✓ Model trained and logged")
"""
    return notebook_content

# Example usage
if __name__ == "__main__":
    cluster_config = {
        "spark_version": "14.3.x-cpu-ml-scala2.12",
        "node_type_id": "i3.xlarge",
        "num_workers": 2
    }

    pipeline = create_ml_pipeline_workflow(
        pipeline_name="customer_churn_pipeline",
        cluster_config=cluster_config,
        tasks_config=[]
    )
```

## Pipeline Components

1. **Feature Engineering**
   - Data preprocessing
   - Feature computation
   - Feature Store updates

2. **Model Training**
   - Hyperparameter tuning
   - Model training
   - Experiment tracking

3. **Model Validation**
   - Performance testing
   - Quality checks
   - Threshold validation

4. **Model Registration**
   - MLflow Registry
   - Version management
   - Metadata tagging

5. **Deployment**
   - Staging deployment
   - Integration testing
   - Production promotion

## Best Practices

1. **Pipeline Design**
   - Modular components
   - Clear dependencies
   - Error handling
   - Retry logic

2. **Orchestration**
   - Appropriate scheduling
   - Resource management
   - Monitoring and alerts
   - Failure notifications

3. **Testing**
   - Unit tests for each component
   - Integration tests
   - End-to-end validation
   - Data quality checks

## References

- [Databricks Workflows](https://docs.databricks.com/workflows/index.html)
