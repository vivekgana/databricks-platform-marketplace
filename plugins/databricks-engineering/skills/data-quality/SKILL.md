---
name: data-quality
description: Comprehensive data quality patterns using Great Expectations, DLT expectations, and custom validators for ensuring data reliability and trust.
triggers:
  - data quality
  - great expectations
  - data validation
  - quality checks
  - data profiling
category: quality
---

# Data Quality Skill

## Overview

Data quality is critical for building trustworthy data products. This skill provides comprehensive patterns for implementing data quality checks using Great Expectations, DLT expectations, and custom validation frameworks.

**Key Benefits:**
- Automated data quality testing
- Comprehensive profiling and validation
- Integration with DLT pipelines
- Custom business rule validation
- Quality metrics and monitoring
- Data contract enforcement

## When to Use This Skill

Use data quality patterns when you need to:
- Validate data against business rules
- Profile datasets for quality metrics
- Implement comprehensive testing frameworks
- Monitor data quality over time
- Enforce data contracts between teams
- Prevent bad data from propagating
- Generate quality reports and alerts

## Core Concepts

### 1. Quality Dimensions

**Completeness**: Are all required fields present?
```python
# Check for null values
completeness_check = {
    "expectation": "expect_column_values_to_not_be_null",
    "kwargs": {"column": "customer_id"}
}
```

**Accuracy**: Does data match expected patterns?
```python
# Validate email format
accuracy_check = {
    "expectation": "expect_column_values_to_match_regex",
    "kwargs": {
        "column": "email",
        "regex": r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$"
    }
}
```

**Consistency**: Are values within expected ranges?
```python
# Check value ranges
consistency_check = {
    "expectation": "expect_column_values_to_be_between",
    "kwargs": {
        "column": "age",
        "min_value": 0,
        "max_value": 120
    }
}
```

**Uniqueness**: Are keys unique?
```python
# Check for duplicates
uniqueness_check = {
    "expectation": "expect_column_values_to_be_unique",
    "kwargs": {"column": "order_id"}
}
```

**Timeliness**: Is data fresh?
```python
# Check data freshness
timeliness_check = {
    "expectation": "expect_column_max_to_be_between",
    "kwargs": {
        "column": "ingestion_timestamp",
        "min_value": datetime.now() - timedelta(hours=2),
        "max_value": datetime.now()
    }
}
```

### 2. Great Expectations Integration

**Basic Setup:**
```python
import great_expectations as gx
from great_expectations.core.batch import RuntimeBatchRequest

# Initialize data context
context = gx.get_context()

# Create checkpoint
checkpoint_config = {
    "name": "sales_data_quality_check",
    "config_version": 1.0,
    "class_name": "SimpleCheckpoint",
    "validations": [
        {
            "batch_request": {
                "datasource_name": "spark_datasource",
                "data_connector_name": "runtime_connector",
                "data_asset_name": "sales_data"
            },
            "expectation_suite_name": "sales_quality_suite"
        }
    ]
}
```

**Expectation Suite:**
```python
# Create expectation suite
suite = context.create_expectation_suite(
    expectation_suite_name="sales_quality_suite",
    overwrite_existing=True
)

# Add expectations
suite.add_expectation(
    gx.core.ExpectationConfiguration(
        expectation_type="expect_table_row_count_to_be_between",
        kwargs={"min_value": 1000, "max_value": 1000000}
    )
)

suite.add_expectation(
    gx.core.ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "order_id"}
    )
)
```

### 3. DLT Quality Checks

**Multi-Level Expectations:**
```python
import dlt
from pyspark.sql.functions import *

@dlt.table(
    name="validated_orders",
    comment="Orders with comprehensive quality validation"
)
# Critical checks (fail pipeline)
@dlt.expect_or_fail("primary_key_not_null", "order_id IS NOT NULL")
@dlt.expect_or_fail("valid_customer_ref",
    "customer_id IN (SELECT customer_id FROM LIVE.customers)")

# Important checks (drop invalid rows)
@dlt.expect_or_drop("positive_amount", "order_amount > 0")
@dlt.expect_or_drop("valid_date_range",
    "order_date >= '2020-01-01' AND order_date <= current_date()")
@dlt.expect_or_drop("valid_status",
    "order_status IN ('pending', 'completed', 'cancelled')")

# Monitoring checks (warn only)
@dlt.expect("reasonable_amount", "order_amount < 100000")
@dlt.expect("same_day_processing",
    "datediff(processing_date, order_date) <= 1")

def validated_orders():
    return dlt.read_stream("raw_orders")
```

