# Test Data Quality Command

## Description
Generate and execute comprehensive data quality tests using Great Expectations, custom PySpark validations, and Databricks Delta Live Tables expectations. Provides automated test generation, execution, reporting, and continuous monitoring integration.

## Usage
```bash
/databricks-engineering:test-data-quality [table-or-pipeline] [--framework framework] [--generate] [--execute] [--report]
```

## Parameters

- `table-or-pipeline` (required): Fully qualified table name (catalog.schema.table) or pipeline name
- `--framework` (optional): Testing framework - "great-expectations", "dlt", "custom", "all" (default: "great-expectations")
- `--generate` (optional): Generate test suites from table schemas and profiling (default: true)
- `--execute` (optional): Execute generated tests (default: true)
- `--report` (optional): Generate HTML/JSON test report (default: true)
- `--profile-data` (optional): Profile data to infer expectations (default: true)
- `--coverage-target` (optional): Target test coverage percentage (default: 80)
- `--severity` (optional): Minimum severity level - "critical", "high", "medium", "low" (default: "medium")
- `--continuous` (optional): Set up continuous monitoring (default: false)

## Examples

### Example 1: Comprehensive quality testing with generation
```bash
/databricks-engineering:test-data-quality main.sales.orders --generate --execute --report
```

### Example 2: Test specific pipeline
```bash
/databricks-engineering:test-data-quality customer-360-pipeline --framework all
```

### Example 3: Execute existing tests only
```bash
/databricks-engineering:test-data-quality main.sales.orders --generate false
```

### Example 4: Generate DLT expectations
```bash
/databricks-engineering:test-data-quality silver.transactions --framework dlt --continuous
```

### Example 5: Custom validation with high coverage
```bash
/databricks-engineering:test-data-quality gold.customer_metrics --framework custom --coverage-target 95
```

## What This Command Does

### Phase 1: Data Profiling (5-10 minutes)

1. **Schema Analysis**
   - Retrieves table schema and metadata
   - Identifies column data types
   - Detects nullable columns
   - Analyzes column names and patterns
   - Reviews table properties and constraints

2. **Statistical Profiling**
   - Calculates row counts and cardinality
   - Computes min/max/mean/median for numeric columns
   - Analyzes value distributions
   - Identifies unique and null value counts
   - Detects outliers and anomalies
   - Calculates correlation between columns

3. **Pattern Detection**
   - Identifies date/timestamp formats
   - Detects email/phone/ID patterns
   - Recognizes foreign key relationships
   - Identifies categorical columns
   - Detects hierarchical relationships

4. **Data Quality Baseline**
   - Records current data quality metrics
   - Establishes thresholds and SLAs
   - Documents business rules
   - Captures data lineage
   - Sets up monitoring baselines

### Phase 2: Test Generation (10-15 minutes)

#### Great Expectations Suite Generation
1. **Schema Expectations**
   ```python
   # Generated expectations
   expect_table_columns_to_match_ordered_list
   expect_column_values_to_be_of_type
   expect_column_values_to_not_be_null (for required columns)
   ```

2. **Data Integrity Expectations**
   ```python
   expect_column_values_to_be_unique (for primary keys)
   expect_column_values_to_be_in_set (for categorical data)
   expect_column_values_to_match_regex (for patterns)
   expect_compound_columns_to_be_unique (for composite keys)
   ```

3. **Statistical Expectations**
   ```python
   expect_column_min_to_be_between
   expect_column_max_to_be_between
   expect_column_mean_to_be_between
   expect_column_quantile_values_to_be_between
   expect_column_values_to_be_between (for ranges)
   ```

4. **Business Rule Expectations**
   ```python
   expect_column_pair_values_A_to_be_greater_than_B
   expect_multicolumn_sum_to_equal
   expect_column_values_to_match_strftime_format
   ```

#### DLT Expectations Generation
```python
# Generated DLT expectations
@dlt.expect("valid_order_id", "order_id IS NOT NULL")
@dlt.expect("positive_amount", "amount > 0")
@dlt.expect("valid_date", "order_date <= current_date()")
@dlt.expect_or_drop("valid_customer", "customer_id IN (SELECT id FROM customers)")
@dlt.expect_or_fail("critical_field", "status IN ('pending', 'completed', 'cancelled')")
```

