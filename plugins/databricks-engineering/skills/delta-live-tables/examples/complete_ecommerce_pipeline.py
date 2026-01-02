"""
Complete E-Commerce Data Pipeline using Delta Live Tables

This example demonstrates a production-ready multi-hop pipeline for an e-commerce
platform with Bronze, Silver, and Gold layers.

Architecture:
- Bronze: Raw data ingestion from multiple sources
- Silver: Data validation, cleansing, and enrichment
- Gold: Business metrics and analytics-ready datasets

Author: Databricks Platform Team
Last Updated: 2026-01-01 19:57:49
"""

import dlt
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window

# ============================================================================
# BRONZE LAYER - Raw Data Ingestion
# ============================================================================

@dlt.table(
    name="bronze_orders_raw",
    comment="Raw orders data from e-commerce platform",
    table_properties={
        "quality": "bronze",
        "pipelines.autoOptimize.managed": "true"
    }
)
def bronze_orders():
    """Ingest raw orders from cloud storage."""
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.schemaLocation", "/mnt/schemas/orders")
            .option("cloudFiles.schemaHints", "order_date DATE, amount DECIMAL(10,2)")
            .load("/mnt/landing/orders/")
            .withColumn("_ingestion_timestamp", current_timestamp())
            .withColumn("_source_file", input_file_name())
    )


@dlt.table(
    name="bronze_customers_raw",
    comment="Raw customer data from CRM system",
    table_properties={"quality": "bronze"}
)
def bronze_customers():
    """Ingest raw customer data."""
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.schemaLocation", "/mnt/schemas/customers")
            .load("/mnt/landing/customers/")
            .withColumn("_ingestion_timestamp", current_timestamp())
            .withColumn("_source_file", input_file_name())
    )


@dlt.table(
    name="bronze_products_raw",
    comment="Raw product catalog data",
    table_properties={"quality": "bronze"}
)
def bronze_products():
    """Ingest raw product catalog."""
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.schemaLocation", "/mnt/schemas/products")
            .load("/mnt/landing/products/")
            .withColumn("_ingestion_timestamp", current_timestamp())
            .withColumn("_source_file", input_file_name())
    )


@dlt.table(
    name="bronze_clickstream_raw",
    comment="Raw clickstream events from website",
    table_properties={"quality": "bronze"}
)
def bronze_clickstream():
    """Ingest raw clickstream events."""
    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.schemaLocation", "/mnt/schemas/clickstream")
            .load("/mnt/landing/clickstream/")
            .withColumn("_ingestion_timestamp", current_timestamp())
            .withColumn("_source_file", input_file_name())
    )


# ============================================================================
# SILVER LAYER - Validated and Cleansed Data
# ============================================================================

@dlt.table(
    name="silver_orders_validated",
    comment="Validated and cleansed order data",
    table_properties={
        "quality": "silver",
        "delta.enableChangeDataFeed": "true",
        "pipelines.autoOptimize.zOrderCols": "order_date,customer_id"
    }
)
# Critical validations (fail pipeline)
@dlt.expect_or_fail("valid_order_id", "order_id IS NOT NULL")
@dlt.expect_or_fail("valid_customer_id", "customer_id IS NOT NULL")

# Data quality validations (drop invalid records)
@dlt.expect_or_drop("positive_amount", "total_amount > 0")
@dlt.expect_or_drop("positive_quantity", "quantity > 0")
@dlt.expect_or_drop("valid_order_date",
    "order_date >= '2020-01-01' AND order_date <= current_date()")

# Business rules (warn but continue)
@dlt.expect("reasonable_amount", "total_amount < 100000")
@dlt.expect("order_status_valid",
    "status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')")
def silver_orders():
    """
    Transform and validate orders with comprehensive quality checks.

    Quality Rules:
    - Remove duplicates based on order_id
    - Validate amounts and quantities
    - Standardize status values
    - Calculate derived metrics
    """
    return (
        dlt.read_stream("bronze_orders_raw")
            .select(
                col("order_id"),
                col("customer_id"),
                col("product_id"),
                col("quantity").cast(IntegerType()),
                col("unit_price").cast(DecimalType(10, 2)),
                col("total_amount").cast(DecimalType(10, 2)),
                col("discount_amount").cast(DecimalType(10, 2)),
                lower(trim(col("status"))).alias("status"),
                to_date(col("order_date")).alias("order_date"),
                to_timestamp(col("order_timestamp")).alias("order_timestamp"),
                col("shipping_address"),
                col("payment_method"),
                current_timestamp().alias("processed_at")
            )
            # Add derived columns
            .withColumn("net_amount",
                (col("total_amount") - coalesce(col("discount_amount"), lit(0)))
                    .cast(DecimalType(10, 2)))
            .withColumn("has_discount",
                when(col("discount_amount") > 0, True).otherwise(False))
            .withColumn("order_hour",
                hour(col("order_timestamp")))
            .withColumn("order_day_of_week",
                dayofweek(col("order_date")))
            # Deduplicate
            .dropDuplicates(["order_id"])
    )


