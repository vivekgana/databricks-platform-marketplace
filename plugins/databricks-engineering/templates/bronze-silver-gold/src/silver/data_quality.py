"""
Data Quality Checker for Silver Layer

Implements comprehensive data quality validations.
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, count, when, isnan, isnull, sum as spark_sum
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DataQualityChecker:
    """Performs data quality checks on silver layer data."""

    def __init__(self, catalog: str, schema: str):
        self.spark = SparkSession.builder.getOrCreate()
        self.catalog = catalog
        self.schema = schema

    def check_null_values(self, df: DataFrame, columns: List[str]) -> Dict[str, int]:
        """Check for null values in specified columns."""
        null_counts = {}

        for column in columns:
            null_count = df.filter(col(column).isNull()).count()
            null_counts[column] = null_count

            if null_count > 0:
                logger.warning(f"Column {column} has {null_count} null values")

        return null_counts

    def check_duplicates(self, df: DataFrame, key_columns: List[str]) -> int:
        """Check for duplicate records based on key columns."""
        total_count = df.count()
        distinct_count = df.select(key_columns).distinct().count()
        duplicates = total_count - distinct_count

        if duplicates > 0:
            logger.warning(f"Found {duplicates} duplicate records")

        return duplicates

    def check_data_ranges(
        self, df: DataFrame, range_checks: Dict[str, tuple]
    ) -> Dict[str, int]:
        """Check if numeric columns are within expected ranges."""
        violations = {}

        for column, (min_val, max_val) in range_checks.items():
            violation_count = df.filter(
                (col(column) < min_val) | (col(column) > max_val)
            ).count()

            violations[column] = violation_count

            if violation_count > 0:
                logger.warning(
                    f"Column {column} has {violation_count} values outside range [{min_val}, {max_val}]"
                )

        return violations

    def generate_quality_report(
        self, table_name: str, checks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive quality report."""
        table_full_name = f"{self.catalog}.{self.schema}.{table_name}"
        df = self.spark.table(table_full_name)

        report = {
            "table_name": table_name,
            "record_count": df.count(),
            "null_checks": {},
            "duplicate_checks": {},
            "range_checks": {},
        }

        if "null_columns" in checks:
            report["null_checks"] = self.check_null_values(df, checks["null_columns"])

        if "key_columns" in checks:
            report["duplicate_checks"] = self.check_duplicates(df, checks["key_columns"])

        if "range_checks" in checks:
            report["range_checks"] = self.check_data_ranges(df, checks["range_checks"])

        return report
