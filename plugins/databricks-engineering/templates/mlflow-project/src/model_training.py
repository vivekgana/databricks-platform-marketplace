"""
Model Training with MLflow

Trains ML models with experiment tracking and model registry.
"""

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from databricks.feature_store import FeatureStoreClient
import logging

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Trains and logs ML models with MLflow."""

    def __init__(self, experiment_name: str, feature_table: str):
        self.experiment_name = experiment_name
        self.feature_table = feature_table
        self.fs = FeatureStoreClient()

        # Set MLflow experiment
        mlflow.set_experiment(experiment_name)

    def train(
        self,
        target_col: str = "churn",
        test_size: float = 0.2,
        n_estimators: int = 100,
        max_depth: int = 10,
    ) -> tuple:
        """
        Train model with MLflow tracking.

        Args:
            target_col: Target column name
            test_size: Test split size
            n_estimators: Number of trees
            max_depth: Max tree depth

        Returns:
            Tuple of (model, metrics)
        """
        logger.info("Starting model training")

        with mlflow.start_run(run_name="churn-model-training") as run:
            # Load features
            features_df = self.fs.read_table(name=self.feature_table)
            pandas_df = features_df.toPandas()

            # Prepare data
            X = pandas_df.drop(columns=[target_col, "customer_id"])
            y = pandas_df[target_col]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )

            # Log parameters
            mlflow.log_param("n_estimators", n_estimators)
            mlflow.log_param("max_depth", max_depth)
            mlflow.log_param("test_size", test_size)
            mlflow.log_param("feature_table", self.feature_table)

            # Train model
            model = RandomForestClassifier(
                n_estimators=n_estimators, max_depth=max_depth, random_state=42
            )

            model.fit(X_train, y_train)

            # Predictions
            y_pred = model.predict(X_test)

            # Calculate metrics
            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred),
                "recall": recall_score(y_test, y_pred),
                "f1": f1_score(y_test, y_pred),
            }

            # Log metrics
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)

            # Log model
            mlflow.sklearn.log_model(
                model,
                "model",
                registered_model_name="customer_churn_model",
            )

            # Log feature importance
            import pandas as pd

            feature_importance = pd.DataFrame(
                {"feature": X.columns, "importance": model.feature_importances_}
            ).sort_values("importance", ascending=False)

            mlflow.log_table(feature_importance, "feature_importance.json")

            logger.info(f"Model training completed. Run ID: {run.info.run_id}")
            logger.info(f"Metrics: {metrics}")

            return model, metrics

    def hyperparameter_tuning(self) -> dict:
        """
        Perform hyperparameter tuning with Hyperopt.

        Returns:
            Best hyperparameters
        """
        from hyperopt import fmin, tpe, hp, Trials, STATUS_OK

        def objective(params):
            with mlflow.start_run(nested=True):
                model, metrics = self.train(
                    n_estimators=int(params["n_estimators"]),
                    max_depth=int(params["max_depth"]),
                )

                return {"loss": -metrics["f1"], "status": STATUS_OK}

        space = {
            "n_estimators": hp.choice("n_estimators", [50, 100, 200]),
            "max_depth": hp.choice("max_depth", [5, 10, 15, 20]),
        }

        with mlflow.start_run(run_name="hyperparameter-tuning"):
            best = fmin(fn=objective, space=space, algo=tpe.suggest, max_evals=20)

        logger.info(f"Best hyperparameters: {best}")
        return best
