"""Model serving for batch and real-time inference."""

import mlflow
from pyspark.sql import SparkSession, DataFrame
from databricks.feature_store import FeatureStoreClient
import logging

logger = logging.getLogger(__name__)


class BatchScorer:
    """Handles batch inference using MLflow models."""

    def __init__(self, model_uri: str, feature_table: str):
        self.spark = SparkSession.builder.getOrCreate()
        self.model_uri = model_uri
        self.feature_table = feature_table
        self.fs = FeatureStoreClient()

    def score_batch(self, customer_ids: list) -> DataFrame:
        """
        Score a batch of customers.

        Args:
            customer_ids: List of customer IDs

        Returns:
            DataFrame with predictions
        """
        logger.info(f"Scoring batch of {len(customer_ids)} customers")

        # Load model
        model = mlflow.pyfunc.load_model(self.model_uri)

        # Get features
        features_df = self.fs.read_table(self.feature_table)
        features_df = features_df.filter(features_df.customer_id.isin(customer_ids))

        # Score
        predictions = self.fs.score_batch(
            model_uri=self.model_uri, df=features_df
        )

        logger.info("Batch scoring completed")
        return predictions


class RealtimeScorer:
    """Handles real-time inference."""

    def __init__(self, model_uri: str):
        self.model = mlflow.pyfunc.load_model(model_uri)

    def predict(self, features: dict) -> float:
        """
        Make real-time prediction.

        Args:
            features: Feature dictionary

        Returns:
            Prediction score
        """
        import pandas as pd

        features_df = pd.DataFrame([features])
        prediction = self.model.predict(features_df)[0]

        return prediction
