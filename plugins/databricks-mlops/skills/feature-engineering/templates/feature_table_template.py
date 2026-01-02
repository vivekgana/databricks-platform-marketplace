"""Feature Table Creation Template"""

from databricks import feature_store
from pyspark.sql import functions as F
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
fs = feature_store.FeatureStoreClient()

def create_customer_features(source_table: str, feature_table: str):
    """Create customer feature table"""

    # Load source data
    df = spark.table(source_table)

    # Compute features
    features = df.groupBy("customer_id").agg(
        F.avg("amount").alias("avg_amount"),
        F.sum("amount").alias("total_amount"),
        F.count("*").alias("transaction_count"),
        F.stddev("amount").alias("std_amount"),
        F.max("timestamp").alias("last_transaction")
    )

    # Add metadata
    features = features.withColumn("feature_timestamp", F.current_timestamp())

    # Create feature table
    fs.create_table(
        name=feature_table,
        primary_keys=["customer_id"],
        df=features,
        description="Customer transaction features"
    )

    return features
