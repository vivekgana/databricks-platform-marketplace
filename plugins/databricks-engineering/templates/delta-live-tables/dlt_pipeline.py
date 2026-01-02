"""
Delta Live Tables Pipeline Definition

Complete DLT pipeline with bronze, silver, and gold layers.
Includes comprehensive data quality expectations.
"""

import dlt
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType


# =============================================================================
# BRONZE LAYER - Raw Data Ingestion
# =============================================================================


@dlt.table(
    name="bronze_raw_events",
    comment="Raw event data ingested from cloud storage",
    table_properties={
        "quality": "bronze",
        "pipelines.autoOptimize.managed": "true",
    },
    partition_cols=["ingestion_date"],
)
@dlt.expect_all_or_drop(
    {
        "valid_event_id": "event_id IS NOT NULL",
        "valid_timestamp": "event_timestamp IS NOT NULL",
    }
)
def bronze_raw_events():
    """
    Ingest raw events from cloud storage using Auto Loader.
    Automatically handles schema inference and evolution.
    """
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", "/mnt/dlt/schemas/events")
        .option("cloudFiles.inferColumnTypes", "true")
        .load("/mnt/source/events/")
        .withColumn("ingestion_timestamp", F.current_timestamp())
        .withColumn("ingestion_date", F.current_date())
        .withColumn("source_file", F.input_file_name())
    )


@dlt.table(
    name="bronze_raw_users",
    comment="Raw user data from operational database",
    table_properties={"quality": "bronze"},
)
@dlt.expect_all_or_drop(
    {
        "valid_user_id": "user_id IS NOT NULL",
    }
)
def bronze_raw_users():
    """
    Ingest user data from source database or files.
    """
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.schemaLocation", "/mnt/dlt/schemas/users")
        .option("header", "true")
        .load("/mnt/source/users/")
        .withColumn("ingestion_timestamp", F.current_timestamp())
    )


# =============================================================================
# SILVER LAYER - Cleaned and Validated Data
# =============================================================================


@dlt.table(
    name="silver_events",
    comment="Cleaned and validated event data",
    table_properties={
        "quality": "silver",
        "pipelines.autoOptimize.managed": "true",
    },
    partition_cols=["event_date"],
)
@dlt.expect_all(
    {
        "valid_event_type": "event_type IN ('click', 'view', 'purchase', 'search')",
        "valid_amount": "amount IS NULL OR amount >= 0",
        "valid_user_id": "user_id IS NOT NULL",
    }
)
@dlt.expect_or_drop("valid_event_id", "event_id IS NOT NULL")
def silver_events():
    """
    Transform bronze events to silver layer with:
    - Data cleaning and standardization
    - Deduplication
    - Type conversions
    - Business rule validation
    """
    return (
        dlt.read_stream("bronze_raw_events")
        .select(
            F.col("event_id"),
            F.col("user_id"),
            F.lower(F.trim(F.col("event_type"))).alias("event_type"),
            F.col("amount").cast("double").alias("amount"),
            F.to_timestamp(F.col("event_timestamp")).alias("event_timestamp"),
            F.to_date(F.col("event_timestamp")).alias("event_date"),
            F.col("properties"),
            F.col("ingestion_timestamp"),
        )
        .dropDuplicates(["event_id"])
        .withColumn("processing_timestamp", F.current_timestamp())
    )


@dlt.table(
    name="silver_users",
    comment="Cleaned and validated user data",
    table_properties={"quality": "silver"},
)
@dlt.expect_all(
    {
        "valid_email": "email IS NOT NULL AND email LIKE '%@%.%'",
        "valid_signup_date": "signup_date IS NOT NULL",
    }
)
def silver_users():
    """
    Transform bronze users to silver layer with:
    - Email validation
    - Name standardization
    - Data type corrections
    """
    return (
        dlt.read_stream("bronze_raw_users")
        .select(
            F.col("user_id"),
            F.trim(F.col("email")).alias("email"),
            F.initcap(F.trim(F.col("first_name"))).alias("first_name"),
            F.initcap(F.trim(F.col("last_name"))).alias("last_name"),
            F.to_date(F.col("signup_date")).alias("signup_date"),
            F.col("country"),
            F.col("ingestion_timestamp"),
        )
        .dropDuplicates(["user_id"])
        .withColumn("processing_timestamp", F.current_timestamp())
    )


@dlt.table(
    name="silver_enriched_events",
    comment="Events enriched with user information",
    table_properties={"quality": "silver"},
)
def silver_enriched_events():
    """
    Join events with user data for enriched analytics.
    """
    events = dlt.read("silver_events")
    users = dlt.read("silver_users")

    return events.join(users, "user_id", "left").select(
        F.col("event_id"),
        F.col("user_id"),
        F.col("event_type"),
        F.col("amount"),
        F.col("event_timestamp"),
        F.col("event_date"),
        F.col("email"),
        F.col("first_name"),
        F.col("last_name"),
        F.col("country"),
        F.col("properties"),
    )


