"""Pytest configuration for ML tests."""

import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    return (
        SparkSession.builder.appName("MLTests")
        .master("local[2]")
        .getOrCreate()
    )


@pytest.fixture
def sample_features(spark):
    data = [
        ("cust1", 10, 1000.0, 5),
        ("cust2", 5, 500.0, 2),
        ("cust3", 20, 2000.0, 10),
    ]
    return spark.createDataFrame(
        data, ["customer_id", "total_transactions", "total_spend", "total_interactions"]
    )
