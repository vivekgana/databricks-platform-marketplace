# MLflow Project Template with Feature Store

**Document Version:** 1.0
**Last Updated:** 2026-01-01
**Template Type:** MLOps Pipeline

## Overview

This template provides a complete MLOps project with MLflow integration, feature engineering, model training, serving, and monitoring capabilities using Databricks Feature Store.

## Features

- **Feature Engineering**: Feature Store integration
- **Model Training**: Automated training with MLflow tracking
- **Model Registry**: Versioned model management
- **Model Serving**: Real-time and batch inference
- **Model Monitoring**: Performance and drift detection
- **Experiment Tracking**: Comprehensive experiment logging
- **CI/CD Integration**: Automated model deployment

## Project Structure

```
mlflow-project/
├── README.md
├── mlflow_project.yaml          # MLflow project configuration
├── src/
│   ├── __init__.py
│   ├── feature_engineering.py  # Feature creation
│   ├── model_training.py       # Model training
│   ├── model_serving.py        # Model deployment
│   └── monitoring.py           # Model monitoring
├── notebooks/
│   ├── 01_data_exploration.py
│   ├── 02_feature_engineering.py
│   ├── 03_model_training.py
│   └── 04_model_evaluation.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_features.py
│   └── test_model.py
├── databricks.yml
└── requirements.txt
```

## Quick Start

### 1. Set Up Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Set MLflow tracking URI
export MLFLOW_TRACKING_URI="databricks"
```

### 2. Create Features

```python
from src.feature_engineering import FeatureEngineer

fe = FeatureEngineer(catalog="main", schema="features")
fe.create_customer_features()
fe.register_feature_table("customer_features")
```

### 3. Train Model

```python
from src.model_training import ModelTrainer

trainer = ModelTrainer(
    experiment_name="/Shared/customer-churn",
    feature_table="main.features.customer_features"
)

model, metrics = trainer.train()
trainer.log_model(model, metrics)
```

### 4. Deploy Model

```bash
# Deploy to production
databricks bundle deploy -t prod

# Enable model serving endpoint
databricks serving-endpoints create \
  --name customer-churn-model \
  --config serving_config.json
```

## Feature Engineering

### Create Features

```python
import mlflow
from databricks.feature_store import FeatureStoreClient

fs = FeatureStoreClient()

# Create feature table
fs.create_table(
    name="main.features.customer_features",
    primary_keys=["customer_id"],
    df=customer_features_df,
    description="Customer behavioral features"
)
```

### Feature Computation

```python
from src.feature_engineering import compute_customer_features

features_df = compute_customer_features(
    transactions_df,
    interactions_df
)
```

## Model Training

### Train with MLflow

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier

with mlflow.start_run(run_name="churn-model-v1"):
    # Log parameters
    mlflow.log_param("n_estimators", 100)
    mlflow.log_param("max_depth", 10)

    # Train model
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)

    # Log metrics
    accuracy = model.score(X_test, y_test)
    mlflow.log_metric("accuracy", accuracy)

    # Log model
    mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name="customer_churn_model"
    )
```

### Hyperparameter Tuning

```python
from hyperopt import fmin, tpe, hp, Trials
import mlflow

space = {
    'n_estimators': hp.choice('n_estimators', [50, 100, 200]),
    'max_depth': hp.choice('max_depth', [5, 10, 15]),
    'min_samples_split': hp.choice('min_samples_split', [2, 5, 10])
}

with mlflow.start_run():
    best = fmin(
        fn=objective_function,
        space=space,
        algo=tpe.suggest,
        max_evals=50,
        trials=Trials()
    )
```

## Model Serving

### Batch Inference

```python
from src.model_serving import BatchScorer

scorer = BatchScorer(
    model_uri="models:/customer_churn_model/Production",
    feature_table="main.features.customer_features"
)

predictions = scorer.score_batch(customer_ids)
```

### Real-time Serving

```bash
# Create serving endpoint
databricks serving-endpoints create \
  --name churn-prediction-api \
  --model-name customer_churn_model \
  --model-version 3 \
  --workload-size Small

# Query endpoint
curl https://your-workspace.cloud.databricks.com/serving-endpoints/churn-prediction-api/invocations \
  -H "Authorization: Bearer $DATABRICKS_TOKEN" \
  -d '{"dataframe_records": [{"customer_id": "12345"}]}'
```

## Model Monitoring

### Track Model Performance

```python
from src.monitoring import ModelMonitor

monitor = ModelMonitor(
    model_name="customer_churn_model",
    serving_endpoint="churn-prediction-api"
)

# Log inference data
monitor.log_predictions(predictions, actuals)

# Check for drift
drift_report = monitor.detect_drift()

# Generate performance report
performance_report = monitor.generate_report()
```

### Alerting

```python
# Set up alerts for performance degradation
monitor.configure_alert(
    metric="accuracy",
    threshold=0.85,
    comparison="less_than",
    notification_channels=["email", "slack"]
)
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Test features
pytest tests/test_features.py -v

# Test model
pytest tests/test_model.py -v

# Test with coverage
pytest tests/ --cov=src --cov-report=html
```

## CI/CD Pipeline

### GitHub Actions Example

```yaml
name: ML Pipeline

on:
  push:
    branches: [main]

jobs:
  train-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Train Model
        run: |
          python src/model_training.py

      - name: Evaluate Model
        run: |
          python src/model_evaluation.py

      - name: Deploy Model
        if: success()
        run: |
          databricks bundle deploy -t prod
```

## Best Practices

1. **Version Everything**: Track code, data, and model versions
2. **Experiment Tracking**: Log all experiments with MLflow
3. **Feature Store**: Centralize feature engineering
4. **Model Registry**: Manage model lifecycle
5. **Automated Testing**: Test models before deployment
6. **Monitoring**: Continuously monitor model performance
7. **A/B Testing**: Compare model versions in production

## Model Governance

### Model Registry Workflow

```
Development → Staging → Production → Archived
```

### Transition Model Stages

```python
import mlflow

client = mlflow.tracking.MlflowClient()

# Transition to Staging
client.transition_model_version_stage(
    name="customer_churn_model",
    version=3,
    stage="Staging"
)

# Transition to Production after validation
client.transition_model_version_stage(
    name="customer_churn_model",
    version=3,
    stage="Production"
)
```

## Troubleshooting

### Model Training Fails
- Check feature table availability
- Verify data quality
- Review hyperparameter ranges

### Serving Endpoint Issues
- Check model version
- Verify endpoint configuration
- Review logs in serving endpoint UI

### Performance Degradation
- Check for data drift
- Review feature distributions
- Validate input data quality

## Documentation

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Databricks Feature Store](https://docs.databricks.com/machine-learning/feature-store/)
- [Model Serving](https://docs.databricks.com/machine-learning/model-serving/)

## License

This template is provided for use with Databricks ML projects.
