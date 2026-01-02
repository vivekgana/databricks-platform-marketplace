"""
Pytest Configuration Template
Shared fixtures for Spark testing.
"""
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    """Create Spark session for tests."""
    return (
        SparkSession.builder
        .master("local[*]")
        .appName("pytest-spark")
        .getOrCreate()
    )


@pytest.fixture
def sample_data(spark):
    """Generate sample test data."""
    return spark.createDataFrame([
        (1, "Alice", 100.0),
        (2, "Bob", 200.0),
        (3, "Charlie", 300.0)
    ], ["id", "name", "amount"])