# =============================================================================
# GOLD LAYER - Business-Level Aggregations
# =============================================================================


@dlt.table(
    name="gold_daily_event_metrics",
    comment="Daily aggregated event metrics by type",
    table_properties={"quality": "gold"},
    partition_cols=["event_date"],
)
def gold_daily_event_metrics():
    """
    Daily aggregations of event metrics.
    """
    return (
        dlt.read("silver_events")
        .groupBy("event_date", "event_type")
        .agg(
            F.count("*").alias("event_count"),
            F.countDistinct("user_id").alias("unique_users"),
            F.sum("amount").alias("total_amount"),
            F.avg("amount").alias("avg_amount"),
            F.max("amount").alias("max_amount"),
            F.min("amount").alias("min_amount"),
        )
        .withColumn("calculation_timestamp", F.current_timestamp())
    )


@dlt.table(
    name="gold_daily_user_metrics",
    comment="Daily user engagement metrics",
    table_properties={"quality": "gold"},
    partition_cols=["event_date"],
)
def gold_daily_user_metrics():
    """
    Daily per-user engagement metrics.
    """
    return (
        dlt.read("silver_enriched_events")
        .groupBy("event_date", "user_id", "country")
        .agg(
            F.count("*").alias("total_events"),
            F.sum(F.when(F.col("event_type") == "click", 1).otherwise(0)).alias(
                "click_count"
            ),
            F.sum(F.when(F.col("event_type") == "view", 1).otherwise(0)).alias(
                "view_count"
            ),
            F.sum(F.when(F.col("event_type") == "purchase", 1).otherwise(0)).alias(
                "purchase_count"
            ),
            F.sum("amount").alias("total_spend"),
        )
        .withColumn("calculation_timestamp", F.current_timestamp())
    )


@dlt.table(
    name="gold_hourly_event_metrics",
    comment="Hourly real-time event metrics",
    table_properties={"quality": "gold", "pipelines.reset.allowed": "false"},
)
def gold_hourly_event_metrics():
    """
    Hourly event metrics for real-time monitoring.
    """
    return (
        dlt.read_stream("silver_events")
        .withColumn("event_hour", F.date_trunc("hour", F.col("event_timestamp")))
        .groupBy(
            F.window(F.col("event_timestamp"), "1 hour"),
            "event_type",
        )
        .agg(
            F.count("*").alias("event_count"),
            F.countDistinct("user_id").alias("unique_users"),
            F.sum("amount").alias("total_amount"),
        )
        .select(
            F.col("window.start").alias("hour_start"),
            F.col("window.end").alias("hour_end"),
            F.col("event_type"),
            F.col("event_count"),
            F.col("unique_users"),
            F.col("total_amount"),
        )
    )


@dlt.table(
    name="gold_user_lifetime_value",
    comment="User lifetime value calculations",
    table_properties={"quality": "gold"},
)
def gold_user_lifetime_value():
    """
    Calculate user lifetime value metrics.
    """
    return (
        dlt.read("silver_enriched_events")
        .groupBy("user_id", "email", "country", "signup_date")
        .agg(
            F.count("*").alias("total_events"),
            F.sum("amount").alias("lifetime_value"),
            F.min("event_date").alias("first_activity_date"),
            F.max("event_date").alias("last_activity_date"),
            F.datediff(F.max("event_date"), F.min("event_date")).alias(
                "days_active"
            ),
        )
        .withColumn("avg_daily_value", F.col("lifetime_value") / F.col("days_active"))
        .withColumn("calculation_timestamp", F.current_timestamp())
    )


# =============================================================================
# DATA QUALITY TABLES
# =============================================================================


@dlt.table(name="quarantine_bronze_events", comment="Quarantined bronze events")
def quarantine_bronze_events():
    """
    Table to store records that failed bronze quality checks.
    """
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("/mnt/source/events/")
        .filter(F.col("event_id").isNull() | F.col("event_timestamp").isNull())
        .withColumn("quarantine_timestamp", F.current_timestamp())
        .withColumn("quarantine_reason", F.lit("Failed bronze expectations"))
    )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def log_metrics(table_name: str, record_count: int):
    """
    Log pipeline metrics for monitoring.

    Args:
        table_name: Name of the table
        record_count: Number of records processed
    """
    print(f"Pipeline Metrics - Table: {table_name}, Records: {record_count}")


# =============================================================================
# PIPELINE CONFIGURATION
# =============================================================================

# Enable pipeline features
spark.conf.set("pipelines.autoOptimization.enabled", "true")
spark.conf.set("pipelines.enableChangeDataCapture", "true")
spark.conf.set("pipelines.enableSchemaEvolution", "true")