@dlt.table(
    name="silver_customers_validated",
    comment="Validated customer data with standardization",
    table_properties={
        "quality": "silver",
        "delta.enableChangeDataFeed": "true"
    }
)
@dlt.expect_or_fail("valid_customer_id", "customer_id IS NOT NULL")
@dlt.expect_or_drop("valid_email",
    "email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Z|a-z]{2,}$'")
@dlt.expect("valid_phone", "phone IS NULL OR length(phone) >= 10")
def silver_customers():
    """
    Validate and standardize customer data.

    Transformations:
    - Standardize email and name formats
    - Cleanse phone numbers
    - Parse address components
    - Calculate customer age
    """
    return (
        dlt.read_stream("bronze_customers_raw")
            .select(
                col("customer_id"),
                # Standardize text fields
                lower(trim(col("email"))).alias("email"),
                initcap(trim(regexp_replace(col("name"), "\\\\s+", " "))).alias("name"),
                regexp_replace(col("phone"), "[^0-9]", "").alias("phone"),
                # Parse address
                col("address.street").alias("street"),
                col("address.city").alias("city"),
                upper(trim(col("address.state"))).alias("state"),
                col("address.zip_code").alias("zip_code"),
                upper(trim(col("address.country"))).alias("country"),
                # Segment and status
                lower(col("segment")).alias("segment"),
                lower(col("status")).alias("status"),
                # Dates
                to_date(col("registration_date")).alias("registration_date"),
                to_date(col("date_of_birth")).alias("date_of_birth"),
                current_timestamp().alias("processed_at")
            )
            # Add derived columns
            .withColumn("customer_age",
                floor(months_between(current_date(), col("date_of_birth")) / 12))
            .withColumn("customer_tenure_days",
                datediff(current_date(), col("registration_date")))
            .withColumn("email_domain",
                split(col("email"), "@")[1])
            .dropDuplicates(["customer_id"])
    )


@dlt.table(
    name="silver_products_validated",
    comment="Validated product catalog with enrichment",
    table_properties={"quality": "silver"}
)
@dlt.expect_or_fail("valid_product_id", "product_id IS NOT NULL")
@dlt.expect_or_drop("positive_price", "price > 0")
@dlt.expect("valid_inventory", "inventory_count >= 0")
def silver_products():
    """Validate and enrich product catalog."""
    return (
        dlt.read_stream("bronze_products_raw")
            .select(
                col("product_id"),
                trim(col("product_name")).alias("product_name"),
                trim(col("description")).alias("description"),
                lower(trim(col("category"))).alias("category"),
                lower(trim(col("subcategory"))).alias("subcategory"),
                col("brand"),
                col("price").cast(DecimalType(10, 2)),
                col("cost").cast(DecimalType(10, 2)),
                col("inventory_count").cast(IntegerType()),
                col("attributes"),
                lower(col("status")).alias("status"),
                current_timestamp().alias("processed_at")
            )
            # Add derived columns
            .withColumn("profit_margin",
                ((col("price") - col("cost")) / col("price") * 100)
                    .cast(DecimalType(5, 2)))
            .withColumn("is_in_stock",
                when(col("inventory_count") > 0, True).otherwise(False))
            .withColumn("stock_status",
                when(col("inventory_count") == 0, "out_of_stock")
                .when(col("inventory_count") < 10, "low_stock")
                .otherwise("in_stock"))
            .dropDuplicates(["product_id"])
    )


@dlt.table(
    name="silver_clickstream_enriched",
    comment="Enriched clickstream events with session tracking",
    table_properties={
        "quality": "silver",
        "pipelines.autoOptimize.zOrderCols": "event_date,user_id"
    }
)
@dlt.expect_or_drop("valid_event_id", "event_id IS NOT NULL")
@dlt.expect_or_drop("valid_timestamp",
    "event_timestamp >= '2020-01-01' AND event_timestamp <= current_timestamp()")
