"""
Gold Layer Aggregation Template for Delta Live Tables

This template demonstrates business-level aggregation patterns for the Gold layer
with optimized query performance and production-ready datasets.

Author: Databricks Platform Team
Last Updated: 2026-01-01 19:57:49
"""

import dlt
from pyspark.sql.functions import (
    col,
    count,
    sum as sql_sum,
    avg,
    min as sql_min,
    max as sql_max,
    countDistinct,
    approx_count_distinct,
    percentile_approx,
    current_timestamp,
    date_trunc,
    window,
    last,
    first,
    collect_list,
    collect_set,
    expr
)
from pyspark.sql.types import DecimalType
from typing import List


# Example 1: Daily Aggregation with KPIs
@dlt.table(
    name="gold_daily_sales_summary",
    comment="Daily sales metrics aggregated for executive dashboards",
    table_properties={
        "quality": "gold",
        "pipelines.autoOptimize.zOrderCols": "sale_date",
        "delta.enableChangeDataFeed": "true"
    }
)
@dlt.expect_or_fail("valid_date", "sale_date IS NOT NULL")
@dlt.expect("positive_metrics", "total_revenue > 0 AND transaction_count > 0")
def gold_daily_sales():
    """
    Aggregate daily sales metrics for business intelligence.

    Key Metrics:
    - Total revenue and transaction count
    - Average order value (AOV)
    - Unique customer count
    - Top product categories
    """
    return (
        dlt.read("silver_sales_validated")
            .groupBy(
                col("sale_date"),
                col("region"),
                col("store_id")
            )
            .agg(
                # Revenue metrics
                sql_sum("amount").cast(DecimalType(12, 2)).alias("total_revenue"),
                count("*").alias("transaction_count"),
                avg("amount").cast(DecimalType(10, 2)).alias("avg_order_value"),

                # Customer metrics
                countDistinct("customer_id").alias("unique_customers"),

                # Product metrics
                countDistinct("product_id").alias("unique_products"),
                collect_set("category").alias("categories_sold"),

                # Statistical metrics
                sql_min("amount").alias("min_transaction"),
                sql_max("amount").alias("max_transaction"),
                percentile_approx("amount", 0.5).alias("median_transaction"),

                # Timestamps
                current_timestamp().alias("aggregated_at")
            )
            .withColumn(
                "revenue_per_customer",
                (col("total_revenue") / col("unique_customers")).cast(DecimalType(10, 2))
            )
    )


# Example 2: Customer Lifetime Value (LTV)
@dlt.table(
    name="gold_customer_ltv",
    comment="Customer lifetime value calculations for retention analysis",
    table_properties={
        "quality": "gold",
        "pipelines.autoOptimize.zOrderCols": "customer_segment"
    }
)
@dlt.expect_or_fail("valid_customer_id", "customer_id IS NOT NULL")
def gold_customer_ltv():
    """
    Calculate customer lifetime value with segmentation.

    Metrics:
    - Total revenue per customer
    - Average order frequency
    - Customer tenure
    - Predicted LTV
    """
    from pyspark.sql.functions import datediff, current_date, months_between

    return (
        dlt.read("silver_transactions_enriched")
            .groupBy("customer_id")
            .agg(
                # Revenue metrics
                sql_sum("amount").cast(DecimalType(12, 2)).alias("total_lifetime_value"),
                count("*").alias("total_orders"),
                avg("amount").cast(DecimalType(10, 2)).alias("avg_order_value"),

                # Temporal metrics
                sql_min("transaction_date").alias("first_order_date"),
                sql_max("transaction_date").alias("last_order_date"),
                countDistinct("transaction_date").alias("active_days"),

                # Product metrics
                countDistinct("product_category").alias("category_diversity"),
                collect_set("product_category").alias("purchased_categories")
            )
            .withColumn(
                "customer_tenure_days",
                datediff(col("last_order_date"), col("first_order_date"))
            )
            .withColumn(
                "order_frequency",
                (col("total_orders") / col("customer_tenure_days")).cast(DecimalType(6, 4))
            )
            .withColumn(
                "customer_segment",
                expr("""
                    CASE
                        WHEN total_lifetime_value >= 10000 THEN 'VIP'
                        WHEN total_lifetime_value >= 5000 THEN 'Gold'
                        WHEN total_lifetime_value >= 1000 THEN 'Silver'
                        ELSE 'Bronze'
                    END
                """)
            )
            .withColumn("calculated_at", current_timestamp())
    )


