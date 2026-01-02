"""Tests for gold layer aggregation."""

import pytest
from src.gold.aggregate_metrics import GoldAggregation
from src.gold.business_logic import BusinessLogic


def test_business_rules(spark, sample_silver_data, test_catalog, test_schema):
    """Test business rule application."""
    business_logic = BusinessLogic(test_catalog, test_schema)

    rules = {"high_value": "CASE WHEN amount > 150 THEN true ELSE false END"}

    result_df = business_logic.apply_business_rules(sample_silver_data, rules)

    assert "high_value" in result_df.columns
    high_value_count = result_df.filter("high_value = true").count()
    assert high_value_count == 1  # Only one record > 150


def test_customer_categorization(spark, test_catalog, test_schema):
    """Test customer categorization logic."""
    business_logic = BusinessLogic(test_catalog, test_schema)

    data = [
        (1, "Customer A", 150000.0),
        (2, "Customer B", 50000.0),
        (3, "Customer C", 5000.0),
        (4, "Customer D", 500.0),
    ]

    df = spark.createDataFrame(data, ["id", "name", "revenue"])

    result_df = business_logic.categorize_customers(df, "revenue")

    segments = {row.id: row.customer_segment for row in result_df.collect()}

    assert segments[1] == "Enterprise"
    assert segments[2] == "Mid-Market"
    assert segments[3] == "SMB"
    assert segments[4] == "Starter"