### 4. Custom Validators

**Business Rule Validators:**
```python
from typing import Dict, Any, List
from pyspark.sql import DataFrame
from pyspark.sql.functions import *

class BusinessRuleValidator:
    """Custom validator for complex business rules."""

    def __init__(self, spark_session):
        self.spark = spark_session
        self.validation_results = []

    def validate_order_logic(self, df: DataFrame) -> Dict[str, Any]:
        """Validate complex order business rules."""

        # Rule 1: Total matches sum of line items
        total_mismatch = df.filter(
            abs(col("order_total") - col("line_items_sum")) > 0.01
        ).count()

        # Rule 2: Discount doesn't exceed maximum allowed
        invalid_discount = df.filter(
            col("discount_amount") > col("order_subtotal") * 0.5
        ).count()

        # Rule 3: Shipping date after order date
        invalid_dates = df.filter(
            col("shipping_date") < col("order_date")
        ).count()

        return {
            "total_records": df.count(),
            "total_mismatch_count": total_mismatch,
            "invalid_discount_count": invalid_discount,
            "invalid_dates_count": invalid_dates,
            "pass_rate": (
                df.count() - total_mismatch - invalid_discount - invalid_dates
            ) / df.count() * 100
        }

    def validate_referential_integrity(
        self,
        df: DataFrame,
        reference_table: str,
        key_column: str
    ) -> Dict[str, Any]:
        """Check referential integrity constraints."""

        ref_df = self.spark.table(reference_table)

        # Find orphaned records
        orphaned = df.join(
            ref_df,
            df[key_column] == ref_df[key_column],
            "left_anti"
        )

        orphaned_count = orphaned.count()

        return {
            "total_records": df.count(),
            "orphaned_records": orphaned_count,
            "orphaned_percentage": orphaned_count / df.count() * 100,
            "valid": orphaned_count == 0
        }
```

## Implementation Patterns

### Pattern 1: Great Expectations Suite

**Complete Quality Suite:**
```python
"""
Great Expectations suite for customer data validation.
"""
import great_expectations as gx
from great_expectations.core.batch import RuntimeBatchRequest
from pyspark.sql import SparkSession
from typing import Dict, Any


class CustomerDataQualitySuite:
    """Comprehensive quality suite for customer data."""

    def __init__(self, context_root_dir: str = None):
        self.context = gx.get_context(context_root_dir=context_root_dir)
        self.suite_name = "customer_data_quality"

    def create_suite(self) -> gx.core.ExpectationSuite:
        """Create comprehensive expectation suite."""

        suite = self.context.create_expectation_suite(
            expectation_suite_name=self.suite_name,
            overwrite_existing=True
        )

        # Schema validation
        suite.add_expectation(
            gx.core.ExpectationConfiguration(
                expectation_type="expect_table_columns_to_match_ordered_list",
                kwargs={
                    "column_list": [
                        "customer_id",
                        "first_name",
                        "last_name",
                        "email",
                        "phone",
                        "registration_date",
                        "status",
                        "lifetime_value"
                    ]
                }
            )
        )

        # Completeness checks
        for col in ["customer_id", "email", "registration_date"]:
            suite.add_expectation(
                gx.core.ExpectationConfiguration(
                    expectation_type="expect_column_values_to_not_be_null",
                    kwargs={"column": col}
                )
            )

        # Uniqueness
        suite.add_expectation(
            gx.core.ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_unique",
                kwargs={"column": "customer_id"}
            )
        )

        suite.add_expectation(
            gx.core.ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_unique",
                kwargs={"column": "email"}
            )
        )

        # Format validation
        suite.add_expectation(
            gx.core.ExpectationConfiguration(
                expectation_type="expect_column_values_to_match_regex",
                kwargs={
                    "column": "email",
                    "regex": r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$"
                }
            )
        )

        suite.add_expectation(
            gx.core.ExpectationConfiguration(
                expectation_type="expect_column_values_to_match_regex",
                kwargs={
                    "column": "phone",
                    "regex": r"^\+?[1-9]\d{1,14}$",
                    "mostly": 0.95  # Allow 5% invalid
                }
            )
        )

        # Value constraints
        suite.add_expectation(
            gx.core.ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_in_set",
                kwargs={
                    "column": "status",
                    "value_set": ["active", "inactive", "suspended", "closed"]
                }
            )
        )

        suite.add_expectation(
            gx.core.ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_between",
                kwargs={
                    "column": "lifetime_value",
                    "min_value": 0,
                    "max_value": 1000000,
                    "mostly": 0.99
                }
            )
        )

        # Date validation
        suite.add_expectation(
            gx.core.ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_between",
                kwargs={
                    "column": "registration_date",
                    "min_value": "2020-01-01",
                    "max_value": "2026-12-31",
                    "parse_strings_as_datetimes": True
                }
            )
        )

        # Row count check
        suite.add_expectation(
            gx.core.ExpectationConfiguration(
                expectation_type="expect_table_row_count_to_be_between",
                kwargs={
                    "min_value": 100,
                    "max_value": 10000000
                }
            )
        )

        self.context.save_expectation_suite(suite)
        return suite

    def run_validation(self, df: DataFrame) -> Dict[str, Any]:
        """Run validation against dataframe."""

        # Create runtime batch request
        batch_request = RuntimeBatchRequest(
            datasource_name="spark_datasource",
            data_connector_name="runtime_connector",
            data_asset_name="customer_data",
            runtime_parameters={"batch_data": df},
            batch_identifiers={"default_identifier_name": "default_identifier"}
        )

        # Run checkpoint
        checkpoint_result = self.context.run_checkpoint(
            checkpoint_name="customer_data_checkpoint",
            validations=[
                {
                    "batch_request": batch_request,
                    "expectation_suite_name": self.suite_name
                }
            ]
        )

        return {
            "success": checkpoint_result.success,
            "statistics": checkpoint_result.run_results,
            "validation_results": checkpoint_result.to_json_dict()
        }
```

