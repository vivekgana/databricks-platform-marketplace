"""
Feature Engineering with Databricks Feature Store

Creates and manages ML features.
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, avg, count, sum as spark_sum, datediff, current_date
from databricks.feature_store import FeatureStoreClient
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Handles feature engineering and Feature Store operations."""

    def __init__(self, catalog: str, schema: str):
        self.spark = SparkSession.builder.getOrCreate()
        self.fs = FeatureStoreClient()
        self.catalog = catalog
        self.schema = schema

    def create_customer_features(
        self, transactions_df: DataFrame, interactions_df: DataFrame
    ) -> DataFrame:
        """
        Create customer behavioral features.

        Args:
            transactions_df: Customer transactions
            interactions_df: Customer interactions

        Returns:
            DataFrame with engineered features
        """
        logger.info("Creating customer features")

        # Transaction features
        transaction_features = (
            transactions_df.groupBy("customer_id")
            .agg(
                count("*").alias("total_transactions"),
                spark_sum("amount").alias("total_spend"),
                avg("amount").alias("avg_transaction_value"),
                datediff(current_date(), col("last_transaction_date")).alias(
                    "days_since_last_transaction"
                ),
            )
        )

        # Interaction features
        interaction_features = (
            interactions_df.groupBy("customer_id")
            .agg(
                count("*").alias("total_interactions"),
                spark_sum(col("duration")).alias("total_interaction_time"),
            )
        )

        # Combine features
        features_df = transaction_features.join(
            interaction_features, "customer_id", "left"
        ).fillna(0)

        # Derived features
        features_df = features_df.withColumn(
            "engagement_score",
            (col("total_transactions") * 0.5 + col("total_interactions") * 0.5),
        ).withColumn("avg_monthly_spend", col("total_spend") / 12)

        return features_df

    def register_feature_table(
        self, table_name: str, features_df: DataFrame, description: str = None
    ) -> None:
        """
        Register feature table in Feature Store.

        Args:
            table_name: Name of feature table
            features_df: DataFrame with features
            description: Table description
        """
        full_table_name = f"{self.catalog}.{self.schema}.{table_name}"

        logger.info(f"Registering feature table: {full_table_name}")

        try:
            # Create feature table
            self.fs.create_table(
                name=full_table_name,
                primary_keys=["customer_id"],
                df=features_df,
                description=description or f"Features for {table_name}",
            )

            logger.info(f"Successfully registered feature table: {full_table_name}")

        except Exception as e:
            # Table might already exist, update it
            logger.info(f"Updating existing feature table: {full_table_name}")
            self.fs.write_table(name=full_table_name, df=features_df, mode="merge")

    def get_features(
        self, table_name: str, customer_ids: list = None
    ) -> DataFrame:
        """
        Retrieve features from Feature Store.

        Args:
            table_name: Name of feature table
            customer_ids: Optional list of customer IDs to filter

        Returns:
            DataFrame with features
        """
        full_table_name = f"{self.catalog}.{self.schema}.{table_name}"

        features_df = self.fs.read_table(name=full_table_name)

        if customer_ids:
            features_df = features_df.filter(col("customer_id").isin(customer_ids))

        return features_df

    def compute_time_series_features(self, df: DataFrame, window_days: int = 30) -> DataFrame:
        """
        Compute time-series aggregated features.

        Args:
            df: Source DataFrame
            window_days: Window size in days

        Returns:
            DataFrame with time-series features
        """
        from pyspark.sql.window import Window

        window_spec = (
            Window.partitionBy("customer_id")
            .orderBy("event_date")
            .rangeBetween(-window_days * 86400, 0)
        )

        ts_features = df.withColumn(
            f"transactions_last_{window_days}d", count("*").over(window_spec)
        ).withColumn(f"spend_last_{window_days}d", spark_sum("amount").over(window_spec))

        return ts_features
