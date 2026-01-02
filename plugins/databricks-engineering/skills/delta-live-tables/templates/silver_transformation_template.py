"""
Silver Layer Transformation Template for Delta Live Tables

This template demonstrates data validation, cleansing, and transformation
patterns for the Silver layer with comprehensive data quality expectations.

Author: Databricks Platform Team
Last Updated: 2026-01-01 19:57:49
"""

import dlt
from pyspark.sql.functions import (
    col,
    lower,
    trim,
    regexp_replace,
    when,
    coalesce,
    to_date,
    to_timestamp,
    current_timestamp,
    sha2,
    concat_ws,
    split,
    size,
    array_contains
)
from pyspark.sql.types import StringType, DecimalType, IntegerType
from typing import List, Dict


# Example 1: Basic Silver Transformation with Validation
@dlt.table(
    name="silver_customers_validated",
    comment="Validated and cleansed customer data",
    table_properties={
        "quality": "silver",
        "delta.enableChangeDataFeed": "true"
    }
)
@dlt.expect_or_drop("valid_customer_id", "customer_id IS NOT NULL")
@dlt.expect_or_drop("valid_email_format",
    "email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Z|a-z]{2,}$'")
@dlt.expect("valid_phone", "phone IS NULL OR length(phone) >= 10")
def silver_customers_basic():
    """
    Transform Bronze customer data with basic validation and cleansing.

    Data Quality Rules:
    - customer_id must not be null (drop violating records)
    - email must match valid format (drop violating records)
    - phone should be at least 10 digits (warn on violations)
    """
    return (
        dlt.read_stream("bronze_customers_raw")
            .select(
                col("customer_id"),
                # Standardize email
                lower(trim(col("email"))).alias("email"),
                # Cleanse name
                trim(regexp_replace(col("name"), "\\\\s+", " ")).alias("name"),
                # Standardize phone
                regexp_replace(col("phone"), "[^0-9]", "").alias("phone"),
                # Parse address
                col("address.street").alias("street"),
                col("address.city").alias("city"),
                col("address.state").alias("state"),
                col("address.zip").alias("zip_code"),
                # Timestamps
                to_timestamp(col("created_at")).alias("created_at"),
                to_timestamp(col("updated_at")).alias("updated_at"),
                current_timestamp().alias("processed_at")
            )
            .dropDuplicates(["customer_id"])
    )


# Example 2: Silver with Complex Validation Rules
@dlt.table(
    name="silver_orders_validated",
    comment="Orders with comprehensive validation and business rules",
    table_properties={
        "quality": "silver",
        "pipelines.autoOptimize.zOrderCols": "order_date,customer_id"
    }
)
# Null checks
@dlt.expect_or_fail("no_null_order_id", "order_id IS NOT NULL")
@dlt.expect_or_fail("no_null_customer_id", "customer_id IS NOT NULL")

# Range validations
@dlt.expect_or_drop("positive_amount", "total_amount > 0")
@dlt.expect_or_drop("positive_quantity", "quantity > 0 AND quantity <= 10000")
@dlt.expect_or_drop("reasonable_unit_price",
    "unit_price >= 0.01 AND unit_price <= 1000000")

# Date validations
@dlt.expect_or_drop("valid_order_date",
    "order_date >= '2020-01-01' AND order_date <= current_date()")

# Business rules
@dlt.expect("amount_calculation_valid",
    "ABS(total_amount - (quantity * unit_price)) < 0.01")
@dlt.expect("valid_status",
    "status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')")

# Referential integrity (warn only)
@dlt.expect("customer_exists",
    "customer_id IN (SELECT customer_id FROM LIVE.silver_customers_validated)")
def silver_orders_complex():
    """
    Transform orders with multi-layered validation.

    Validation Levels:
    - FAIL: Critical fields (IDs) - stops pipeline
    - DROP: Invalid data (negative amounts, bad dates)
    - WARN: Business rules (referential integrity)
    """
    return (
        dlt.read_stream("bronze_orders_raw")
            .select(
                col("order_id"),
                col("customer_id"),
                col("product_id"),
                # Cast to proper types
                col("quantity").cast(IntegerType()),
                col("unit_price").cast(DecimalType(10, 2)),
                col("total_amount").cast(DecimalType(10, 2)),
                # Standardize status
                lower(trim(col("status"))).alias("status"),
                # Parse dates
                to_date(col("order_date")).alias("order_date"),
                to_timestamp(col("order_timestamp")).alias("order_timestamp"),
                # Add derived columns
                (col("quantity") * col("unit_price")).alias("calculated_amount"),
                current_timestamp().alias("processed_at")
            )
            .dropDuplicates(["order_id"])
    )