### Pattern 2: Custom Quality Framework

**Comprehensive Quality Framework:**
```python
"""
Custom data quality framework for comprehensive validation.
"""
from typing import Dict, List, Any, Callable, Optional
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import *
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class QualityRule:
    """Define a quality rule."""
    name: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    validation_func: Callable[[DataFrame], int]
    threshold: float = 1.0  # Pass rate threshold


@dataclass
class QualityResult:
    """Quality validation result."""
    rule_name: str
    passed: bool
    total_records: int
    failed_records: int
    pass_rate: float
    severity: str
    timestamp: datetime
    details: Dict[str, Any]


class DataQualityFramework:
    """Comprehensive data quality validation framework."""

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.rules: List[QualityRule] = []
        self.results: List[QualityResult] = []

    def add_rule(self, rule: QualityRule) -> None:
        """Add validation rule to framework."""
        self.rules.append(rule)

    def add_completeness_rule(
        self,
        column: str,
        severity: str = "high"
    ) -> None:
        """Add completeness check for a column."""

        def check(df: DataFrame) -> int:
            return df.filter(col(column).isNull()).count()

        self.add_rule(QualityRule(
            name=f"completeness_{column}",
            description=f"Check {column} has no null values",
            severity=severity,
            validation_func=check
        ))

    def add_uniqueness_rule(
        self,
        column: str,
        severity: str = "critical"
    ) -> None:
        """Add uniqueness check for a column."""

        def check(df: DataFrame) -> int:
            total = df.count()
            unique = df.select(column).distinct().count()
            return total - unique

        self.add_rule(QualityRule(
            name=f"uniqueness_{column}",
            description=f"Check {column} values are unique",
            severity=severity,
            validation_func=check
        ))

    def add_format_rule(
        self,
        column: str,
        regex_pattern: str,
        severity: str = "medium"
    ) -> None:
        """Add format validation rule."""

        def check(df: DataFrame) -> int:
            return df.filter(
                ~col(column).rlike(regex_pattern)
            ).count()

        self.add_rule(QualityRule(
            name=f"format_{column}",
            description=f"Check {column} matches pattern {regex_pattern}",
            severity=severity,
            validation_func=check
        ))

    def add_range_rule(
        self,
        column: str,
        min_value: Any,
        max_value: Any,
        severity: str = "medium"
    ) -> None:
        """Add range validation rule."""

        def check(df: DataFrame) -> int:
            return df.filter(
                (col(column) < min_value) | (col(column) > max_value)
            ).count()

        self.add_rule(QualityRule(
            name=f"range_{column}",
            description=f"Check {column} is between {min_value} and {max_value}",
            severity=severity,
            validation_func=check
        ))

    def add_referential_integrity_rule(
        self,
        column: str,
        reference_table: str,
        reference_column: str,
        severity: str = "critical"
    ) -> None:
        """Add referential integrity check."""

        def check(df: DataFrame) -> int:
            ref_df = self.spark.table(reference_table)
            orphaned = df.join(
                ref_df,
                df[column] == ref_df[reference_column],
                "left_anti"
            )
            return orphaned.count()

        self.add_rule(QualityRule(
            name=f"ref_integrity_{column}",
            description=f"Check {column} exists in {reference_table}.{reference_column}",
            severity=severity,
            validation_func=check
        ))

    def add_custom_rule(
        self,
        name: str,
        description: str,
        validation_func: Callable[[DataFrame], int],
        severity: str = "medium",
        threshold: float = 1.0
    ) -> None:
        """Add custom validation rule."""

        self.add_rule(QualityRule(
            name=name,
            description=description,
            severity=severity,
            validation_func=validation_func,
            threshold=threshold
        ))

    def validate(self, df: DataFrame) -> Dict[str, Any]:
        """Run all validation rules."""

        self.results = []
        total_records = df.count()

        for rule in self.rules:
            try:
                failed_count = rule.validation_func(df)
                pass_rate = (total_records - failed_count) / total_records * 100

                result = QualityResult(
                    rule_name=rule.name,
                    passed=pass_rate >= (rule.threshold * 100),
                    total_records=total_records,
                    failed_records=failed_count,
                    pass_rate=pass_rate,
                    severity=rule.severity,
                    timestamp=datetime.now(),
                    details={"description": rule.description}
                )

                self.results.append(result)

            except Exception as e:
                self.results.append(QualityResult(
                    rule_name=rule.name,
                    passed=False,
                    total_records=total_records,
                    failed_records=-1,
                    pass_rate=0.0,
                    severity=rule.severity,
                    timestamp=datetime.now(),
                    details={"error": str(e)}
                ))

        return self.get_summary()

    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary."""

        total_rules = len(self.results)
        passed_rules = sum(1 for r in self.results if r.passed)

        critical_failures = [
            r for r in self.results
            if not r.passed and r.severity == "critical"
        ]

        return {
            "timestamp": datetime.now().isoformat(),
            "total_rules": total_rules,
            "passed_rules": passed_rules,
            "failed_rules": total_rules - passed_rules,
            "pass_rate": passed_rules / total_rules * 100 if total_rules > 0 else 0,
            "critical_failures": len(critical_failures),
            "has_critical_failures": len(critical_failures) > 0,
            "results": [
                {
                    "rule": r.rule_name,
                    "passed": r.passed,
                    "pass_rate": r.pass_rate,
                    "failed_records": r.failed_records,
                    "severity": r.severity
                }
                for r in self.results
            ]
        }

    def save_results(self, output_path: str) -> None:
        """Save validation results to Delta table."""

        results_data = [
            {
                "rule_name": r.rule_name,
                "passed": r.passed,
                "total_records": r.total_records,
                "failed_records": r.failed_records,
                "pass_rate": r.pass_rate,
                "severity": r.severity,
                "timestamp": r.timestamp,
                "details": json.dumps(r.details)
            }
            for r in self.results
        ]

        results_df = self.spark.createDataFrame(results_data)
        results_df.write.format("delta").mode("append").save(output_path)
```

