# Feature Engineering Skill

**Last Updated:** 2026-01-01 22:45:49
**Version:** 1.0.0

## Overview

Master Databricks Feature Store patterns for scalable feature engineering, online/offline serving, and feature reuse across ML projects.

## Key Patterns

### Pattern 1: Feature Table Creation

```python
from databricks import feature_store
from pyspark.sql import functions as F

fs = feature_store.FeatureStoreClient()

# Compute features
features = df.groupBy("customer_id").agg(
    F.avg("amount").alias("avg_transaction_amount"),
    F.count("*").alias("transaction_count"),
    F.max("timestamp").alias("last_transaction_date")
).withColumn("feature_timestamp", F.current_timestamp())

# Create feature table
fs.create_table(
    name="catalog.schema.customer_features",
    primary_keys=["customer_id"],
    df=features,
    description="Customer transaction features"
)
```

### Pattern 2: Training with Feature Lookup

```python
# Create training set
training_set = fs.create_training_set(
    df=labels_df,
    feature_lookups=[
        feature_store.FeatureLookup(
            table_name="catalog.schema.customer_features",
            lookup_key="customer_id"
        )
    ],
    label="target"
)

training_df = training_set.load_df()
```

### Pattern 3: Online Feature Serving

```python
# Publish to online store
fs.publish_table(
    name="catalog.schema.customer_features",
    online_store={
        "type": "cosmosdb",
        "account_uri": uri,
        "database_name": "features"
    }
)
```

## Best Practices

1. Use appropriate primary keys
2. Include timestamp columns
3. Document feature semantics
4. Version feature definitions
5. Monitor feature freshness
6. Implement point-in-time correctness

## References

- [Feature Store Documentation](https://docs.databricks.com/machine-learning/feature-store/)
