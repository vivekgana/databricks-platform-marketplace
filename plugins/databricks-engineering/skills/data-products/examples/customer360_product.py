"""
Customer 360 Data Product Example
"""
import dlt
from pyspark.sql.functions import *


@dlt.table(
    name="customer_360",
    comment="Complete customer view data product",
    table_properties={
        "product.name": "customer-360",
        "product.version": "1.0.0",
        "product.owner": "data-team",
        "quality.freshness": "1 hour"
    }
)
@dlt.expect_or_fail("required_customer_id", "customer_id IS NOT NULL")
@dlt.expect("complete_profile", "email IS NOT NULL AND phone IS NOT NULL")
def customer_360():
    """Build customer 360 data product."""
    profile = dlt.read("silver_customer_profile")
    behavior = dlt.read("silver_customer_behavior")

    return profile.join(behavior, "customer_id", "left")