### Pattern 3: DLT Quality Monitoring

**Quality Metrics Collection:**
```python
"""
DLT pipeline with comprehensive quality monitoring.
"""
import dlt
from pyspark.sql.functions import *
from typing import Dict, Any


class DLTQualityMonitor:
    """Monitor data quality in DLT pipelines."""

    @staticmethod
    def create_quality_tables():
        """Create tables with quality monitoring."""

        @dlt.table(
            name="quality_metrics",
            comment="Quality metrics for all pipeline tables",
            table_properties={
                "quality": "monitoring",
                "delta.enableChangeDataFeed": "true"
            }
        )
        def quality_metrics():
            """Aggregate quality metrics across pipeline."""
            return spark.sql("""
                SELECT
                    current_timestamp() as metric_timestamp,
                    'bronze_orders' as table_name,
                    COUNT(*) as total_records,
                    COUNT_IF(order_id IS NULL) as null_order_ids,
                    COUNT_IF(amount <= 0) as invalid_amounts,
                    COUNT_IF(order_date > current_date()) as future_dates
                FROM LIVE.bronze_orders
            """)

        @dlt.table(
            name="orders_with_quality",
            comment="Orders with quality scores"
        )
        @dlt.expect("valid_order_id", "order_id IS NOT NULL")
        @dlt.expect_or_drop("positive_amount", "amount > 0")
        @dlt.expect("valid_email", "email RLIKE '^[A-Za-z0-9._%+-]+@'")
        def orders_with_quality():
            return (
                dlt.read_stream("bronze_orders")
                .withColumn(
                    "quality_score",
                    when(col("order_id").isNotNull(), 1).otherwise(0) +
                    when(col("amount") > 0, 1).otherwise(0) +
                    when(col("email").rlike("^[A-Za-z0-9._%+-]+@"), 1).otherwise(0)
                )
                .withColumn(
                    "quality_tier",
                    when(col("quality_score") >= 3, "high")
                    .when(col("quality_score") >= 2, "medium")
                    .otherwise("low")
                )
            )

    @staticmethod
    def get_quality_report(event_log_path: str) -> Dict[str, Any]:
        """Generate quality report from DLT event log."""

        events = spark.read.format("delta").load(event_log_path)

        # Extract expectation metrics
        expectations = (
            events
            .filter(col("event_type") == "flow_progress")
            .select(
                col("timestamp"),
                col("origin.flow_name").alias("table_name"),
                col("details.flow_progress.metrics.num_output_rows").alias("output_rows"),
                explode(col("details.flow_progress.data_quality.expectations")).alias("expectation")
            )
            .select(
                "timestamp",
                "table_name",
                "output_rows",
                col("expectation.name").alias("expectation_name"),
                col("expectation.passed_records").alias("passed"),
                col("expectation.failed_records").alias("failed")
            )
        )

        return {
            "total_tables": expectations.select("table_name").distinct().count(),
            "total_expectations": expectations.count(),
            "failed_expectations": expectations.filter(col("failed") > 0).count(),
            "details": expectations.collect()
        }
```