def silver_clickstream():
    """Enrich clickstream events with session information."""
    return (
        dlt.read_stream("bronze_clickstream_raw")
            .select(
                col("event_id"),
                col("user_id"),
                col("session_id"),
                lower(col("event_type")).alias("event_type"),
                col("page_url"),
                col("referrer_url"),
                col("product_id"),
                to_timestamp(col("event_timestamp")).alias("event_timestamp"),
                col("device_type"),
                col("browser"),
                col("os"),
                current_timestamp().alias("processed_at")
            )
            # Add derived columns
            .withColumn("event_date", to_date(col("event_timestamp")))
            .withColumn("event_hour", hour(col("event_timestamp")))
            .withColumn("is_mobile",
                when(col("device_type").isin("mobile", "tablet"), True).otherwise(False))
    )


# ============================================================================
# GOLD LAYER - Business Metrics and Analytics
# ============================================================================

@dlt.table(
    name="gold_daily_sales_summary",
    comment="Daily sales metrics for executive dashboards",
    table_properties={
        "quality": "gold",
        "pipelines.autoOptimize.zOrderCols": "order_date"
    }
)
@dlt.expect_or_fail("valid_date", "order_date IS NOT NULL")
def gold_daily_sales():
    """
    Aggregate daily sales metrics.

    Metrics:
    - Total revenue and orders
    - Average order value
    - Unique customers
    - Discount impact
    """
    return (
        dlt.read("silver_orders_validated")
            .groupBy("order_date")
            .agg(
                # Revenue metrics
                sum("total_amount").cast(DecimalType(12, 2)).alias("total_revenue"),
                sum("net_amount").cast(DecimalType(12, 2)).alias("net_revenue"),
                sum("discount_amount").cast(DecimalType(12, 2)).alias("total_discounts"),

                # Order metrics
                count("*").alias("order_count"),
                avg("total_amount").cast(DecimalType(10, 2)).alias("avg_order_value"),

                # Customer metrics
                countDistinct("customer_id").alias("unique_customers"),

                # Product metrics
                countDistinct("product_id").alias("unique_products"),
                sum("quantity").alias("total_units_sold"),

                # Status breakdown
                sum(when(col("status") == "delivered", 1).otherwise(0)).alias("delivered_orders"),
                sum(when(col("status") == "cancelled", 1).otherwise(0)).alias("cancelled_orders"),

                current_timestamp().alias("calculated_at")
            )
            .withColumn("discount_rate",
                (col("total_discounts") / col("total_revenue") * 100)
                    .cast(DecimalType(5, 2)))
            .withColumn("revenue_per_customer",
                (col("total_revenue") / col("unique_customers"))
                    .cast(DecimalType(10, 2)))
            .withColumn("cancellation_rate",
                (col("cancelled_orders") / col("order_count") * 100)
                    .cast(DecimalType(5, 2)))
    )


@dlt.table(
    name="gold_customer_360",
    comment="Customer 360 view with lifetime value and RFM scores",
    table_properties={
        "quality": "gold",
        "delta.enableChangeDataFeed": "true"
    }
)
@dlt.expect_or_fail("valid_customer_id", "customer_id IS NOT NULL")
def gold_customer_360():
    """
    Create comprehensive customer 360 view.

    Features:
    - Customer profile
    - Purchase history
    - RFM scores
    - Lifetime value
    - Behavioral metrics
    """
    customers = dlt.read("silver_customers_validated")
    orders = dlt.read("silver_orders_validated")
    clicks = dlt.read("silver_clickstream_enriched")

    # Order aggregations
    order_metrics = (
        orders
            .groupBy("customer_id")
            .agg(
                # Purchase metrics
                count("*").alias("total_orders"),
                sum("total_amount").alias("lifetime_value"),
                avg("total_amount").alias("avg_order_value"),
                min("order_date").alias("first_order_date"),
                max("order_date").alias("last_order_date"),
                countDistinct("product_id").alias("unique_products_purchased"),

                # Recency
                datediff(current_date(), max("order_date")).alias("days_since_last_order")
            )
    )

    # Clickstream aggregations
    click_metrics = (
        clicks
            .groupBy("user_id")
            .agg(
                count("*").alias("total_events"),
                countDistinct("session_id").alias("total_sessions"),
                sum(when(col("event_type") == "view_product", 1).otherwise(0))
                    .alias("product_views"),
                sum(when(col("event_type") == "add_to_cart", 1).otherwise(0))
                    .alias("cart_adds")
            )
    )

    # Join all metrics
    customer_360 = (
        customers
            .join(order_metrics, "customer_id", "left")
            .join(click_metrics, customers.customer_id == clicks.user_id, "left")
    )

    # Calculate RFM scores
    window_spec = Window.orderBy(col("days_since_last_order").asc())

    return (
        customer_360
            .withColumn("recency_score",
                ntile(5).over(window_spec))
            .withColumn("frequency_score",
                ntile(5).over(Window.orderBy(col("total_orders").desc())))
            .withColumn("monetary_score",
                ntile(5).over(Window.orderBy(col("lifetime_value").desc())))
            .withColumn("rfm_score",
                col("recency_score") + col("frequency_score") + col("monetary_score"))
            .withColumn("customer_segment",
                when(col("rfm_score") >= 13, "Champions")
                .when(col("rfm_score") >= 10, "Loyal Customers")
                .when(col("rfm_score") >= 7, "Potential Loyalists")
                .when(col("rfm_score") >= 5, "At Risk")
                .otherwise("Lost"))
            .withColumn("conversion_rate",
                (coalesce(col("total_orders"), lit(0)) /
                 coalesce(col("total_sessions"), lit(1)))
                    .cast(DecimalType(5, 4)))
            .withColumn("calculated_at", current_timestamp())
    )