#### Custom PySpark Validations
```python
# Generated custom validation functions
def validate_referential_integrity(df):
    """Validate foreign key relationships"""
    pass

def validate_business_logic(df):
    """Validate complex business rules"""
    pass

def validate_data_freshness(df):
    """Validate data is within SLA freshness"""
    pass
```

### Phase 3: Test Execution (5-20 minutes depending on data size)

1. **Test Suite Execution**
   - Runs Great Expectations checkpoint
   - Executes DLT pipeline with expectations
   - Runs custom validation functions
   - Collects test results and metrics
   - Captures failed records for analysis

2. **Performance Testing**
   - Measures test execution time
   - Monitors resource utilization
   - Validates test scalability
   - Identifies slow validations
   - Optimizes test performance

3. **Failure Analysis**
   - Categorizes failures by severity
   - Samples failed records
   - Identifies failure patterns
   - Generates remediation suggestions
   - Tracks failure trends

### Phase 4: Reporting (2-5 minutes)

1. **Executive Summary**
   - Overall quality score
   - Tests passed vs failed
   - Critical issues identified
   - Trend analysis
   - SLA compliance status

2. **Detailed Test Results**
   - Test-by-test breakdown
   - Failure details and examples
   - Statistical analysis
   - Visualization of distributions
   - Historical comparison

3. **Recommendations**
   - Data cleansing suggestions
   - Schema improvements
   - Pipeline enhancements
   - Monitoring setup
   - Remediation priorities

## Generated File Structure

```
tests/
├── data_quality/
│   ├── great_expectations/
│   │   ├── expectations/
│   │   │   ├── main_sales_orders_suite.json
│   │   │   └── validation_results/
│   │   ├── checkpoints/
│   │   │   └── main_sales_orders_checkpoint.yaml
│   │   └── great_expectations.yml
│   ├── dlt/
│   │   ├── orders_expectations.py
│   │   └── expectations_config.yaml
│   ├── custom/
│   │   ├── business_rules.py
│   │   ├── referential_integrity.py
│   │   └── data_freshness.py
│   └── reports/
│       ├── quality_report_2024-12-31.html
│       ├── quality_metrics.json
│       └── failed_records/
│           └── orders_failures.csv
├── fixtures/
│   └── quality_test_fixtures.py
└── conftest.py

docs/
└── data_quality/
    ├── main_sales_orders_profile.md
    ├── quality_standards.md
    └── monitoring_setup.md
```

## Great Expectations Integration

### Generated Expectation Suite Example
```json
{
  "expectation_suite_name": "main.sales.orders",
  "data_asset_type": "Dataset",
  "meta": {
    "great_expectations_version": "0.18.0",
    "generated_by": "databricks-engineering-plugin",
    "created_at": "2024-12-31T10:30:00Z"
  },
  "expectations": [
    {
      "expectation_type": "expect_table_row_count_to_be_between",
      "kwargs": {
        "min_value": 1000,
        "max_value": 1000000
      },
      "meta": {
        "severity": "critical",
        "notes": "Expected daily order volume"
      }
    },
    {
      "expectation_type": "expect_column_values_to_not_be_null",
      "kwargs": {
        "column": "order_id"
      },
      "meta": {
        "severity": "critical",
        "notes": "Primary key must not be null"
      }
    },
    {
      "expectation_type": "expect_column_values_to_be_unique",
      "kwargs": {
        "column": "order_id"
      },
      "meta": {
        "severity": "critical",
        "notes": "Primary key must be unique"
      }
    },
    {
      "expectation_type": "expect_column_values_to_be_in_set",
      "kwargs": {
        "column": "status",
        "value_set": ["pending", "processing", "completed", "cancelled", "refunded"]
      },
      "meta": {
        "severity": "high",
        "notes": "Valid order statuses"
      }
    },
    {
      "expectation_type": "expect_column_values_to_be_between",
      "kwargs": {
        "column": "amount",
        "min_value": 0,
        "max_value": 1000000,
        "mostly": 0.99
      },
      "meta": {
        "severity": "high",
        "notes": "Order amounts should be positive and reasonable"
      }
    },
    {
      "expectation_type": "expect_column_values_to_match_strftime_format",
      "kwargs": {
        "column": "order_date",
        "strftime_format": "%Y-%m-%d"
      },
      "meta": {
        "severity": "medium",
        "notes": "Date format standardization"
      }
    },
    {
      "expectation_type": "expect_column_pair_values_A_to_be_greater_than_B",
      "kwargs": {
        "column_A": "delivery_date",
        "column_B": "order_date",
        "mostly": 0.95
      },
      "meta": {
        "severity": "high",
        "notes": "Delivery date must be after order date"
      }
    }
  ]
}
```

