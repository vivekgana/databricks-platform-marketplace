"""
Bronze Layer Ingestion Template for Delta Live Tables

This template demonstrates raw data ingestion patterns for the Bronze layer
using Delta Live Tables with cloud file streaming and metadata enrichment.

Author: Databricks Platform Team
Last Updated: 2026-01-01 19:57:49
"""

import dlt
from pyspark.sql.functions import (
    current_timestamp,
    input_file_name,
    col,
    lit,
    to_timestamp
)
from typing import Optional


class BronzeIngestionConfig:
    """Configuration for Bronze layer ingestion."""

    def __init__(
        self,
        source_path: str,
        source_format: str = "json",
        table_name: str = "bronze_raw",
        schema_location: Optional[str] = None
    ):
        """
        Initialize Bronze ingestion configuration.

        Args:
            source_path: Cloud storage path for source data
            source_format: File format (json, csv, parquet, etc.)
            table_name: Name for the Bronze table
            schema_location: Optional schema inference location
        """
        self.source_path = source_path
        self.source_format = source_format
        self.table_name = table_name
        self.schema_location = schema_location or f"{source_path}/_schemas"


# Example 1: Basic Bronze Ingestion
@dlt.table(
    name="bronze_events_raw",
    comment="Raw events ingested from cloud storage with metadata enrichment",
    table_properties={
        "quality": "bronze",
        "pipelines.autoOptimize.managed": "true",
        "delta.enableChangeDataFeed": "true"
    }
)
def bronze_events_basic():
    """
    Ingest raw events with minimal transformation.

    This is the simplest Bronze ingestion pattern - store data as-is
    with metadata columns for auditing and debugging.
    """
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.schemaLocation", "/mnt/schemas/events")
            .option("cloudFiles.inferColumnTypes", "true")
            .load("/mnt/landing/events/")
            # Add metadata columns
            .withColumn("_ingestion_timestamp", current_timestamp())
            .withColumn("_source_file", input_file_name())
            .withColumn("_pipeline_version", lit("1.0.0"))
    )


# Example 2: Bronze Ingestion with Schema Hints
@dlt.table(
    name="bronze_sales_raw",
    comment="Raw sales data with enforced schema hints",
    table_properties={
        "quality": "bronze",
        "pipelines.autoOptimize.zOrderCols": "ingestion_date"
    }
)
def bronze_sales_with_schema():
    """
    Ingest sales data with schema hints for better type inference.

    Use schema hints when Auto Loader's type inference needs guidance
    for specific columns (dates, decimals, etc.).
    """
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.schemaLocation", "/mnt/schemas/sales")
            # Schema hints for better type inference
            .option("cloudFiles.schemaHints",
                "sale_date DATE, amount DECIMAL(10,2), quantity INT")
            .option("cloudFiles.inferColumnTypes", "true")
            .load("/mnt/landing/sales/")
            .withColumn("_ingestion_timestamp", current_timestamp())
            .withColumn("_source_file", input_file_name())
            .withColumn("_ingestion_date", current_timestamp().cast("date"))
    )


# Example 3: Bronze Ingestion with Rescue Data
@dlt.table(
    name="bronze_devices_raw",
    comment="Raw device data with rescue column for schema evolution",
    table_properties={
        "quality": "bronze",
        "delta.enableChangeDataFeed": "true"
    }
)
@dlt.expect("has_device_id", "device_id IS NOT NULL OR _rescue_data IS NOT NULL")
def bronze_devices_with_rescue():
    """
    Ingest device data with rescue column for handling schema mismatches.

    The _rescue_data column captures any data that doesn't match the schema,
    preventing data loss during schema evolution.
    """
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.schemaLocation", "/mnt/schemas/devices")
            .option("rescuedDataColumn", "_rescue_data")  # Capture schema mismatches
            .load("/mnt/landing/devices/")
            .withColumn("_ingestion_timestamp", current_timestamp())
            .withColumn("_source_file", input_file_name())
    )


