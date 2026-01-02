"""
MLflow Experiment Tracking Template

This template provides a complete example of MLflow experiment tracking
with best practices for Databricks.
"""

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import pandas as pd

# Configuration
EXPERIMENT_NAME = "/Users/{username}/projects/{project_name}/training"
MODEL_NAME = "catalog.schema.model_name"

# Set experiment
mlflow.set_experiment(EXPERIMENT_NAME)

def train_and_track_model(X, y, params: dict):
    """Train model with comprehensive MLflow tracking"""

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Start MLflow run
    with mlflow.start_run(run_name=f"rf_model_{params['n_estimators']}") as run:

        # Log tags
        mlflow.set_tag("model_type", "random_forest")
        mlflow.set_tag("data_version", "v1.0")
        mlflow.set_tag("environment", "development")

        # Enable auto-logging
        mlflow.sklearn.autolog(
            log_input_examples=True,
            log_model_signatures=True,
            log_models=True
        )

        # Log parameters
        mlflow.log_params(params)
        mlflow.log_param("train_size", len(X_train))
        mlflow.log_param("test_size", len(X_test))

        # Train model
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)

        # Predictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)

        # Calculate metrics
        metrics = {
            "train_accuracy": accuracy_score(y_train, y_pred_train),
            "train_precision": precision_score(y_train, y_pred_train, average='weighted'),
            "test_accuracy": accuracy_score(y_test, y_pred_test),
            "test_precision": precision_score(y_test, y_pred_test, average='weighted'),
            "test_recall": recall_score(y_test, y_pred_test, average='weighted')
        }

        # Log metrics
        mlflow.log_metrics(metrics)

        # Log model with signature
        signature = mlflow.models.infer_signature(X_train, y_train)
        mlflow.sklearn.log_model(
            model,
            "model",
            signature=signature,
            input_example=X_train.head(5),
            registered_model_name=MODEL_NAME
        )

        print(f"Run ID: {run.info.run_id}")
        print(f"Test Accuracy: {metrics['test_accuracy']:.4f}")

        return run.info.run_id, model

if __name__ == "__main__":
    # Load your data
    # X, y = load_data()

    # Define parameters
    params = {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 5,
        "random_state": 42
    }

    # Train and track
    # run_id, model = train_and_track_model(X, y, params)
    pass