### Generated Checkpoint Configuration
```yaml
# main_sales_orders_checkpoint.yaml
name: main_sales_orders_checkpoint
config_version: 1.0
class_name: SimpleCheckpoint
validations:
  - batch_request:
      datasource_name: databricks_datasource
      data_connector_name: default_inferred_data_connector_name
      data_asset_name: main.sales.orders
      batch_identifiers:
        timestamp: latest
    expectation_suite_name: main.sales.orders
    action_list:
      - name: store_validation_result
        action:
          class_name: StoreValidationResultAction
      - name: update_data_docs
        action:
          class_name: UpdateDataDocsAction
      - name: send_slack_notification
        action:
          class_name: SlackNotificationAction
          slack_webhook: ${SLACK_WEBHOOK_URL}
          notify_on: failure
```

### Generated Databricks Integration
```python
# src/quality/orders_quality_tests.py
"""
Data quality tests for main.sales.orders
Generated by databricks-engineering plugin
"""

from great_expectations.data_context import DataContext
from great_expectations.core.batch import RuntimeBatchRequest
from pyspark.sql import SparkSession
import logging

logger = logging.getLogger(__name__)


class OrdersQualityValidator:
    """Quality validator for orders table"""

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.context = DataContext("/Workspace/great_expectations")
        self.table_name = "main.sales.orders"
        self.checkpoint_name = "main_sales_orders_checkpoint"

    def run_validation(self):
        """Execute quality validation checkpoint"""
        try:
            # Create batch request
            batch_request = RuntimeBatchRequest(
                datasource_name="databricks_datasource",
                data_connector_name="default_runtime_data_connector_name",
                data_asset_name=self.table_name,
                runtime_parameters={
                    "batch_data": self.spark.table(self.table_name)
                },
                batch_identifiers={
                    "timestamp": self._get_current_timestamp()
                }
            )

            # Run checkpoint
            results = self.context.run_checkpoint(
                checkpoint_name=self.checkpoint_name,
                validations=[{
                    "batch_request": batch_request
                }]
            )

            # Process results
            if results.success:
                logger.info(f"✓ Quality validation passed for {self.table_name}")
                return True, results
            else:
                logger.error(f"✗ Quality validation failed for {self.table_name}")
                self._log_failures(results)
                return False, results

        except Exception as e:
            logger.error(f"Error running validation: {str(e)}")
            raise

    def _log_failures(self, results):
        """Log detailed failure information"""
        for validation in results.run_results.values():
            for result in validation["validation_result"]["results"]:
                if not result["success"]:
                    logger.error(f"Failed expectation: {result['expectation_config']['expectation_type']}")
                    logger.error(f"Details: {result.get('result', {})}")

    def _get_current_timestamp(self):
        """Get current timestamp for batch identifier"""
        from datetime import datetime
        return datetime.now().isoformat()

    def get_quality_metrics(self):
        """Get quality metrics for monitoring"""
        df = self.spark.table(self.table_name)

        metrics = {
            "row_count": df.count(),
            "column_count": len(df.columns),
            "null_counts": {
                col: df.filter(df[col].isNull()).count()
                for col in df.columns
            },
            "duplicate_count": df.count() - df.dropDuplicates().count(),
            "timestamp": self._get_current_timestamp()
        }

        return metrics


# Databricks notebook integration
if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    validator = OrdersQualityValidator(spark)

    # Run validation
    success, results = validator.run_validation()

    # Get metrics
    metrics = validator.get_quality_metrics()

    # Log to MLflow
    import mlflow
    with mlflow.start_run(run_name="quality_validation"):
        mlflow.log_metrics({
            "quality_score": results.success,
            "row_count": metrics["row_count"],
            "duplicate_count": metrics["duplicate_count"]
        })
        mlflow.log_dict(metrics, "quality_metrics.json")

    # Exit with appropriate code
    dbutils.notebook.exit("success" if success else "failure")
```

## DLT Expectations Integration