# Example 3: Silver with Data Enrichment
@dlt.table(
    name="silver_transactions_enriched",
    comment="Transactions enriched with derived attributes and quality scores",
    table_properties={"quality": "silver"}
)
@dlt.expect_or_drop("valid_transaction_id", "transaction_id IS NOT NULL")
@dlt.expect_or_drop("valid_amount", "amount > 0 AND amount < 1000000")
def silver_transactions_enriched():
    """
    Enrich transaction data with derived attributes and quality scoring.

    Enrichments:
    - Transaction type classification
    - Risk scoring
    - Data quality scoring
    - Standardization
    """
    return (
        dlt.read_stream("bronze_transactions_raw")
            .select(
                col("transaction_id"),
                col("account_id"),
                col("amount").cast(DecimalType(10, 2)),
                col("currency"),
                to_timestamp(col("transaction_timestamp")).alias("timestamp"),

                # Classify transaction type
                when(col("amount") < 10, "micro")
                    .when(col("amount") < 100, "small")
                    .when(col("amount") < 1000, "medium")
                    .when(col("amount") < 10000, "large")
                    .otherwise("enterprise").alias("transaction_type"),

                # Calculate risk score (0-100)
                (
                    when(col("amount") > 10000, 30).otherwise(0) +
                    when(col("currency") != "USD", 20).otherwise(0) +
                    when(col("country") == "high_risk", 50).otherwise(0)
                ).alias("risk_score"),

                # Data quality score
                (
                    when(col("account_id").isNotNull(), 25).otherwise(0) +
                    when(col("amount").isNotNull(), 25).otherwise(0) +
                    when(col("currency").isNotNull(), 25).otherwise(0) +
                    when(col("transaction_timestamp").isNotNull(), 25).otherwise(0)
                ).alias("quality_score"),

                # Standardization
                upper(trim(col("currency"))).alias("currency_code"),
                lower(trim(col("country"))).alias("country_code"),

                current_timestamp().alias("processed_at")
            )
            .filter(col("quality_score") >= 75)  # Minimum quality threshold
    )


# Example 4: Silver with Slowly Changing Dimension (SCD) Type 2
@dlt.view(
    comment="Staging view for customer CDC processing"
)
def silver_customers_cdc_staging():
    """Prepare customer data for SCD Type 2 processing."""
    return (
        dlt.read_stream("bronze_customers_cdc")
            .select(
                col("customer_id"),
                lower(trim(col("email"))).alias("email"),
                trim(col("name")).alias("name"),
                col("segment"),
                col("status"),
                to_timestamp(col("updated_at")).alias("updated_at"),
                col("operation")  # INSERT, UPDATE, DELETE
            )
    )


dlt.create_streaming_table(
    name="silver_customers_history",
    comment="Customer history with SCD Type 2 tracking",
    table_properties={
        "quality": "silver",
        "delta.enableChangeDataFeed": "true"
    }
)

dlt.apply_changes(
    target="silver_customers_history",
    source="silver_customers_cdc_staging",
    keys=["customer_id"],
    sequence_by="updated_at",
    apply_as_deletes=col("operation") == "DELETE",
    stored_as_scd_type=2
)


# Example 5: Silver with Data Masking (PII Protection)
@dlt.table(
    name="silver_users_masked",
    comment="User data with PII masking for analytics",
    table_properties={"quality": "silver"}
)
@dlt.expect_or_drop("valid_user_id", "user_id IS NOT NULL")
def silver_users_with_masking():
    """
    Transform user data with PII masking for compliance.

    Masking Strategies:
    - Email: Hash the local part, keep domain
    - Phone: Show only last 4 digits
    - SSN: Show only last 4 digits
    - Credit Card: Show only last 4 digits
    """
    return (
        dlt.read_stream("bronze_users_raw")
            .select(
                col("user_id"),

                # Mask email (hash local part)
                concat_ws("@",
                    sha2(split(col("email"), "@")[0], 256).substr(1, 8),
                    split(col("email"), "@")[1]
                ).alias("email_masked"),

                # Mask phone (show last 4 digits)
                concat(
                    lit("***-***-"),
                    col("phone").substr(-4, 4)
                ).alias("phone_masked"),

                # Mask SSN (show last 4 digits)
                concat(
                    lit("***-**-"),
                    col("ssn").substr(-4, 4)
                ).alias("ssn_masked"),

                # Keep non-PII fields
                col("user_segment"),
                col("registration_date"),
                col("status"),

                current_timestamp().alias("processed_at")
            )
    )


