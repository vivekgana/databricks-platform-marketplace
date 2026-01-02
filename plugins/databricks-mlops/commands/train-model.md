# Train Model Command

**Last Updated:** 2026-01-01 22:45:49
**Version:** 1.0.0
**Category:** Training

## Overview

Train machine learning models with comprehensive MLflow experiment tracking, auto-logging, and distributed training support. This command guides you through training ML models on Databricks with best practices for reproducibility and scalability.

## Prerequisites

- Databricks workspace with ML runtime
- MLflow configured
- Training data available in Delta tables or volumes
- Appropriate cluster configuration for training workload

## Command Usage

```bash
/databricks-mlops:train-model [model-type] [--config path/to/config.yaml]
```

## Parameters

- `model-type` (optional): Type of model to train (sklearn, xgboost, lightgbm, pytorch, tensorflow)
- `--config`: Path to training configuration file
- `--experiment-name`: MLflow experiment name
- `--auto-log`: Enable MLflow auto-logging (default: true)
- `--distributed`: Enable distributed training for supported frameworks

## Training Process

You are an expert MLOps engineer specializing in Databricks model training. Guide the user through:

### 1. Training Configuration
- Determine model type and framework
- Configure training parameters
- Set up data loading and preprocessing
- Define evaluation metrics

### 2. Experiment Setup
- Create or select MLflow experiment
- Configure experiment tracking
- Set up auto-logging for the framework
- Define run tags and metadata

### 3. Training Implementation

Generate a comprehensive training script:

```python
import mlflow
import mlflow.sklearn
from databricks import feature_store
from pyspark.sql import SparkSession
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
EXPERIMENT_NAME = "/Users/{username}/ml-experiments/{project_name}"
MODEL_NAME = "{model_name}"
CATALOG = "main"
SCHEMA = "ml_models"

# Initialize Spark and Feature Store
spark = SparkSession.builder.getOrCreate()
fs = feature_store.FeatureStoreClient()

def load_training_data(table_name: str):
    """Load training data from Delta table"""
    logger.info(f"Loading training data from {table_name}")
    df = spark.table(table_name)
    return df.toPandas()

def prepare_features(df: pd.DataFrame, feature_cols: list, target_col: str):
    """Prepare features and target for training"""
    X = df[feature_cols]
    y = df[target_col]
    return train_test_split(X, y, test_size=0.2, random_state=42)

def train_model(X_train, y_train, X_test, y_test, params: dict):
    """Train model with MLflow tracking"""

    # Set experiment
    mlflow.set_experiment(EXPERIMENT_NAME)

    with mlflow.start_run(run_name=f"{MODEL_NAME}_training") as run:
        # Enable autologging
        mlflow.sklearn.autolog()

        # Log parameters
        mlflow.log_params(params)

        # Log dataset info
        mlflow.log_param("train_samples", len(X_train))
        mlflow.log_param("test_samples", len(X_test))
        mlflow.log_param("features", X_train.columns.tolist())

        # Train model
        logger.info("Training model...")
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)

        # Predictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)

        # Calculate metrics
        train_metrics = {
            "train_accuracy": accuracy_score(y_train, y_pred_train),
            "train_precision": precision_score(y_train, y_pred_train, average='weighted'),
            "train_recall": recall_score(y_train, y_pred_train, average='weighted'),
            "train_f1": f1_score(y_train, y_pred_train, average='weighted')
        }

        test_metrics = {
            "test_accuracy": accuracy_score(y_test, y_pred_test),
            "test_precision": precision_score(y_test, y_pred_test, average='weighted'),
            "test_recall": recall_score(y_test, y_pred_test, average='weighted'),
            "test_f1": f1_score(y_test, y_pred_test, average='weighted')
        }

        # Log metrics
        mlflow.log_metrics(train_metrics)
        mlflow.log_metrics(test_metrics)

        # Log model
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name=f"{CATALOG}.{SCHEMA}.{MODEL_NAME}",
            input_example=X_train.head(5),
            signature=mlflow.models.infer_signature(X_train, y_train)
        )

        logger.info(f"Model trained successfully. Run ID: {run.info.run_id}")
        logger.info(f"Test Accuracy: {test_metrics['test_accuracy']:.4f}")

        return run.info.run_id, model

# Main execution
if __name__ == "__main__":
    # Load data
    df = load_training_data(f"{CATALOG}.{SCHEMA}.training_data")

    # Feature columns (customize based on your data)
    feature_cols = [col for col in df.columns if col not in ['target', 'id', 'timestamp']]
    target_col = 'target'

    # Prepare data
    X_train, X_test, y_train, y_test = prepare_features(df, feature_cols, target_col)

    # Training parameters
    params = {
        'n_estimators': 100,
        'max_depth': 10,
        'min_samples_split': 5,
        'min_samples_leaf': 2,
        'random_state': 42,
        'n_jobs': -1
    }

    # Train model
    run_id, model = train_model(X_train, y_train, X_test, y_test, params)

    print(f"✓ Training completed successfully")
    print(f"✓ Run ID: {run_id}")
    print(f"✓ Model registered: {CATALOG}.{SCHEMA}.{MODEL_NAME}")
```

