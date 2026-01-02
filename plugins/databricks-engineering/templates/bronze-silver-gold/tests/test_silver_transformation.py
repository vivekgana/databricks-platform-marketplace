"""Tests for silver layer transformation."""

import pytest
from src.silver.transform_data import SilverTransformation


def test_deduplicate_data(spark, sample_bronze_data, test_catalog, test_schema):
    """Test data deduplication."""
    transformation = SilverTransformation(test_catalog, test_schema)

    result_df = transformation.deduplicate_data(
        sample_bronze_data, partition_columns=["id"], order_by_columns=["timestamp"]
    )

    assert result_df.count() == 3  # Should remove 1 duplicate
    assert result_df.filter("id = 1").count() == 1


def test_clean_string_columns(spark, test_catalog, test_schema):
    """Test string column cleaning."""
    transformation = SilverTransformation(test_catalog, test_schema)

    data = [(1, "  Test  Value  "), (2, "Another   Test")]
    df = spark.createDataFrame(data, ["id", "value"])

    result_df = transformation.clean_string_columns(df, columns=["value"])

    values = [row.value for row in result_df.collect()]
    assert all(val == val.strip() for val in values)
    assert "Test Value" in values


def test_generate_surrogate_key(spark, test_catalog, test_schema):
    """Test surrogate key generation."""
    transformation = SilverTransformation(test_catalog, test_schema)

    data = [(1, "test"), (2, "test2")]
    df = spark.createDataFrame(data, ["id", "value"])

    result_df = transformation._generate_surrogate_key(df, key_columns=["id", "value"])

    assert "surrogate_key" in result_df.columns
    assert result_df.select("surrogate_key").distinct().count() == 2