### Pattern 4: Data Profiling

**Comprehensive Profiling:**
```python
"""
Data profiling utilities for quality assessment.
"""
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import *
from typing import Dict, Any, List


class DataProfiler:
    """Profile datasets for quality assessment."""

    def __init__(self, spark: SparkSession):
        self.spark = spark

    def profile_dataset(self, df: DataFrame) -> Dict[str, Any]:
        """Generate comprehensive data profile."""

        profile = {
            "record_count": df.count(),
            "column_count": len(df.columns),
            "columns": {}
        }

        for column in df.columns:
            profile["columns"][column] = self.profile_column(df, column)

        return profile

    def profile_column(self, df: DataFrame, column: str) -> Dict[str, Any]:
        """Profile individual column."""

        col_type = df.schema[column].dataType.simpleString()

        base_stats = df.select(
            count(col(column)).alias("count"),
            count(when(col(column).isNull(), 1)).alias("null_count"),
            countDistinct(col(column)).alias("distinct_count")
        ).first()

        total_count = df.count()

        profile = {
            "type": col_type,
            "count": base_stats["count"],
            "null_count": base_stats["null_count"],
            "null_percentage": base_stats["null_count"] / total_count * 100,
            "distinct_count": base_stats["distinct_count"],
            "cardinality": base_stats["distinct_count"] / total_count
        }

        # Numeric profiling
        if col_type in ["int", "bigint", "double", "float", "decimal"]:
            numeric_stats = df.select(
                min(col(column)).alias("min"),
                max(col(column)).alias("max"),
                avg(col(column)).alias("mean"),
                stddev(col(column)).alias("stddev")
            ).first()

            profile.update({
                "min": numeric_stats["min"],
                "max": numeric_stats["max"],
                "mean": numeric_stats["mean"],
                "stddev": numeric_stats["stddev"]
            })

        # String profiling
        if col_type == "string":
            string_stats = df.select(
                min(length(col(column))).alias("min_length"),
                max(length(col(column))).alias("max_length"),
                avg(length(col(column))).alias("avg_length")
            ).first()

            profile.update({
                "min_length": string_stats["min_length"],
                "max_length": string_stats["max_length"],
                "avg_length": string_stats["avg_length"]
            })

            # Top values
            top_values = (
                df.groupBy(col(column))
                .count()
                .orderBy(desc("count"))
                .limit(10)
                .collect()
            )

            profile["top_values"] = [
                {"value": row[column], "count": row["count"]}
                for row in top_values
            ]

        return profile

    def detect_anomalies(self, df: DataFrame, column: str) -> DataFrame:
        """Detect anomalies using IQR method."""

        # Calculate quartiles
        quantiles = df.stat.approxQuantile(column, [0.25, 0.75], 0.05)
        q1, q3 = quantiles[0], quantiles[1]
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # Flag anomalies
        return df.withColumn(
            f"{column}_anomaly",
            when(
                (col(column) < lower_bound) | (col(column) > upper_bound),
                "anomaly"
            ).otherwise("normal")
        )

    def compare_distributions(
        self,
        df1: DataFrame,
        df2: DataFrame,
        column: str
    ) -> Dict[str, Any]:
        """Compare distributions between two datasets."""

        stats1 = df1.select(
            count(col(column)).alias("count"),
            avg(col(column)).alias("mean"),
            stddev(col(column)).alias("stddev")
        ).first()

        stats2 = df2.select(
            count(col(column)).alias("count"),
            avg(col(column)).alias("mean"),
            stddev(col(column)).alias("stddev")
        ).first()

        return {
            "dataset1": {
                "count": stats1["count"],
                "mean": stats1["mean"],
                "stddev": stats1["stddev"]
            },
            "dataset2": {
                "count": stats2["count"],
                "mean": stats2["mean"],
                "stddev": stats2["stddev"]
            },
            "mean_difference": abs(stats1["mean"] - stats2["mean"]),
            "stddev_difference": abs(stats1["stddev"] - stats2["stddev"])
        }
```