### 4. Distributed Training (for large datasets)

For distributed training with Spark ML or Horovod:

```python
from pyspark.ml.classification import RandomForestClassifier as SparkRF
from pyspark.ml.feature import VectorAssembler
from pyspark.ml import Pipeline

def train_distributed_model(training_table: str):
    """Train model using Spark ML for distributed processing"""

    # Load data
    df = spark.table(training_table)

    # Assemble features
    feature_cols = [col for col in df.columns if col not in ['target', 'id']]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

    # Create pipeline
    rf = SparkRF(
        labelCol="target",
        featuresCol="features",
        numTrees=100,
        maxDepth=10
    )

    pipeline = Pipeline(stages=[assembler, rf])

    # Train with MLflow tracking
    with mlflow.start_run():
        mlflow.log_param("num_trees", 100)
        mlflow.log_param("max_depth", 10)

        model = pipeline.fit(df)

        # Log model
        mlflow.spark.log_model(
            model,
            "spark-model",
            registered_model_name=f"{CATALOG}.{SCHEMA}.{MODEL_NAME}"
        )

    return model
```

### 5. Validation and Testing
- Split data appropriately (train/val/test)
- Calculate comprehensive metrics
- Create confusion matrix and ROC curves
- Log all artifacts to MLflow

### 6. Post-Training Steps
- Review experiment results in MLflow UI
- Compare with baseline models
- Document training results
- Prepare for model registration

## Best Practices

1. **Reproducibility**
   - Set random seeds
   - Log all parameters and dependencies
   - Version control training code
   - Document data versions

2. **Experiment Tracking**
   - Use descriptive experiment names
   - Tag runs with metadata
   - Log custom metrics
   - Save plots and artifacts

3. **Data Management**
   - Use Delta tables for data versioning
   - Implement data validation
   - Cache frequently accessed data
   - Use feature store when applicable

4. **Performance Optimization**
   - Use appropriate cluster sizes
   - Enable auto-scaling
   - Leverage distributed training for large datasets
   - Profile training jobs

5. **Model Validation**
   - Use holdout test set
   - Cross-validation for small datasets
   - Monitor for overfitting
   - Test on production-like data

## Integration Points

- **Feature Store**: Load features for training
- **Delta Lake**: Version controlled training data
- **MLflow**: Experiment tracking and model registry
- **Unity Catalog**: Model governance
- **Workflows**: Automated retraining pipelines

## Monitoring

Track these metrics during training:
- Training/validation loss curves
- Model performance metrics
- Resource utilization (CPU/GPU/memory)
- Training time and throughput
- Data quality metrics

## Next Steps

After training:
1. Use `/databricks-mlops:validate-model` to validate the trained model
2. Use `/databricks-mlops:register-model` to register to Model Registry
3. Use `/databricks-mlops:deploy-model` to deploy to serving endpoint

## Example Workflow

```bash
# 1. Train model
/databricks-mlops:train-model xgboost --experiment-name "/my-ml-project/training"

# 2. Validate model
/databricks-mlops:validate-model --run-id <run_id>

# 3. Register model
/databricks-mlops:register-model --run-id <run_id> --model-name "my_model"
```

## Troubleshooting

Common issues and solutions:
- **OOM errors**: Reduce batch size or increase cluster memory
- **Slow training**: Enable distributed training or use GPU instances
- **Poor metrics**: Check data quality, feature engineering, hyperparameters
- **MLflow errors**: Verify experiment permissions and workspace configuration

## References

- [Databricks ML Runtime](https://docs.databricks.com/runtime/mlruntime.html)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Distributed Training on Databricks](https://docs.databricks.com/machine-learning/train-model/distributed-training.html)
