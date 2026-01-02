"""
DataFrame Assertion Utilities
Helper functions for testing DataFrames.
"""
from pyspark.sql import DataFrame
from typing import List


def assert_schema_equals(df: DataFrame, expected_columns: List[str]):
    """Assert DataFrame has expected columns."""
    actual = df.columns
    assert set(actual) == set(expected_columns), \
        f"Schema mismatch: {actual} != {expected_columns}"


def assert_row_count(df: DataFrame, expected: int):
    """Assert DataFrame has expected row count."""
    actual = df.count()
    assert actual == expected, \
        f"Row count mismatch: {actual} != {expected}"


def assert_no_nulls(df: DataFrame, column: str):
    """Assert column has no null values."""
    null_count = df.filter(df[column].isNull()).count()
    assert null_count == 0, \
        f"Column {column} has {null_count} null values"
