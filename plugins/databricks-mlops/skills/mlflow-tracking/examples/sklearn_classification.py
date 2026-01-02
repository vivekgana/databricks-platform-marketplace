"""
Complete Scikit-learn Classification Example with MLflow

Demonstrates end-to-end workflow with experiment tracking,
model registration, and validation.
"""

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Configuration
EXPERIMENT_NAME = "/ml-experiments/classification-demo"
CATALOG = "main"
SCHEMA = "ml_models"
MODEL_NAME = f"{CATALOG}.{SCHEMA}.demo_classifier"

# Initialize
mlflow.set_experiment(EXPERIMENT_NAME)
client = MlflowClient()

# Generate sample data
X, y = make_classification(
    n_samples=10000,
    n_features=20,
    n_informative=15,
    n_redundant=5,
    random_state=42
)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Training run
with mlflow.start_run(run_name="rf_classifier_v1") as run:

    # Enable auto-logging
    mlflow.sklearn.autolog()

    # Model parameters
    params = {
        "n_estimators": 100,
        "max_depth": 15,
        "min_samples_split": 5,
        "min_samples_leaf": 2,
        "random_state": 42
    }

    # Log additional metadata
    mlflow.log_params({
        "data_samples": len(X_train),
        "n_features": X_train.shape[1]
    })

    # Train model
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
    mlflow.log_metric("cv_mean_accuracy", cv_scores.mean())
    mlflow.log_metric("cv_std_accuracy", cv_scores.std())

    # Test predictions
    y_pred = model.predict(X_test)

    # Log classification report
    report = classification_report(y_test, y_pred, output_dict=True)
    mlflow.log_dict(report, "classification_report.json")

    # Create and log confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig('confusion_matrix.png')
    mlflow.log_artifact('confusion_matrix.png')

    # Log feature importance
    feature_importance = pd.DataFrame({
        'feature': [f'feature_{i}' for i in range(X_train.shape[1])],
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    mlflow.log_dict(feature_importance.to_dict(), "feature_importance.json")

    print(f"✓ Model trained successfully")
    print(f"✓ Run ID: {run.info.run_id}")
    print(f"✓ Test Accuracy: {model.score(X_test, y_test):.4f}")

# Register model
model_version = mlflow.register_model(
    model_uri=f"runs:/{run.info.run_id}/model",
    name=MODEL_NAME
)

print(f"✓ Model registered: {MODEL_NAME} v{model_version.version}")
