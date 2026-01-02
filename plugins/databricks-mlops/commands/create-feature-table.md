# Create Feature Table Command

**Last Updated:** 2026-01-01 22:45:49
**Version:** 1.0.0
**Category:** Feature Store

## Overview

Create and manage Feature Store tables with online/offline serving capabilities for ML pipelines.

## Command Usage

```bash
/databricks-mlops:create-feature-table --table-name <name> --primary-keys <keys>
```

## Feature Table Creation

```python
from databricks import feature_store
from databricks.feature_store import feature_table
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp
import logging

spark = SparkSession.builder.getOrCreate()
fs = feature_store.FeatureStoreClient()

def create_feature_table(
    table_name: str,
    primary_keys: list,
    df,
    description: str,
    online_store: dict = None
):
    """Create Feature Store table with online serving"""

    # Add metadata columns
    df = df.withColumn("feature_timestamp", current_timestamp())

    # Create feature table
    fs.create_table(
        name=table_name,
        primary_keys=primary_keys,
        df=df,
        description=description,
        schema=df.schema
    )

    print(f"✓ Created feature table: {table_name}")

    # Configure online store if specified
    if online_store:
        configure_online_store(table_name, online_store)

    return table_name

def write_features(table_name: str, df, mode: str = "merge"):
    """Write features to Feature Store table"""

    fs.write_table(
        name=table_name,
        df=df,
        mode=mode
    )

    print(f"✓ Features written to {table_name}")

def configure_online_store(table_name: str, online_config: dict):
    """Configure online feature serving"""

    # Example: Configure with CosmosDB or DynamoDB
    fs.publish_table(
        name=table_name,
        online_store=online_config
    )

    print(f"✓ Online store configured for {table_name}")

def read_features_for_training(
    feature_table: str,
    lookup_keys: list,
    training_df
):
    """Read features and create training dataset"""

    training_set = fs.create_training_set(
        df=training_df,
        feature_lookups=[
            feature_store.FeatureLookup(
                table_name=feature_table,
                lookup_key=lookup_keys
            )
        ],
        label="target"
    )

    return training_set.load_df()

def create_feature_engineering_pipeline(
    source_table: str,
    feature_table: str,
    primary_keys: list
):
    """Create automated feature engineering pipeline"""

    from pyspark.sql.functions import col, avg, sum, count, datediff, when

    # Read source data
    df = spark.table(source_table)

    # Feature engineering transformations
    features = df.groupBy(primary_keys).agg(
        avg("amount").alias("avg_transaction_amount"),
        sum("amount").alias("total_transaction_amount"),
        count("*").alias("transaction_count"),
        avg(when(col("category") == "online", 1).otherwise(0)).alias("online_ratio")
    )

    # Write to feature store
    write_features(feature_table, features)

    return features

# Example: Complete feature table workflow
if __name__ == "__main__":
    CATALOG = "main"
    SCHEMA = "feature_store"
    TABLE_NAME = f"{CATALOG}.{SCHEMA}.customer_features"

    # Sample data
    data = spark.createDataFrame([
        (1, 100.0, "online", "2024-01-01"),
        (1, 50.0, "offline", "2024-01-02"),
        (2, 200.0, "online", "2024-01-01")
    ], ["customer_id", "amount", "category", "date"])

    # Create feature table
    create_feature_table(
        table_name=TABLE_NAME,
        primary_keys=["customer_id"],
        df=data,
        description="Customer transaction features"
    )

    # Create features pipeline
    create_feature_engineering_pipeline(
        source_table=f"{CATALOG}.bronze.transactions",
        feature_table=TABLE_NAME,
        primary_keys=["customer_id"]
    )
```

## Best Practices

1. **Schema Design**
   - Use appropriate primary keys
   - Version feature columns
   - Add timestamp columns
   - Document feature semantics

2. **Performance**
   - Partition large tables
   - Use appropriate data types
   - Optimize for lookup patterns
   - Cache frequently used features

3. **Online Serving**
   - Configure for low latency
   - Monitor cache hit rates
   - Set appropriate TTLs
   - Plan for failover

## References

- [Databricks Feature Store](https://docs.databricks.com/machine-learning/feature-store/index.html)
