"""
Bronze Layer - Raw Data Ingestion

This module handles ingestion of raw data from various sources into bronze Delta tables.
Implements minimal transformations to preserve data fidelity.
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    current_timestamp,
    input_file_name,
    col,
    lit,
)
from delta import DeltaTable
from typing import Optional, Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BronzeIngestion:
    """
    Handles raw data ingestion into bronze layer Delta tables.

    The bronze layer stores raw data with minimal transformations:
    - Adds metadata columns (ingestion timestamp, source file)
    - Preserves original data structure
    - Enables data lineage tracking
    """

    def __init__(
        self,
        catalog: str,
        schema: str,
        checkpoint_location: Optional[str] = None,
    ):
        """
        Initialize BronzeIngestion.

        Args:
            catalog: Unity Catalog name
            schema: Schema name within the catalog
            checkpoint_location: Optional checkpoint location for streaming
        """
        self.spark = SparkSession.builder.getOrCreate()
        self.catalog = catalog
        self.schema = schema
        self.checkpoint_location = checkpoint_location or f"/tmp/checkpoints/{catalog}/{schema}"

        logger.info(f"Initialized BronzeIngestion for {catalog}.{schema}")

    def _add_metadata_columns(self, df: DataFrame) -> DataFrame:
        """
        Add metadata columns to track data lineage.

        Args:
            df: Source DataFrame

        Returns:
            DataFrame with metadata columns
        """
        return df.withColumn("ingestion_timestamp", current_timestamp()).withColumn(
            "source_file", input_file_name()
        ).withColumn("ingestion_date", col("ingestion_timestamp").cast("date"))

    def ingest_json_data(
        self,
        source_path: str,
        table_name: str,
        schema_hint: Optional[str] = None,
        merge_schema: bool = True,
        partition_by: Optional[List[str]] = None,
    ) -> None:
        """
        Ingest JSON data into bronze table.

        Args:
            source_path: Path to source JSON files
            table_name: Target bronze table name
            schema_hint: Optional schema hint for complex JSON
            merge_schema: Whether to merge schema changes
            partition_by: Optional list of columns to partition by
        """
        logger.info(f"Starting JSON ingestion from {source_path}")

        try:
            # Read JSON data
            df = self.spark.read.format("json").option("inferSchema", "true").option(
                "mergeSchema", str(merge_schema)
            )

            if schema_hint:
                df = df.schema(schema_hint)

            df = df.load(source_path)

            # Add metadata
            df = self._add_metadata_columns(df)

            # Write to bronze table
            target_table = f"{self.catalog}.{self.schema}.{table_name}"

            writer = df.write.format("delta").mode("append").option(
                "mergeSchema", str(merge_schema)
            )

            if partition_by:
                writer = writer.partitionBy(partition_by)

            writer.saveAsTable(target_table)

            record_count = df.count()
            logger.info(
                f"Successfully ingested {record_count} records to {target_table}"
            )

        except Exception as e:
            logger.error(f"Error during JSON ingestion: {str(e)}")
            raise

    def ingest_csv_data(
        self,
        source_path: str,
        table_name: str,
        header: bool = True,
        delimiter: str = ",",
        merge_schema: bool = True,
        partition_by: Optional[List[str]] = None,
    ) -> None:
        """
        Ingest CSV data into bronze table.

        Args:
            source_path: Path to source CSV files
            table_name: Target bronze table name
            header: Whether CSV has header row
            delimiter: CSV delimiter
            merge_schema: Whether to merge schema changes
            partition_by: Optional list of columns to partition by
        """
        logger.info(f"Starting CSV ingestion from {source_path}")

        try:
            # Read CSV data
            df = (
                self.spark.read.format("csv")
                .option("header", str(header))
                .option("delimiter", delimiter)
                .option("inferSchema", "true")
                .option("mergeSchema", str(merge_schema))
                .load(source_path)
            )

            # Add metadata
            df = self._add_metadata_columns(df)

            # Write to bronze table
            target_table = f"{self.catalog}.{self.schema}.{table_name}"

            writer = df.write.format("delta").mode("append").option(
                "mergeSchema", str(merge_schema)
            )

            if partition_by:
                writer = writer.partitionBy(partition_by)

            writer.saveAsTable(target_table)

            record_count = df.count()
            logger.info(
                f"Successfully ingested {record_count} records to {target_table}"
            )

        except Exception as e:
            logger.error(f"Error during CSV ingestion: {str(e)}")
            raise

    def ingest_parquet_data(
        self,
        source_path: str,
        table_name: str,
        merge_schema: bool = True,
        partition_by: Optional[List[str]] = None,
    ) -> None:
        """
        Ingest Parquet data into bronze table.

        Args:
            source_path: Path to source Parquet files
            table_name: Target bronze table name
            merge_schema: Whether to merge schema changes
            partition_by: Optional list of columns to partition by
        """
        logger.info(f"Starting Parquet ingestion from {source_path}")

        try:
            # Read Parquet data
            df = (
                self.spark.read.format("parquet")
                .option("mergeSchema", str(merge_schema))
                .load(source_path)
            )

            # Add metadata
            df = self._add_metadata_columns(df)

            # Write to bronze table
            target_table = f"{self.catalog}.{self.schema}.{table_name}"

            writer = df.write.format("delta").mode("append").option(
                "mergeSchema", str(merge_schema)
            )

            if partition_by:
                writer = writer.partitionBy(partition_by)

            writer.saveAsTable(target_table)

            record_count = df.count()
            logger.info(
                f"Successfully ingested {record_count} records to {target_table}"
            )

        except Exception as e:
            logger.error(f"Error during Parquet ingestion: {str(e)}")
            raise

    def ingest_streaming_data(
        self,
        source_path: str,
        table_name: str,
        format: str = "json",
        trigger: str = "processingTime",
        trigger_interval: str = "1 minute",
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Ingest streaming data into bronze table.

        Args:
            source_path: Path to source streaming data
            table_name: Target bronze table name
            format: Source data format (json, csv, parquet)
            trigger: Trigger type (processingTime, once, continuous)
            trigger_interval: Trigger interval for processingTime
            options: Additional read options
        """
        logger.info(f"Starting streaming ingestion from {source_path}")

        try:
            # Read streaming data
            reader = self.spark.readStream.format(format)

            if options:
                for key, value in options.items():
                    reader = reader.option(key, value)

            df = reader.load(source_path)

            # Add metadata
            df = self._add_metadata_columns(df)

            # Write to bronze table
            target_table = f"{self.catalog}.{self.schema}.{table_name}"
            checkpoint_path = f"{self.checkpoint_location}/{table_name}"

            query = (
                df.writeStream.format("delta")
                .outputMode("append")
                .option("checkpointLocation", checkpoint_path)
                .trigger(processingTime=trigger_interval)
                .toTable(target_table)
            )

            logger.info(
                f"Started streaming query for {target_table} with ID: {query.id}"
            )

        except Exception as e:
            logger.error(f"Error during streaming ingestion: {str(e)}")
            raise

    def ingest_from_jdbc(
        self,
        jdbc_url: str,
        table_name: str,
        source_table: str,
        properties: Dict[str, str],
        partition_column: Optional[str] = None,
        num_partitions: int = 10,
        lower_bound: Optional[int] = None,
        upper_bound: Optional[int] = None,
    ) -> None:
        """
        Ingest data from JDBC source into bronze table.

        Args:
            jdbc_url: JDBC connection URL
            table_name: Target bronze table name
            source_table: Source table name in JDBC database
            properties: JDBC connection properties (user, password, etc.)
            partition_column: Column to use for partitioning reads
            num_partitions: Number of partitions for parallel reads
            lower_bound: Lower bound for partition column
            upper_bound: Upper bound for partition column
        """
        logger.info(f"Starting JDBC ingestion from {source_table}")

        try:
            # Read from JDBC
            reader = (
                self.spark.read.format("jdbc")
                .option("url", jdbc_url)
                .option("dbtable", source_table)
            )

            for key, value in properties.items():
                reader = reader.option(key, value)

            if partition_column:
                reader = (
                    reader.option("partitionColumn", partition_column)
                    .option("numPartitions", str(num_partitions))
                    .option("lowerBound", str(lower_bound))
                    .option("upperBound", str(upper_bound))
                )

            df = reader.load()

            # Add metadata
            df = self._add_metadata_columns(df).withColumn("source_system", lit("jdbc"))

            # Write to bronze table
            target_table = f"{self.catalog}.{self.schema}.{table_name}"

            df.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable(
                target_table
            )

            record_count = df.count()
            logger.info(
                f"Successfully ingested {record_count} records to {target_table}"
            )

        except Exception as e:
            logger.error(f"Error during JDBC ingestion: {str(e)}")
            raise

    def get_table_metrics(self, table_name: str) -> Dict[str, Any]:
        """
        Get metrics for a bronze table.

        Args:
            table_name: Bronze table name

        Returns:
            Dictionary containing table metrics
        """
        target_table = f"{self.catalog}.{self.schema}.{table_name}"

        try:
            df = self.spark.table(target_table)

            metrics = {
                "record_count": df.count(),
                "latest_ingestion": df.agg({"ingestion_timestamp": "max"}).collect()[
                    0
                ][0],
                "earliest_ingestion": df.agg({"ingestion_timestamp": "min"}).collect()[
                    0
                ][0],
                "partition_count": df.rdd.getNumPartitions(),
            }

            # Get Delta table history
            delta_table = DeltaTable.forName(self.spark, target_table)
            history = delta_table.history(1).collect()

            if history:
                metrics["last_operation"] = history[0].operation
                metrics["last_operation_timestamp"] = history[0].timestamp

            return metrics

        except Exception as e:
            logger.error(f"Error getting table metrics: {str(e)}")
            raise