# Example 3: Real-time Streaming Aggregation
@dlt.table(
    name="gold_hourly_metrics_streaming",
    comment="Hourly metrics computed in real-time from streaming data",
    table_properties={
        "quality": "gold",
        "pipelines.autoOptimize.optimizeWrite": "true"
    }
)
def gold_hourly_streaming():
    """
    Compute hourly metrics from streaming data with watermarking.

    Use Cases:
    - Real-time dashboards
    - Operational monitoring
    - Anomaly detection
    """
    return (
        dlt.read_stream("silver_events_validated")
            .withWatermark("event_timestamp", "10 minutes")
            .groupBy(
                window("event_timestamp", "1 hour"),
                col("event_type"),
                col("region")
            )
            .agg(
                count("*").alias("event_count"),
                countDistinct("user_id").alias("unique_users"),
                approx_count_distinct("session_id", 0.01).alias("approx_sessions"),
                avg("processing_latency").alias("avg_latency_ms"),
                current_timestamp().alias("computed_at")
            )
            .select(
                col("window.start").alias("hour_start"),
                col("window.end").alias("hour_end"),
                col("event_type"),
                col("region"),
                col("event_count"),
                col("unique_users"),
                col("approx_sessions"),
                col("avg_latency_ms"),
                col("computed_at")
            )
    )


# Example 4: Product Performance Dashboard
@dlt.table(
    name="gold_product_performance",
    comment="Product performance metrics for inventory and marketing decisions",
    table_properties={
        "quality": "gold",
        "pipelines.autoOptimize.zOrderCols": "category,product_id"
    }
)
def gold_product_performance():
    """
    Aggregate product-level metrics for business decisions.

    Metrics:
    - Sales volume and revenue
    - Inventory turnover
    - Customer satisfaction
    - Return rates
    """
    sales = dlt.read("silver_sales_validated")
    returns = dlt.read("silver_returns_validated")
    reviews = dlt.read("silver_product_reviews")

    # Sales aggregation
    sales_agg = (
        sales
            .groupBy("product_id", "category")
            .agg(
                sql_sum("quantity").alias("units_sold"),
                sql_sum("amount").alias("total_revenue"),
                countDistinct("customer_id").alias("unique_buyers"),
                count("*").alias("transaction_count")
            )
    )

    # Returns aggregation
    returns_agg = (
        returns
            .groupBy("product_id")
            .agg(
                count("*").alias("return_count"),
                sql_sum("return_amount").alias("total_returns")
            )
    )

    # Reviews aggregation
    reviews_agg = (
        reviews
            .groupBy("product_id")
            .agg(
                avg("rating").cast(DecimalType(3, 2)).alias("avg_rating"),
                count("*").alias("review_count")
            )
    )

    # Join all metrics
    return (
        sales_agg
            .join(returns_agg, "product_id", "left")
            .join(reviews_agg, "product_id", "left")
            .select(
                col("product_id"),
                col("category"),
                col("units_sold"),
                col("total_revenue"),
                col("unique_buyers"),
                col("transaction_count"),
                coalesce(col("return_count"), lit(0)).alias("return_count"),
                coalesce(col("total_returns"), lit(0)).alias("total_returns"),
                coalesce(col("avg_rating"), lit(0)).alias("avg_rating"),
                coalesce(col("review_count"), lit(0)).alias("review_count")
            )
            .withColumn(
                "return_rate",
                (col("return_count") / col("transaction_count")).cast(DecimalType(5, 4))
            )
            .withColumn(
                "revenue_per_buyer",
                (col("total_revenue") / col("unique_buyers")).cast(DecimalType(10, 2))
            )
            .withColumn("calculated_at", current_timestamp())
    )


# Example 5: Feature Table for ML
@dlt.table(
    name="gold_customer_features",
    comment="Customer feature table for machine learning models",
    table_properties={
        "quality": "gold",
        "delta.enableChangeDataFeed": "true"
    }
)
@dlt.expect_or_fail("valid_customer_id", "customer_id IS NOT NULL")
def gold_customer_features():
    """
    Create feature table for customer churn prediction models.

    Features:
    - Recency, Frequency, Monetary (RFM) scores
    - Behavioral features
    - Engagement metrics
    """
    from pyspark.sql.functions import datediff, current_date, months_between, ntile
    from pyspark.sql.window import Window

    transactions = dlt.read("silver_transactions_enriched")
    events = dlt.read("silver_events_validated")

    # Transaction features
    txn_features = (
        transactions
            .groupBy("customer_id")
            .agg(
                # RFM features
                datediff(current_date(), sql_max("transaction_date")).alias("days_since_last_purchase"),
                count("*").alias("purchase_frequency"),
                sql_sum("amount").alias("monetary_value"),

                # Statistical features
                avg("amount").alias("avg_transaction_amount"),
                sql_min("amount").alias("min_transaction_amount"),
                sql_max("amount").alias("max_transaction_amount"),

                # Temporal features
                countDistinct(date_trunc("month", col("transaction_date"))).alias("active_months"),
                months_between(current_date(), sql_min("transaction_date")).alias("customer_age_months")
            )
    )

    # Behavioral features
    behavioral_features = (
        events
            .groupBy("customer_id")
            .agg(
                countDistinct("event_type").alias("event_diversity"),
                count("*").alias("total_events"),
                sql_sum(when(col("event_type") == "view_product", 1).otherwise(0)).alias("product_views"),
                sql_sum(when(col("event_type") == "add_to_cart", 1).otherwise(0)).alias("cart_additions"),
                sql_sum(when(col("event_type") == "support_contact", 1).otherwise(0)).alias("support_contacts")
            )
    )

    # Join features
    features_df = txn_features.join(behavioral_features, "customer_id", "left")

    # Calculate RFM scores using ntile
    window_spec = Window.orderBy(col("days_since_last_purchase").desc())

    return (
        features_df
            .withColumn("recency_score", ntile(5).over(window_spec))
            .withColumn("frequency_score",
                ntile(5).over(Window.orderBy(col("purchase_frequency"))))
            .withColumn("monetary_score",
                ntile(5).over(Window.orderBy(col("monetary_value"))))
            .withColumn(
                "rfm_score",
                col("recency_score") + col("frequency_score") + col("monetary_score")
            )
            .withColumn(
                "conversion_rate",
                (col("cart_additions") / col("product_views")).cast(DecimalType(5, 4))
            )
            .withColumn("feature_timestamp", current_timestamp())
    )


