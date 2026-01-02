"""
Gold Layer - Business Aggregations

Creates business-level aggregates optimized for analytics and reporting.
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col,
    sum as spark_sum,
    avg,
    count,
    max as spark_max,
    min as spark_min,
    current_timestamp,
    window,
    date_trunc,
)
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class GoldAggregation:
    """Creates business-level aggregations for gold layer."""

    def __init__(self, catalog: str, schema: str):
        self.spark = SparkSession.builder.getOrCreate()
        self.catalog = catalog
        self.schema = schema
        logger.info(f"Initialized GoldAggregation for {catalog}.{schema}")

    def create_daily_metrics(
        self,
        source_table: str,
        target_table: str,
        date_column: str,
        group_by_columns: List[str],
        metric_columns: List[str],
    ) -> None:
        """
        Create daily aggregated metrics.

        Args:
            source_table: Source silver table
            target_table: Target gold table
            date_column: Column to use for daily grouping
            group_by_columns: Additional grouping columns
            metric_columns: Columns to aggregate
        """
        logger.info(f"Creating daily metrics from {source_table}")

        source_full_name = f"{self.catalog}.{self.schema}.{source_table}"
        target_full_name = f"{self.catalog}.{self.schema}.{target_table}"

        df = self.spark.table(source_full_name)

        # Group by date and additional columns
        agg_exprs = []
        for metric_col in metric_columns:
            agg_exprs.extend(
                [
                    spark_sum(col(metric_col)).alias(f"{metric_col}_sum"),
                    avg(col(metric_col)).alias(f"{metric_col}_avg"),
                    spark_max(col(metric_col)).alias(f"{metric_col}_max"),
                    spark_min(col(metric_col)).alias(f"{metric_col}_min"),
                    count(col(metric_col)).alias(f"{metric_col}_count"),
                ]
            )

        aggregated_df = (
            df.groupBy(col(date_column).cast("date"), *group_by_columns)
            .agg(*agg_exprs)
            .withColumn("aggregation_timestamp", current_timestamp())
        )

        aggregated_df.write.format("delta").mode("overwrite").option(
            "overwriteSchema", "true"
        ).saveAsTable(target_full_name)

        logger.info(f"Created daily metrics in {target_table}")

    def create_hourly_aggregates(
        self,
        source_table: str,
        target_table: str,
        timestamp_column: str,
        group_by_columns: List[str],
        metric_columns: List[str],
    ) -> None:
        """Create hourly time-series aggregates."""
        source_full_name = f"{self.catalog}.{self.schema}.{source_table}"
        target_full_name = f"{self.catalog}.{self.schema}.{target_table}"

        df = self.spark.table(source_full_name)

        # Truncate to hour
        df = df.withColumn("hour", date_trunc("hour", col(timestamp_column)))

        agg_exprs = []
        for metric_col in metric_columns:
            agg_exprs.extend(
                [
                    spark_sum(col(metric_col)).alias(f"{metric_col}_sum"),
                    avg(col(metric_col)).alias(f"{metric_col}_avg"),
                    count(col(metric_col)).alias(f"{metric_col}_count"),
                ]
            )

        aggregated_df = df.groupBy("hour", *group_by_columns).agg(*agg_exprs)

        aggregated_df.write.format("delta").mode("overwrite").partitionBy(
            "hour"
        ).saveAsTable(target_full_name)

        logger.info(f"Created hourly aggregates in {target_table}")
