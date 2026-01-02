"""Data quality validation for data products."""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col
import json
import logging

logger = logging.getLogger(__name__)


class DataQualityValidator:
    """Validates data quality against contract specifications."""

    def __init__(self, catalog: str, schema: str, table: str):
        self.spark = SparkSession.builder.getOrCreate()
        self.catalog = catalog
        self.schema = schema
        self.table = table
        self.full_table_name = f"{catalog}.{schema}.{table}"

    def validate_all(self) -> dict:
        """Run all quality validations."""
        df = self.spark.table(self.full_table_name)

        report = {
            "table": self.full_table_name,
            "record_count": df.count(),
            "null_checks": self.check_nulls(df),
            "uniqueness_checks": self.check_uniqueness(df),
            "range_checks": self.check_ranges(df),
            "quality_score": 0.0,
        }

        # Calculate overall quality score
        passed_checks = sum(
            1
            for check in [
                report["null_checks"],
                report["uniqueness_checks"],
                report["range_checks"],
            ]
            if check.get("passed", False)
        )
        report["quality_score"] = (passed_checks / 3) * 100

        return report

    def check_nulls(self, df: DataFrame) -> dict:
        """Check for null values in required fields."""
        required_fields = ["customer_id", "email", "country"]
        null_counts = {}

        for field in required_fields:
            null_count = df.filter(col(field).isNull()).count()
            null_counts[field] = null_count

        passed = all(count == 0 for count in null_counts.values())
        return {"passed": passed, "null_counts": null_counts}

    def check_uniqueness(self, df: DataFrame) -> dict:
        """Check uniqueness constraints."""
        key_fields = ["customer_id"]
        total_count = df.count()
        distinct_count = df.select(key_fields).distinct().count()

        passed = total_count == distinct_count
        duplicates = total_count - distinct_count

        return {"passed": passed, "duplicate_count": duplicates}

    def check_ranges(self, df: DataFrame) -> dict:
        """Check value ranges."""
        violations = df.filter((col("lifetime_value") < 0) | (col("total_orders") < 0)).count()

        return {"passed": violations == 0, "violation_count": violations}

    def check_sla_compliance(self) -> dict:
        """Check SLA compliance."""
        df = self.spark.table(self.full_table_name)

        # Check freshness
        freshness_query = f"""
            SELECT MAX(TIMESTAMPDIFF(MINUTE, updated_at, CURRENT_TIMESTAMP())) as data_age
            FROM {self.full_table_name}
        """
        data_age = self.spark.sql(freshness_query).collect()[0]["data_age"]

        freshness_sla_met = data_age <= 60  # 1 hour SLA

        return {
            "freshness_sla_met": freshness_sla_met,
            "data_age_minutes": data_age,
            "sla_threshold_minutes": 60,
        }