### Generated DLT Pipeline with Expectations
```python
# pipelines/orders_dlt_with_quality.py
"""
DLT pipeline with data quality expectations
Generated by databricks-engineering plugin
"""

import dlt
from pyspark.sql import functions as F
from pyspark.sql.types import *


# Bronze layer - raw ingestion with basic quality checks
@dlt.table(
    name="bronze_orders",
    comment="Raw orders data with quality expectations",
    table_properties={
        "quality": "bronze",
        "pipelines.autoOptimize.zOrderCols": "order_date"
    }
)
@dlt.expect("valid_order_id", "order_id IS NOT NULL")
@dlt.expect("valid_json_structure", "from_json IS NOT NULL")
def bronze_orders():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", "/mnt/schemas/orders")
        .load("/mnt/raw/orders")
        .withColumn("ingest_timestamp", F.current_timestamp())
        .withColumn("source_file", F.input_file_name())
    )


# Silver layer - cleaned data with comprehensive quality checks
@dlt.table(
    name="silver_orders",
    comment="Cleaned orders with comprehensive quality expectations",
    table_properties={
        "quality": "silver",
        "pipelines.autoOptimize.zOrderCols": "order_date,customer_id"
    }
)
# Critical expectations - fail pipeline if violated
@dlt.expect_or_fail("valid_order_id", "order_id IS NOT NULL")
@dlt.expect_or_fail("unique_order_id", "order_id IS NOT NULL")
@dlt.expect_or_fail("valid_status", "status IN ('pending', 'processing', 'completed', 'cancelled', 'refunded')")

# High severity - drop records if violated
@dlt.expect_or_drop("valid_customer", "customer_id IS NOT NULL")
@dlt.expect_or_drop("positive_amount", "amount > 0")
@dlt.expect_or_drop("valid_date_range", "order_date >= '2020-01-01' AND order_date <= current_date()")

# Medium severity - track violations but allow
@dlt.expect("reasonable_amount", "amount <= 1000000")
@dlt.expect("valid_email", "email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}$'")
@dlt.expect("valid_phone", "phone RLIKE '^\\\\+?[1-9]\\\\d{1,14}$'")
@dlt.expect("delivery_after_order", "delivery_date IS NULL OR delivery_date >= order_date")
def silver_orders():
    return (
        dlt.read_stream("bronze_orders")
        .select(
            "order_id",
            "customer_id",
            "order_date",
            F.to_date("order_date").alias("order_date_clean"),
            "amount",
            F.round(F.col("amount"), 2).alias("amount_clean"),
            "status",
            F.lower(F.trim(F.col("status"))).alias("status_clean"),
            "email",
            F.lower(F.trim(F.col("email"))).alias("email_clean"),
            "phone",
            "delivery_date",
            "ingest_timestamp"
        )
        .withColumn("processing_timestamp", F.current_timestamp())
    )


# Gold layer - aggregated metrics with business rule expectations
@dlt.table(
    name="gold_daily_order_metrics",
    comment="Daily order aggregations with business rule expectations",
    table_properties={
        "quality": "gold"
    }
)
@dlt.expect("minimum_orders", "total_orders >= 100")
@dlt.expect("reasonable_avg_amount", "avg_order_amount BETWEEN 10 AND 10000")
@dlt.expect("positive_revenue", "total_revenue > 0")
def gold_daily_order_metrics():
    return (
        dlt.read_stream("silver_orders")
        .groupBy("order_date")
        .agg(
            F.count("*").alias("total_orders"),
            F.sum("amount").alias("total_revenue"),
            F.avg("amount").alias("avg_order_amount"),
            F.countDistinct("customer_id").alias("unique_customers"),
            F.count(F.when(F.col("status") == "completed", 1)).alias("completed_orders"),
            F.count(F.when(F.col("status") == "cancelled", 1)).alias("cancelled_orders")
        )
        .withColumn("completion_rate", F.col("completed_orders") / F.col("total_orders"))
        .withColumn("cancellation_rate", F.col("cancelled_orders") / F.col("total_orders"))
    )


# Quality metrics tracking table
@dlt.table(
    name="quality_metrics",
    comment="Data quality metrics over time"
)
def quality_metrics():
    """Track data quality metrics for monitoring"""
    return (
        dlt.read_stream("silver_orders")
        .select(
            F.current_timestamp().alias("check_timestamp"),
            F.lit("silver_orders").alias("table_name"),
            F.count("*").alias("total_records"),
            F.sum(F.when(F.col("amount").isNull(), 1).otherwise(0)).alias("null_amount_count"),
            F.sum(F.when(F.col("customer_id").isNull(), 1).otherwise(0)).alias("null_customer_count"),
            F.sum(F.when(F.col("email").rlike("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}$"), 0).otherwise(1)).alias("invalid_email_count")
        )
    )
```

