"""
Spark Testing Fixtures
Reusable fixtures for Spark DataFrame testing.
"""
import pytest
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import *


@pytest.fixture
def spark_session():
    """Create Spark session."""
    return SparkSession.builder\
        .master("local[2]")\
        .appName("test")\
        .getOrCreate()


@pytest.fixture
def sample_orders(spark_session):
    """Sample orders data for testing."""
    schema = StructType([
        StructField("order_id", StringType(), False),
        StructField("customer_id", StringType(), False),
        StructField("amount", DoubleType(), False)
    ])

    data = [
        ("O1", "C1", 100.0),
        ("O2", "C2", 200.0)
    ]

    return spark_session.createDataFrame(data, schema)
