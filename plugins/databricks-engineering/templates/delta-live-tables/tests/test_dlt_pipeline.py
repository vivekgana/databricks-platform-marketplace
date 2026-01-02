"""Tests for DLT pipeline transformations."""

import pytest
from pyspark.sql import functions as F


def test_event_data_structure(spark):
    """Test event data has expected structure."""
    data = [
        ("evt1", "user1", "click", 10.0, "2024-01-01 10:00:00"),
        ("evt2", "user2", "view", None, "2024-01-01 10:05:00"),
    ]

    df = spark.createDataFrame(
        data, ["event_id", "user_id", "event_type", "amount", "event_timestamp"]
    )

    assert df.count() == 2
    assert "event_id" in df.columns
    assert "amount" in df.columns


def test_daily_aggregation(spark):
    """Test daily aggregation logic."""
    data = [
        ("2024-01-01", "click", 5),
        ("2024-01-01", "click", 3),
        ("2024-01-01", "view", 2),
    ]

    df = spark.createDataFrame(data, ["date", "event_type", "count"])

    result = df.groupBy("date", "event_type").agg(F.sum("count").alias("total_count"))

    assert result.filter("event_type = 'click'").collect()[0].total_count == 8
    assert result.filter("event_type = 'view'").collect()[0].total_count == 2
