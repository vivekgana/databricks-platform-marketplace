"""
Pytest configuration for medallion architecture tests.
"""

import pytest
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip


@pytest.fixture(scope="session")
def spark():
    """Create Spark session for testing."""
    builder = (
        SparkSession.builder.appName("MedallionTests")
        .master("local[2]")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse")
    )

    spark_session = configure_spark_with_delta_pip(builder).getOrCreate()
    yield spark_session
    spark_session.stop()


@pytest.fixture(scope="function")
def test_catalog():
    """Test catalog name."""
    return "test_catalog"


@pytest.fixture(scope="function")
def test_schema():
    """Test schema name."""
    return "test_schema"


@pytest.fixture
def sample_bronze_data(spark):
    """Sample bronze layer data for testing."""
    data = [
        (1, "John Doe", "john@example.com", "2024-01-01 10:00:00"),
        (2, "Jane Smith", "jane@example.com", "2024-01-01 10:05:00"),
        (3, "Bob Johnson", "bob@example.com", "2024-01-01 10:10:00"),
        (1, "John Doe", "john.doe@example.com", "2024-01-01 10:15:00"),  # Duplicate
    ]

    schema = "id INT, name STRING, email STRING, timestamp STRING"
    return spark.createDataFrame(data, schema)


@pytest.fixture
def sample_silver_data(spark):
    """Sample silver layer data for testing."""
    data = [
        (1, "John Doe", "john@example.com", "2024-01-01", 100.0),
        (2, "Jane Smith", "jane@example.com", "2024-01-01", 200.0),
        (3, "Bob Johnson", "bob@example.com", "2024-01-02", 150.0),
    ]

    schema = "id INT, name STRING, email STRING, date STRING, amount DOUBLE"
    return spark.createDataFrame(data, schema)