# Example 6: Silver with Deduplication Strategy
@dlt.table(
    name="silver_events_deduplicated",
    comment="Events with advanced deduplication logic",
    table_properties={
        "quality": "silver",
        "pipelines.autoOptimize.zOrderCols": "event_date,event_type"
    }
)
@dlt.expect_or_drop("valid_event_id", "event_id IS NOT NULL")
def silver_events_deduplicated():
    """
    Deduplicate events using composite key and recency logic.

    Deduplication Strategy:
    - Primary key: event_id
    - Composite key: user_id + event_type + event_timestamp
    - Resolution: Keep most recent record based on processed_timestamp
    """
    from pyspark.sql.window import Window
    from pyspark.sql.functions import row_number, desc

    bronze_events = dlt.read_stream("bronze_events_raw")

    # Define window for deduplication
    window_spec = (
        Window
            .partitionBy("event_id")
            .orderBy(desc("_ingestion_timestamp"))
    )

    return (
        bronze_events
            .withColumn("row_num", row_number().over(window_spec))
            .filter(col("row_num") == 1)
            .drop("row_num")
            .select(
                col("event_id"),
                col("user_id"),
                col("event_type"),
                to_timestamp(col("event_timestamp")).alias("event_timestamp"),
                to_date(col("event_timestamp")).alias("event_date"),
                col("event_properties"),
                current_timestamp().alias("processed_at")
            )
    )


# Example 7: Silver with Error Quarantine Pattern
@dlt.table(
    name="silver_products_validated",
    comment="Validated product data",
    table_properties={"quality": "silver"}
)
@dlt.expect_or_drop("valid_product_id", "product_id IS NOT NULL")
@dlt.expect_or_drop("positive_price", "price > 0")
def silver_products_validated():
    """Valid product records that pass all quality checks."""
    return (
        dlt.read_stream("bronze_products_raw")
            .withColumn("validation_errors",
                when(col("product_id").isNull(), array("null_product_id"))
                .when(col("price") <= 0, array("invalid_price"))
                .otherwise(array())
            )
            .filter(size(col("validation_errors")) == 0)
            .select(
                col("product_id"),
                col("product_name"),
                col("category"),
                col("price").cast(DecimalType(10, 2)),
                col("inventory_count").cast(IntegerType()),
                current_timestamp().alias("processed_at")
            )
    )


@dlt.table(
    name="silver_products_quarantine",
    comment="Invalid product records for review and correction",
    table_properties={"quality": "quarantine"}
)
def silver_products_quarantine():
    """
    Quarantine invalid records for review.

    This table captures records that fail validation so they can be:
    - Reviewed by data stewards
    - Corrected and reprocessed
    - Used for improving upstream data quality
    """
    return (
        dlt.read_stream("bronze_products_raw")
            .withColumn("validation_errors",
                when(col("product_id").isNull(), array("null_product_id"))
                .when(col("price") <= 0, array("invalid_price"))
                .otherwise(array())
            )
            .filter(size(col("validation_errors")) > 0)
            .select(
                col("*"),
                col("validation_errors"),
                current_timestamp().alias("quarantine_timestamp")
            )
    )


# Best Practices:
# 1. Use appropriate expectation levels (fail/drop/warn)
# 2. Add derived columns for business value
# 3. Implement comprehensive data quality checks
# 4. Use proper data types (DecimalType for money)
# 5. Standardize text fields (lower, trim)
# 6. Add quality scores for downstream filtering
# 7. Implement quarantine pattern for bad data
# 8. Use SCD Type 2 for tracking historical changes
# 9. Mask PII data when required
# 10. Z-ORDER by common filter columns