@dlt.table(
    name="gold_product_performance",
    comment="Product performance metrics for inventory and marketing",
    table_properties={
        "quality": "gold",
        "pipelines.autoOptimize.zOrderCols": "category,product_id"
    }
)
def gold_product_performance():
    """
    Aggregate product-level performance metrics.

    Metrics:
    - Sales volume and revenue
    - Customer reach
    - Inventory turnover
    - View-to-purchase conversion
    """
    products = dlt.read("silver_products_validated")
    orders = dlt.read("silver_orders_validated")
    clicks = dlt.read("silver_clickstream_enriched")

    # Sales metrics
    sales_metrics = (
        orders
            .groupBy("product_id")
            .agg(
                count("*").alias("order_count"),
                sum("quantity").alias("units_sold"),
                sum("total_amount").alias("total_revenue"),
                countDistinct("customer_id").alias("unique_buyers")
            )
    )

    # Click metrics
    click_metrics = (
        clicks
            .filter(col("product_id").isNotNull())
            .groupBy("product_id")
            .agg(
                sum(when(col("event_type") == "view_product", 1).otherwise(0))
                    .alias("product_views"),
                sum(when(col("event_type") == "add_to_cart", 1).otherwise(0))
                    .alias("cart_adds")
            )
    )

    # Join all metrics
    return (
        products
            .join(sales_metrics, "product_id", "left")
            .join(click_metrics, "product_id", "left")
            .select(
                col("product_id"),
                col("product_name"),
                col("category"),
                col("subcategory"),
                col("brand"),
                col("price"),
                col("inventory_count"),
                coalesce(col("order_count"), lit(0)).alias("order_count"),
                coalesce(col("units_sold"), lit(0)).alias("units_sold"),
                coalesce(col("total_revenue"), lit(0)).alias("total_revenue"),
                coalesce(col("unique_buyers"), lit(0)).alias("unique_buyers"),
                coalesce(col("product_views"), lit(0)).alias("product_views"),
                coalesce(col("cart_adds"), lit(0)).alias("cart_adds")
            )
            .withColumn("view_to_cart_rate",
                (col("cart_adds") / nullif(col("product_views"), 0) * 100)
                    .cast(DecimalType(5, 2)))
            .withColumn("cart_to_purchase_rate",
                (col("order_count") / nullif(col("cart_adds"), 0) * 100)
                    .cast(DecimalType(5, 2)))
            .withColumn("revenue_per_view",
                (col("total_revenue") / nullif(col("product_views"), 0))
                    .cast(DecimalType(10, 2)))
            .withColumn("calculated_at", current_timestamp())
    )


# ============================================================================
# DATA QUALITY MONITORING
# ============================================================================

@dlt.table(
    name="gold_data_quality_metrics",
    comment="Pipeline data quality metrics for monitoring",
    table_properties={"quality": "gold"}
)
def gold_data_quality():
    """
    Track data quality metrics across all layers.

    Use this table to monitor:
    - Record counts
    - Validation pass rates
    - Processing latency
    """
    bronze_orders_count = dlt.read("bronze_orders_raw").count()
    silver_orders_count = dlt.read("silver_orders_validated").count()

    return spark.createDataFrame([
        {
            "layer": "bronze_to_silver",
            "source_table": "bronze_orders_raw",
            "target_table": "silver_orders_validated",
            "source_count": bronze_orders_count,
            "target_count": silver_orders_count,
            "drop_rate": (1 - silver_orders_count / bronze_orders_count) * 100,
            "measured_at": current_timestamp()
        }
    ])