### DLT Expectations Configuration
```yaml
# config/dlt_expectations.yaml
expectations:
  critical:
    - name: valid_order_id
      expectation: "order_id IS NOT NULL"
      action: fail
      description: "Order ID is required for all records"

    - name: valid_status
      expectation: "status IN ('pending', 'processing', 'completed', 'cancelled', 'refunded')"
      action: fail
      description: "Status must be one of the valid values"

  high:
    - name: valid_customer
      expectation: "customer_id IS NOT NULL"
      action: drop
      description: "Customer ID required for processing"

    - name: positive_amount
      expectation: "amount > 0"
      action: drop
      description: "Order amount must be positive"

    - name: valid_date_range
      expectation: "order_date >= '2020-01-01' AND order_date <= current_date()"
      action: drop
      description: "Order date must be within valid range"

  medium:
    - name: reasonable_amount
      expectation: "amount <= 1000000"
      action: track
      description: "Flag unusually large orders for review"

    - name: valid_email
      expectation: "email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}$'"
      action: track
      description: "Email should match standard format"

monitoring:
  enable: true
  alert_on_failure: true
  slack_webhook: ${SLACK_WEBHOOK_URL}
  email_recipients:
    - data-engineering@company.com
  sla_threshold: 0.95  # 95% of expectations must pass
```

## Custom Validation Functions

