"""Time Series Feature Engineering Example"""

from pyspark.sql import functions as F
from pyspark.sql.window import Window
from databricks import feature_store

fs = feature_store.FeatureStoreClient()

def create_time_series_features(df, entity_col: str, timestamp_col: str):
    """Create time-based aggregation features"""

    # Define windows
    window_7d = Window.partitionBy(entity_col).orderBy(timestamp_col).rangeBetween(-7*86400, 0)
    window_30d = Window.partitionBy(entity_col).orderBy(timestamp_col).rangeBetween(-30*86400, 0)

    # Time-based features
    features = df.withColumn(
        "avg_amount_7d", F.avg("amount").over(window_7d)
    ).withColumn(
        "avg_amount_30d", F.avg("amount").over(window_30d)
    ).withColumn(
        "count_7d", F.count("*").over(window_7d)
    ).withColumn(
        "count_30d", F.count("*").over(window_30d)
    )

    return features
