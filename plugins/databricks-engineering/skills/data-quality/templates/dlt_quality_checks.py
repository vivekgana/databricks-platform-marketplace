"""
DLT Quality Checks Template
Pre-built quality checks for DLT pipelines.
"""
import dlt
from pyspark.sql.functions import *


# Completeness checks
def add_completeness_expectations(required_columns: list):
    """Decorator factory for completeness checks."""
    def decorator(func):
        for col in required_columns:
            func = dlt.expect_or_fail(
                f"required_{col}",
                f"{col} IS NOT NULL"
            )(func)
        return func
    return decorator


# Format validation
EMAIL_PATTERN = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$"
PHONE_PATTERN = r"^\+?[1-9]\d{1,14}$"
UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"


@dlt.table(name="validated_contacts")
@dlt.expect("valid_email", f"email RLIKE '{EMAIL_PATTERN}'")
@dlt.expect("valid_phone", f"phone RLIKE '{PHONE_PATTERN}'")
def example_format_validation():
    return dlt.read_stream("raw_contacts")