### Generated Custom Validators
```python
# src/quality/custom_validators.py
"""
Custom data quality validation functions
Generated by databricks-engineering plugin
"""

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class CustomQualityValidator:
    """Custom quality validation rules for orders"""

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.validation_results = []

    def validate_referential_integrity(
        self,
        orders_df: DataFrame,
        customers_df: DataFrame
    ) -> Tuple[bool, Dict]:
        """Validate foreign key relationships"""
        logger.info("Validating referential integrity...")

        # Check for orphaned orders
        orphaned_orders = (
            orders_df
            .join(customers_df, orders_df.customer_id == customers_df.id, "left_anti")
        )

        orphaned_count = orphaned_orders.count()
        total_count = orders_df.count()

        result = {
            "validation": "referential_integrity",
            "passed": orphaned_count == 0,
            "total_records": total_count,
            "orphaned_records": orphaned_count,
            "orphaned_percentage": (orphaned_count / total_count * 100) if total_count > 0 else 0,
            "severity": "critical" if orphaned_count > 0 else "info"
        }

        self.validation_results.append(result)
        return result["passed"], result

    def validate_business_logic(self, df: DataFrame) -> Tuple[bool, Dict]:
        """Validate complex business rules"""
        logger.info("Validating business logic...")

        violations = []

        # Rule 1: Completed orders must have delivery date
        completed_no_delivery = df.filter(
            (F.col("status") == "completed") & F.col("delivery_date").isNull()
        ).count()

        if completed_no_delivery > 0:
            violations.append({
                "rule": "completed_orders_delivery_date",
                "description": "Completed orders must have delivery date",
                "violation_count": completed_no_delivery
            })

        # Rule 2: Cancelled orders should not have delivery date
        cancelled_with_delivery = df.filter(
            (F.col("status") == "cancelled") & F.col("delivery_date").isNotNull()
        ).count()

        if cancelled_with_delivery > 0:
            violations.append({
                "rule": "cancelled_orders_no_delivery",
                "description": "Cancelled orders should not have delivery date",
                "violation_count": cancelled_with_delivery
            })

        # Rule 3: Refund amount should not exceed order amount
        invalid_refunds = df.filter(
            F.col("refund_amount") > F.col("amount")
        ).count()

        if invalid_refunds > 0:
            violations.append({
                "rule": "refund_amount_validation",
                "description": "Refund amount cannot exceed order amount",
                "violation_count": invalid_refunds
            })

        result = {
            "validation": "business_logic",
            "passed": len(violations) == 0,
            "total_rules_checked": 3,
            "violations": violations,
            "severity": "high" if violations else "info"
        }

        self.validation_results.append(result)
        return result["passed"], result

    def validate_data_freshness(
        self,
        df: DataFrame,
        max_age_hours: int = 24
    ) -> Tuple[bool, Dict]:
        """Validate data is within SLA freshness"""
        logger.info("Validating data freshness...")

        max_order_date = df.agg(F.max("order_date")).collect()[0][0]
        current_date = self.spark.sql("SELECT current_date()").collect()[0][0]

        if max_order_date:
            age_hours = (current_date - max_order_date).total_seconds() / 3600
            is_fresh = age_hours <= max_age_hours

            result = {
                "validation": "data_freshness",
                "passed": is_fresh,
                "max_order_date": str(max_order_date),
                "current_date": str(current_date),
                "age_hours": age_hours,
                "sla_hours": max_age_hours,
                "severity": "critical" if not is_fresh else "info"
            }
        else:
            result = {
                "validation": "data_freshness",
                "passed": False,
                "error": "No order dates found",
                "severity": "critical"
            }

        self.validation_results.append(result)
        return result["passed"], result

    def validate_data_completeness(self, df: DataFrame) -> Tuple[bool, Dict]:
        """Validate data completeness across columns"""
        logger.info("Validating data completeness...")

        total_rows = df.count()
        completeness_by_column = {}

        for column in df.columns:
            non_null_count = df.filter(F.col(column).isNotNull()).count()
            completeness_pct = (non_null_count / total_rows * 100) if total_rows > 0 else 0
            completeness_by_column[column] = {
                "non_null_count": non_null_count,
                "null_count": total_rows - non_null_count,
                "completeness_percentage": completeness_pct
            }

        # Flag columns with >10% null values
        incomplete_columns = [
            col for col, metrics in completeness_by_column.items()
            if metrics["completeness_percentage"] < 90
        ]

        result = {
            "validation": "data_completeness",
            "passed": len(incomplete_columns) == 0,
            "total_columns": len(df.columns),
            "incomplete_columns": incomplete_columns,
            "completeness_by_column": completeness_by_column,
            "severity": "medium" if incomplete_columns else "info"
        }

        self.validation_results.append(result)
        return result["passed"], result

    def validate_statistical_distribution(
        self,
        df: DataFrame,
        column: str,
        expected_mean: float,
        tolerance: float = 0.1
    ) -> Tuple[bool, Dict]:
        """Validate statistical distribution hasn't drifted"""
        logger.info(f"Validating statistical distribution for {column}...")

        stats = df.agg(
            F.mean(column).alias("mean"),
            F.stddev(column).alias("stddev"),
            F.min(column).alias("min"),
            F.max(column).alias("max")
        ).collect()[0]

        actual_mean = stats["mean"]
        deviation = abs(actual_mean - expected_mean) / expected_mean if expected_mean != 0 else 0

        result = {
            "validation": f"statistical_distribution_{column}",
            "passed": deviation <= tolerance,
            "column": column,
            "expected_mean": expected_mean,
            "actual_mean": actual_mean,
            "deviation": deviation,
            "tolerance": tolerance,
            "stddev": stats["stddev"],
            "min": stats["min"],
            "max": stats["max"],
            "severity": "medium" if deviation > tolerance else "info"
        }

        self.validation_results.append(result)
        return result["passed"], result

    def get_validation_summary(self) -> Dict:
        """Get summary of all validations"""
        total_validations = len(self.validation_results)
        passed_validations = sum(1 for r in self.validation_results if r["passed"])

        critical_failures = [r for r in self.validation_results if not r["passed"] and r["severity"] == "critical"]
        high_failures = [r for r in self.validation_results if not r["passed"] and r["severity"] == "high"]
        medium_failures = [r for r in self.validation_results if not r["passed"] and r["severity"] == "medium"]

        return {
            "total_validations": total_validations,
            "passed_validations": passed_validations,
            "failed_validations": total_validations - passed_validations,
            "success_rate": (passed_validations / total_validations * 100) if total_validations > 0 else 0,
            "critical_failures": len(critical_failures),
            "high_failures": len(high_failures),
            "medium_failures": len(medium_failures),
            "overall_passed": len(critical_failures) == 0 and len(high_failures) == 0,
            "validation_results": self.validation_results
        }


# Example usage in Databricks notebook
if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    validator = CustomQualityValidator(spark)

    # Load data
    orders_df = spark.table("main.sales.orders")
    customers_df = spark.table("main.sales.customers")

    # Run validations
    validator.validate_referential_integrity(orders_df, customers_df)
    validator.validate_business_logic(orders_df)
    validator.validate_data_freshness(orders_df, max_age_hours=24)
    validator.validate_data_completeness(orders_df)
    validator.validate_statistical_distribution(orders_df, "amount", expected_mean=150.0, tolerance=0.15)

    # Get summary
    summary = validator.get_validation_summary()

    # Log results
    print(f"Quality Validation Summary:")
    print(f"  Total Validations: {summary['total_validations']}")
    print(f"  Passed: {summary['passed_validations']}")
    print(f"  Failed: {summary['failed_validations']}")
    print(f"  Success Rate: {summary['success_rate']:.2f}%")
    print(f"  Critical Failures: {summary['critical_failures']}")
    print(f"  Overall Status: {'✓ PASSED' if summary['overall_passed'] else '✗ FAILED'}")

    # Exit with status
    dbutils.notebook.exit("success" if summary['overall_passed'] else "failure")
```

