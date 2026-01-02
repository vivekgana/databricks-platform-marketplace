"""
Business Logic for Gold Layer

Implements domain-specific business rules and calculations.
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, when, lit, expr
import logging

logger = logging.getLogger(__name__)


class BusinessLogic:
    """Applies business logic and calculations."""

    def __init__(self, catalog: str, schema: str):
        self.spark = SparkSession.builder.getOrCreate()
        self.catalog = catalog
        self.schema = schema

    def apply_business_rules(self, df: DataFrame, rules: dict) -> DataFrame:
        """
        Apply business rules to DataFrame.

        Args:
            df: Source DataFrame
            rules: Dictionary of rule_name -> sql_expression

        Returns:
            DataFrame with business rules applied
        """
        result_df = df

        for rule_name, rule_expr in rules.items():
            result_df = result_df.withColumn(rule_name, expr(rule_expr))
            logger.info(f"Applied business rule: {rule_name}")

        return result_df

    def categorize_customers(self, df: DataFrame, revenue_column: str) -> DataFrame:
        """Example: Categorize customers by revenue."""
        return df.withColumn(
            "customer_segment",
            when(col(revenue_column) >= 100000, "Enterprise")
            .when(col(revenue_column) >= 10000, "Mid-Market")
            .when(col(revenue_column) >= 1000, "SMB")
            .otherwise("Starter"),
        )
