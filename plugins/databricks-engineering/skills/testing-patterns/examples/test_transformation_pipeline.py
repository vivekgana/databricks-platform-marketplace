"""
Transformation Pipeline Test Example
Unit tests for data transformations.
"""
import pytest
from pyspark.sql.functions import col


def transform_orders(df):
    """Sample transformation to test."""
    return df.withColumn("amount_usd", col("amount") * 1.0)


def test_transform_orders(spark, sample_data):
    """Test order transformation logic."""
    result = transform_orders(sample_data)

    assert "amount_usd" in result.columns
    assert result.count() == 3
    assert result.filter(col("amount_usd") < 0).count() == 0