# Example 6: Time-Series Trend Analysis
@dlt.table(
    name="gold_monthly_trends",
    comment="Monthly trend analysis for forecasting and planning",
    table_properties={
        "quality": "gold",
        "pipelines.autoOptimize.zOrderCols": "year_month"
    }
)
def gold_monthly_trends():
    """
    Calculate month-over-month trends and growth rates.

    Metrics:
    - Revenue growth
    - Customer acquisition
    - Retention rates
    """
    from pyspark.sql.functions import lag, date_format
    from pyspark.sql.window import Window

    monthly_metrics = (
        dlt.read("silver_sales_validated")
            .withColumn("year_month", date_format(col("sale_date"), "yyyy-MM"))
            .groupBy("year_month", "region")
            .agg(
                sql_sum("amount").alias("monthly_revenue"),
                count("*").alias("monthly_transactions"),
                countDistinct("customer_id").alias("monthly_customers")
            )
    )

    window_spec = Window.partitionBy("region").orderBy("year_month")

    return (
        monthly_metrics
            .withColumn("prev_month_revenue", lag("monthly_revenue", 1).over(window_spec))
            .withColumn("prev_month_customers", lag("monthly_customers", 1).over(window_spec))
            .withColumn(
                "revenue_growth_rate",
                ((col("monthly_revenue") - col("prev_month_revenue")) / col("prev_month_revenue") * 100)
                    .cast(DecimalType(5, 2))
            )
            .withColumn(
                "customer_growth_rate",
                ((col("monthly_customers") - col("prev_month_customers")) / col("prev_month_customers") * 100)
                    .cast(DecimalType(5, 2))
            )
            .withColumn("calculated_at", current_timestamp())
    )


# Example 7: Executive Summary Dashboard
@dlt.table(
    name="gold_executive_summary",
    comment="High-level KPIs for executive dashboards",
    table_properties={
        "quality": "gold",
        "pipelines.autoOptimize.optimizeWrite": "true"
    }
)
def gold_executive_summary():
    """
    Aggregate enterprise-wide KPIs for C-level dashboards.

    Top-Level Metrics:
    - Total revenue and growth
    - Customer metrics (acquisition, retention, LTV)
    - Operational efficiency
    - Product performance
    """
    from pyspark.sql.functions import lit, date_format, current_date

    sales = dlt.read("silver_sales_validated")
    customers = dlt.read("silver_customers_validated")
    products = dlt.read("silver_products_validated")

    return (
        sales
            .select(
                date_format(current_date(), "yyyy-MM-dd").alias("report_date"),
                lit("ALL").alias("business_unit")
            )
            .limit(1)
            .join(
                sales.agg(
                    sql_sum("amount").alias("total_revenue"),
                    count("*").alias("total_transactions"),
                    countDistinct("customer_id").alias("active_customers")
                ),
                how="cross"
            )
            .join(
                customers.agg(
                    count("*").alias("total_customers")
                ),
                how="cross"
            )
            .join(
                products.agg(
                    count("*").alias("total_products")
                ),
                how="cross"
            )
            .withColumn("calculated_at", current_timestamp())
    )


# Best Practices:
# 1. Use appropriate aggregation functions (exact vs approximate)
# 2. Add Z-ORDER for common query patterns
# 3. Include time-based partitioning for large datasets
# 4. Implement SCD Type 2 for historical tracking
# 5. Use DecimalType for financial calculations
# 6. Add watermarking for streaming aggregations
# 7. Create feature tables for ML workflows
# 8. Include metadata columns (aggregated_at, calculated_at)
# 9. Use EXPECT_OR_FAIL for critical business metrics
# 10. Optimize for dashboard query patterns
