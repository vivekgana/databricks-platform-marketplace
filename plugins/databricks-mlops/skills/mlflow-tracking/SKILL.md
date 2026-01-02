# MLflow Tracking Skill

**Last Updated:** 2026-01-01 22:45:49
**Version:** 1.0.0
**Category:** Tracking

## Overview

Master MLflow experiment tracking patterns for reproducible ML workflows on Databricks. This skill covers experiment organization, parameter tracking, metric logging, artifact management, and model registration.

## Learning Objectives

By using this skill, you will understand:

1. **Experiment Organization**
   - Hierarchical experiment naming
   - Run organization strategies
   - Tag-based filtering
   - Nested runs for complex workflows

2. **Auto-logging**
   - Framework-specific auto-logging
   - Custom metric logging
   - Artifact capture
   - Configuration

3. **Model Packaging**
   - Model signatures
   - Input examples
   - Custom Python models
   - Dependencies management

4. **Model Registry Integration**
   - Model registration workflows
   - Version management
   - Stage transitions
   - Unity Catalog integration

## Key Patterns

### Pattern 1: Structured Experiment Tracking

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier

# Set hierarchical experiment
mlflow.set_experiment(f"/Users/{username}/projects/{project_name}/training")

# Start run with descriptive name
with mlflow.start_run(run_name=f"{model_type}_v{version}") as run:

    # Log dataset version
    mlflow.set_tag("data_version", "v2.1")
    mlflow.set_tag("feature_set", "standard")

    # Enable auto-logging
    mlflow.sklearn.autolog(log_input_examples=True, log_model_signatures=True)

    # Log hyperparameters
    params = {"n_estimators": 100, "max_depth": 10}
    mlflow.log_params(params)

    # Train model
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    # Log custom business metrics
    mlflow.log_metric("business_metric", calculate_business_value(model, X_test))

    # Log artifacts
    mlflow.log_artifact("feature_importance.png")
    mlflow.log_dict(feature_names, "features.json")

    print(f"Run ID: {run.info.run_id}")
```

### Pattern 2: Model Registration with Governance

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

def register_model_with_validation(run_id: str, model_name: str):
    """Register model with validation gates"""

    # Get run metrics
    run = client.get_run(run_id)
    metrics = run.data.metrics

    # Validation gate
    if metrics.get("test_accuracy", 0) < 0.85:
        raise ValueError("Model does not meet minimum accuracy threshold")

    # Register to Unity Catalog
    model_uri = f"runs:/{run_id}/model"
    full_name = f"catalog.schema.{model_name}"

    result = mlflow.register_model(
        model_uri=model_uri,
        name=full_name,
        tags={
            "source_run_id": run_id,
            "validation_status": "passed",
            "deployed_by": "ml_pipeline"
        }
    )

    return result
```

### Pattern 3: Custom Python Model

```python
import mlflow.pyfunc

class CustomModel(mlflow.pyfunc.PythonModel):
    """Custom model with preprocessing"""

    def load_context(self, context):
        """Load model and artifacts"""
        import joblib
        self.model = joblib.load(context.artifacts["model"])
        self.scaler = joblib.load(context.artifacts["scaler"])

    def predict(self, context, model_input):
        """Custom prediction logic"""
        # Preprocess
        scaled_input = self.scaler.transform(model_input)

        # Predict
        predictions = self.model.predict(scaled_input)

        # Post-process
        return self.post_process(predictions)

    def post_process(self, predictions):
        """Custom post-processing"""
        # Add business logic
        return predictions

# Log custom model
artifacts = {
    "model": "model.pkl",
    "scaler": "scaler.pkl"
}

mlflow.pyfunc.log_model(
    artifact_path="custom_model",
    python_model=CustomModel(),
    artifacts=artifacts
)
```

## Templates

- `experiment_tracking_template.py`: Complete experiment tracking example
- `model_registration_template.py`: Model registry workflow
- `custom_model_template.py`: Custom Python model pattern
- `nested_runs_template.py`: Nested runs for hyperparameter tuning

## Examples

- `sklearn_classification.py`: Scikit-learn classification with MLflow
- `xgboost_regression.py`: XGBoost regression tracking
- `pytorch_training.py`: PyTorch model tracking
- `hyperparameter_tuning.py`: Hyperopt integration

## Best Practices

1. **Always set experiment name** before starting runs
2. **Use descriptive run names** that indicate model type and version
3. **Log all hyperparameters** for reproducibility
4. **Include model signatures** for input validation
5. **Tag runs** with relevant metadata (data version, feature set, etc.)
6. **Log artifacts** (plots, reports, configs)
7. **Use Unity Catalog** for production models
8. **Version control** experiment code alongside tracking

## Common Pitfalls

- Forgetting to set experiment (uses default experiment)
- Not logging model signature (causes serving issues)
- Missing input examples (harder to debug)
- Not tagging runs (hard to filter/search)
- Logging too many artifacts (storage costs)

## Integration Points

- **Feature Store**: Track feature lineage
- **Model Serving**: Automatic endpoint updates
- **Workflows**: Automated training pipelines
- **Unity Catalog**: Model governance

## References

- [MLflow Tracking Documentation](https://mlflow.org/docs/latest/tracking.html)
- [Databricks MLflow Guide](https://docs.databricks.com/mlflow/tracking.html)