# Example 4: Multi-Source Bronze Ingestion
@dlt.table(
    name="bronze_customers_raw",
    comment="Raw customer data from multiple sources",
    table_properties={"quality": "bronze"}
)
def bronze_customers_multi_source():
    """
    Ingest customer data from multiple sources with source tracking.

    This pattern is useful when consolidating data from different systems
    or regions into a single Bronze table.
    """
    # Source 1: CRM System
    crm_data = (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.schemaLocation", "/mnt/schemas/crm")
            .load("/mnt/landing/crm/customers/")
            .withColumn("_source_system", lit("CRM"))
    )

    # Source 2: E-commerce Platform
    ecommerce_data = (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.schemaLocation", "/mnt/schemas/ecommerce")
            .load("/mnt/landing/ecommerce/customers/")
            .withColumn("_source_system", lit("ECOMMERCE"))
    )

    # Union both sources
    return (
        crm_data.unionByName(ecommerce_data, allowMissingColumns=True)
            .withColumn("_ingestion_timestamp", current_timestamp())
            .withColumn("_source_file", input_file_name())
    )


# Example 5: Bronze Ingestion with Delta Change Data Feed
@dlt.table(
    name="bronze_inventory_raw",
    comment="Raw inventory data for downstream CDC processing",
    table_properties={
        "quality": "bronze",
        "delta.enableChangeDataFeed": "true",
        "pipelines.autoOptimize.optimizeWrite": "true"
    }
)
def bronze_inventory_with_cdf():
    """
    Ingest inventory data with Change Data Feed enabled.

    Enable CDF when downstream consumers need to track changes
    (inserts, updates, deletes) to Bronze data.
    """
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.schemaLocation", "/mnt/schemas/inventory")
            .load("/mnt/landing/inventory/")
            .withColumn("_ingestion_timestamp", current_timestamp())
            .withColumn("_source_file", input_file_name())
            .withColumn("_record_hash",
                sha2(concat_ws("||", col("*")), 256))  # For change detection
    )


# Example 6: Parameterized Bronze Ingestion (Reusable)
def create_bronze_table(config: BronzeIngestionConfig):
    """
    Factory function for creating parameterized Bronze tables.

    This pattern promotes code reuse by creating Bronze ingestion
    logic that can be configured at runtime.

    Args:
        config: BronzeIngestionConfig instance with source details

    Returns:
        DataFrame representing the Bronze table
    """
    options = {
        "cloudFiles.format": config.source_format,
        "cloudFiles.schemaLocation": config.schema_location,
        "cloudFiles.inferColumnTypes": "true"
    }

    @dlt.table(
        name=config.table_name,
        comment=f"Raw data ingested from {config.source_path}",
        table_properties={"quality": "bronze"}
    )
    def bronze_table():
        reader = spark.readStream.format("cloudFiles")

        for key, value in options.items():
            reader = reader.option(key, value)

        return (
            reader.load(config.source_path)
                .withColumn("_ingestion_timestamp", current_timestamp())
                .withColumn("_source_file", input_file_name())
        )

    return bronze_table


# Usage example for parameterized function:
# events_config = BronzeIngestionConfig(
#     source_path="/mnt/landing/events",
#     source_format="json",
#     table_name="bronze_events_raw"
# )
# create_bronze_table(events_config)


# Example 7: Bronze with File Notification Mode
@dlt.table(
    name="bronze_transactions_raw",
    comment="Raw transactions ingested using file notification mode",
    table_properties={"quality": "bronze"}
)
def bronze_transactions_notification():
    """
    Ingest transactions using file notification mode for efficiency.

    File notification mode uses cloud provider notifications instead of
    directory listing, reducing latency and costs for high-volume ingestion.
    """
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "parquet")
            .option("cloudFiles.schemaLocation", "/mnt/schemas/transactions")
            .option("cloudFiles.useNotifications", "true")  # Enable notifications
            .option("cloudFiles.queueUrl",
                "https://sqs.us-east-1.amazonaws.com/...")  # SQS queue URL
            .load("/mnt/landing/transactions/")
            .withColumn("_ingestion_timestamp", current_timestamp())
            .withColumn("_source_file", input_file_name())
            .withColumn("_file_modification_time",
                to_timestamp(input_file_name()))
    )


# Best Practices:
# 1. Always add _ingestion_timestamp for tracking
# 2. Include _source_file for debugging
# 3. Use cloudFiles.schemaLocation to persist schema
# 4. Enable rescuedDataColumn for schema evolution
# 5. Add _source_system when ingesting from multiple sources
# 6. Set appropriate table properties (autoOptimize, CDF)
# 7. Partition by ingestion date for large volumes
# 8. Use file notification mode for high-volume ingestion