## Best Practices

### 1. Quality Rule Organization
```
/quality/
  ├── rules/
  │   ├── completeness_rules.py
  │   ├── accuracy_rules.py
  │   └── business_rules.py
  ├── suites/
  │   ├── customer_suite.py
  │   └── order_suite.py
  └── monitors/
      └── pipeline_monitor.py
```

### 2. Layered Quality Approach

**Bronze**: Schema and format validation
```python
@dlt.expect("valid_schema", "all required columns present")
```

**Silver**: Business rule validation
```python
@dlt.expect_or_drop("valid_business_key", "customer_id IS NOT NULL")
```

**Gold**: Aggregate and metric validation
```python
@dlt.expect("reasonable_totals", "daily_revenue < 10000000")
```

### 3. Quality Metrics

Track these key metrics:
- Completeness rate (% non-null)
- Accuracy rate (% matching patterns)
- Consistency rate (% within ranges)
- Uniqueness rate (% unique keys)
- Timeliness (data freshness)
- Validity (% passing business rules)

### 4. Alerting Strategy

```python
def check_quality_thresholds(quality_results: Dict[str, Any]) -> None:
    """Alert on quality threshold violations."""

    if quality_results["pass_rate"] < 95:
        send_alert(
            severity="high",
            message=f"Quality pass rate {quality_results['pass_rate']}% below threshold"
        )

    if quality_results["has_critical_failures"]:
        send_alert(
            severity="critical",
            message="Critical quality rules failed"
        )
```

## Complete Examples

See `/examples/` directory for:
- `customer_data_validation.py`: Complete customer data quality suite
- `pipeline_quality_monitoring.py`: DLT pipeline with quality monitoring

## Common Pitfalls to Avoid

Don't:
- Validate everything (focus on critical fields)
- Use only warning-level checks
- Ignore quality metrics over time
- Hard-code validation thresholds
- Skip profiling new data sources

Do:
- Prioritize rules by business impact
- Mix enforcement levels appropriately
- Track quality trends
- Make thresholds configurable
- Profile before implementing rules

## Related Skills

- `delta-live-tables`: DLT expectations
- `testing-patterns`: Quality testing
- `data-products`: Data contracts
- `medallion-architecture`: Layer-specific quality

## References

- [Great Expectations Docs](https://docs.greatexpectations.io/)
- [DLT Expectations](https://docs.databricks.com/delta-live-tables/expectations.html)
- [Data Quality Patterns](https://www.databricks.com/blog/2020/07/06/a-technical-introduction-to-data-quality.html)