## Test Report Generation

### HTML Report Template
The command generates a comprehensive HTML report with:
- Executive dashboard with quality score
- Test results by category
- Failed record samples
- Trend analysis charts
- Downloadable CSV of failures
- Remediation recommendations

### JSON Report for Automation
```json
{
  "report_metadata": {
    "generated_at": "2024-12-31T10:30:00Z",
    "table_name": "main.sales.orders",
    "framework": "all",
    "execution_time_seconds": 145
  },
  "quality_score": {
    "overall": 94.5,
    "critical_tests": 100,
    "high_severity_tests": 92.3,
    "medium_severity_tests": 88.7
  },
  "test_results": {
    "total_tests": 45,
    "passed": 42,
    "failed": 3,
    "skipped": 0
  },
  "failures": [
    {
      "test_name": "expect_column_values_to_match_regex",
      "column": "email",
      "severity": "medium",
      "failed_records": 127,
      "sample_failures": ["user@", "invalid.email", "@domain.com"]
    }
  ],
  "recommendations": [
    "Implement email validation at ingestion",
    "Add data cleansing step for email normalization",
    "Set up monitoring alert for email validation failures"
  ]
}
```

## Continuous Monitoring Setup

When `--continuous` flag is used, the command sets up:

1. **Scheduled Quality Checks**
   - Daily validation jobs
   - Real-time DLT expectations
   - Alerting on failures

2. **Quality Metrics Tracking**
   - Historical quality score
   - Trend analysis
   - SLA compliance tracking

3. **Automated Remediation**
   - Auto-quarantine failed records
   - Trigger data cleansing workflows
   - Notification to data owners

## Best Practices

1. **Test Coverage**
   - Aim for 80%+ coverage of critical columns
   - Include both schema and data validations
   - Test business rules explicitly

2. **Performance**
   - Run validations on samples for large tables
   - Use incremental validation for streaming
   - Optimize validation queries

3. **Severity Levels**
   - Critical: Fail pipeline on violation
   - High: Drop invalid records
   - Medium: Track and alert
   - Low: Log for analysis

4. **Maintenance**
   - Review and update expectations quarterly
   - Adjust thresholds based on data evolution
   - Archive old validation results

## Troubleshooting

**Issue**: Great Expectations installation errors
**Solution**: `pip install great-expectations databricks-sql-connector`

**Issue**: DLT expectations causing pipeline failures
**Solution**: Start with `@dlt.expect` (track only), then upgrade to `@dlt.expect_or_drop`

**Issue**: Custom validations running too slowly
**Solution**: Sample data for validation, use broadcast joins, cache intermediate results

## Related Commands

- `/databricks-engineering:work-pipeline` - Implement pipeline with quality checks
- `/databricks-engineering:monitor-data-product` - Set up continuous monitoring
- `/databricks-engineering:review-pipeline` - Review quality test coverage

---

**Last Updated**: 2024-12-31
**Version**: 1.0.0
**Category**: Quality Assurance
**Prepared by**: gekambaram
