"""
Customer Data Validation Example
Complete validation suite for customer data.
"""
import dlt
from pyspark.sql.functions import *


@dlt.table(
    name="bronze_customers_raw",
    comment="Raw customer data ingestion"
)
def bronze_customers():
    return spark.readStream\
        .format("cloudFiles")\
        .option("cloudFiles.format", "json")\
        .load("/mnt/data/customers/")


@dlt.table(name="silver_customers_validated")
@dlt.expect_or_fail("required_id", "customer_id IS NOT NULL")
@dlt.expect_or_drop("valid_email", "email RLIKE '^[A-Za-z0-9._%+-]+@'")
@dlt.expect("reasonable_age", "age BETWEEN 0 AND 120")
def silver_customers():
    return (
        dlt.read_stream("bronze_customers_raw")
        .withColumn("validated_at", current_timestamp())
    )
