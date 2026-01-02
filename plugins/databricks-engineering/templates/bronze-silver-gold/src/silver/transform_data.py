"""
Silver Layer - Data Transformation

This module handles transformation of bronze data into clean, validated silver tables.
Implements data quality checks, deduplication, and business rule validation.
"""

from pyspark.sql import SparkSession, DataFrame, Window
from pyspark.sql.functions import (
    col,
    current_timestamp,
    sha2,
    concat_ws,
    row_number,
    when,
    trim,
    upper,
    lower,
    regexp_replace,
    to_date,
    to_timestamp,
    coalesce,
)
from delta import DeltaTable
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SilverTransformation:
    """
    Handles transformation of bronze data into silver layer tables.

    The silver layer implements:
    - Data cleaning and standardization
    - Deduplication
    - Data type conversions
    - Business rule validation
    - Schema enforcement
    """

    def __init__(self, catalog: str, schema: str):
        """
        Initialize SilverTransformation.

        Args:
            catalog: Unity Catalog name
            schema: Schema name within the catalog
        """
        self.spark = SparkSession.builder.getOrCreate()
        self.catalog = catalog
        self.schema = schema

        logger.info(f"Initialized SilverTransformation for {catalog}.{schema}")

    def _add_processing_metadata(self, df: DataFrame) -> DataFrame:
        """
        Add silver layer processing metadata.

        Args:
            df: DataFrame to add metadata to

        Returns:
            DataFrame with metadata columns
        """
        return df.withColumn("silver_processing_timestamp", current_timestamp()).withColumn(
            "silver_processing_date",
            col("silver_processing_timestamp").cast("date"),
        )

    def _generate_surrogate_key(self, df: DataFrame, key_columns: List[str]) -> DataFrame:
        """
        Generate surrogate key from business key columns.

        Args:
            df: DataFrame
            key_columns: Columns to use for surrogate key

        Returns:
            DataFrame with surrogate_key column
        """
        return df.withColumn(
            "surrogate_key", sha2(concat_ws("|", *[col(c) for c in key_columns]), 256)
        )

    def deduplicate_data(
        self,
        df: DataFrame,
        partition_columns: List[str],
        order_by_columns: List[str],
        order_desc: bool = True,
    ) -> DataFrame:
        """
        Deduplicate data based on partition and ordering columns.

        Args:
            df: DataFrame to deduplicate
            partition_columns: Columns to partition by for deduplication
            order_by_columns: Columns to order by
            order_desc: Whether to order descending

        Returns:
            Deduplicated DataFrame
        """
        logger.info(
            f"Deduplicating data on columns: {partition_columns}, ordered by: {order_by_columns}"
        )

        window_spec = Window.partitionBy(partition_columns)

        for order_col in order_by_columns:
            if order_desc:
                window_spec = window_spec.orderBy(col(order_col).desc())
            else:
                window_spec = window_spec.orderBy(col(order_col).asc())

        deduplicated_df = (
            df.withColumn("row_num", row_number().over(window_spec))
            .filter(col("row_num") == 1)
            .drop("row_num")
        )

        original_count = df.count()
        deduplicated_count = deduplicated_df.count()
        duplicates_removed = original_count - deduplicated_count

        logger.info(
            f"Removed {duplicates_removed} duplicates. "
            f"Original: {original_count}, Final: {deduplicated_count}"
        )

        return deduplicated_df

    def clean_string_columns(
        self, df: DataFrame, columns: Optional[List[str]] = None, trim: bool = True
    ) -> DataFrame:
        """
        Clean string columns by trimming and removing extra whitespace.

        Args:
            df: DataFrame to clean
            columns: Specific columns to clean (None for all string columns)
            trim: Whether to trim whitespace

        Returns:
            DataFrame with cleaned strings
        """
        if columns is None:
            # Get all string columns
            columns = [
                field.name for field in df.schema.fields if str(field.dataType) == "StringType"
            ]

        cleaned_df = df

        for column in columns:
            if trim:
                cleaned_df = cleaned_df.withColumn(column, trim(col(column)))

            # Remove multiple consecutive spaces
            cleaned_df = cleaned_df.withColumn(
                column, regexp_replace(col(column), "\\s+", " ")
            )

        logger.info(f"Cleaned {len(columns)} string columns")

        return cleaned_df

    def standardize_columns(
        self,
        df: DataFrame,
        uppercase_columns: Optional[List[str]] = None,
        lowercase_columns: Optional[List[str]] = None,
        date_columns: Optional[Dict[str, str]] = None,
        timestamp_columns: Optional[Dict[str, str]] = None,
    ) -> DataFrame:
        """
        Standardize column formats.

        Args:
            df: DataFrame to standardize
            uppercase_columns: Columns to convert to uppercase
            lowercase_columns: Columns to convert to lowercase
            date_columns: Dict of column_name -> date_format
            timestamp_columns: Dict of column_name -> timestamp_format

        Returns:
            Standardized DataFrame
        """
        standardized_df = df

        # Uppercase columns
        if uppercase_columns:
            for column in uppercase_columns:
                standardized_df = standardized_df.withColumn(column, upper(col(column)))

        # Lowercase columns
        if lowercase_columns:
            for column in lowercase_columns:
                standardized_df = standardized_df.withColumn(column, lower(col(column)))

        # Date columns
        if date_columns:
            for column, date_format in date_columns.items():
                standardized_df = standardized_df.withColumn(
                    column, to_date(col(column), date_format)
                )

        # Timestamp columns
        if timestamp_columns:
            for column, timestamp_format in timestamp_columns.items():
                standardized_df = standardized_df.withColumn(
                    column, to_timestamp(col(column), timestamp_format)
                )

        logger.info("Applied column standardization")

        return standardized_df

    def handle_null_values(
        self,
        df: DataFrame,
        fill_values: Optional[Dict[str, Any]] = None,
        drop_columns: Optional[List[str]] = None,
    ) -> DataFrame:
        """
        Handle null values in DataFrame.

        Args:
            df: DataFrame to process
            fill_values: Dict of column_name -> fill_value
            drop_columns: Columns where null rows should be dropped

        Returns:
            DataFrame with nulls handled
        """
        processed_df = df

        # Fill specific null values
        if fill_values:
            processed_df = processed_df.fillna(fill_values)

        # Drop rows with nulls in specific columns
        if drop_columns:
            processed_df = processed_df.dropna(subset=drop_columns)

        logger.info("Handled null values")

        return processed_df

    def transform_bronze_to_silver(
        self,
        source_table: str,
        target_table: str,
        key_columns: List[str],
        partition_columns: Optional[List[str]] = None,
        order_by_columns: Optional[List[str]] = None,
        string_columns_to_clean: Optional[List[str]] = None,
        uppercase_columns: Optional[List[str]] = None,
        lowercase_columns: Optional[List[str]] = None,
        date_columns: Optional[Dict[str, str]] = None,
        timestamp_columns: Optional[Dict[str, str]] = None,
        null_fill_values: Optional[Dict[str, Any]] = None,
        required_columns: Optional[List[str]] = None,
        additional_filters: Optional[str] = None,
    ) -> None:
        """
        Complete transformation from bronze to silver layer.

        Args:
            source_table: Bronze table name
            target_table: Silver table name
            key_columns: Columns for surrogate key generation
            partition_columns: Columns for deduplication
            order_by_columns: Columns for ordering during deduplication
            string_columns_to_clean: String columns to clean
            uppercase_columns: Columns to uppercase
            lowercase_columns: Columns to lowercase
            date_columns: Date columns to standardize
            timestamp_columns: Timestamp columns to standardize
            null_fill_values: Values to fill for nulls
            required_columns: Columns that cannot be null
            additional_filters: Optional SQL WHERE clause
        """
        logger.info(f"Starting transformation from {source_table} to {target_table}")

        try:
            # Read bronze table
            source_full_name = f"{self.catalog}.{self.schema}.{source_table}"
            df = self.spark.table(source_full_name)

            initial_count = df.count()
            logger.info(f"Loaded {initial_count} records from bronze")

            # Apply additional filters if provided
            if additional_filters:
                df = df.filter(additional_filters)
                logger.info(
                    f"Applied filter: {additional_filters}, records: {df.count()}"
                )

            # Clean string columns
            if string_columns_to_clean:
                df = self.clean_string_columns(df, string_columns_to_clean)

            # Standardize columns
            df = self.standardize_columns(
                df,
                uppercase_columns=uppercase_columns,
                lowercase_columns=lowercase_columns,
                date_columns=date_columns,
                timestamp_columns=timestamp_columns,
            )

            # Handle null values
            df = self.handle_null_values(
                df, fill_values=null_fill_values, drop_columns=required_columns
            )

            # Deduplicate if partition columns provided
            if partition_columns and order_by_columns:
                df = self.deduplicate_data(df, partition_columns, order_by_columns)

            # Generate surrogate key
            df = self._generate_surrogate_key(df, key_columns)

            # Add processing metadata
            df = self._add_processing_metadata(df)

            # Write to silver table
            target_full_name = f"{self.catalog}.{self.schema}.{target_table}"

            df.write.format("delta").mode("overwrite").option(
                "overwriteSchema", "true"
            ).saveAsTable(target_full_name)

            final_count = df.count()
            logger.info(f"Successfully wrote {final_count} records to {target_table}")
            logger.info(f"Records filtered/deduplicated: {initial_count - final_count}")

        except Exception as e:
            logger.error(f"Error during transformation: {str(e)}")
            raise

    def merge_bronze_to_silver(
        self,
        source_table: str,
        target_table: str,
        merge_keys: List[str],
        update_columns: Optional[List[str]] = None,
    ) -> None:
        """
        Merge bronze data into existing silver table.

        Args:
            source_table: Bronze table name
            target_table: Silver table name
            merge_keys: Columns to use for merge matching
            update_columns: Columns to update (None for all)
        """
        logger.info(f"Starting merge from {source_table} to {target_table}")

        try:
            source_full_name = f"{self.catalog}.{self.schema}.{source_table}"
            target_full_name = f"{self.catalog}.{self.schema}.{target_table}"

            # Read source data
            source_df = self.spark.table(source_full_name)

            # Get Delta table
            delta_table = DeltaTable.forName(self.spark, target_full_name)

            # Build merge condition
            merge_condition = " AND ".join(
                [f"target.{key} = source.{key}" for key in merge_keys]
            )

            # Determine columns to update
            if update_columns is None:
                update_columns = [
                    field.name
                    for field in source_df.schema.fields
                    if field.name not in merge_keys
                ]

            update_dict = {col: f"source.{col}" for col in update_columns}
            insert_dict = {
                field.name: f"source.{field.name}" for field in source_df.schema.fields
            }

            # Perform merge
            delta_table.alias("target").merge(
                source_df.alias("source"), merge_condition
            ).whenMatchedUpdate(set=update_dict).whenNotMatchedInsert(
                values=insert_dict
            ).execute()

            logger.info(f"Successfully merged data into {target_table}")

        except Exception as e:
            logger.error(f"Error during merge: {str(e)}")
            raise

    def apply_scd_type2(
        self,
        source_table: str,
        target_table: str,
        business_keys: List[str],
        compare_columns: List[str],
    ) -> None:
        """
        Apply Slowly Changing Dimension Type 2 logic.

        Args:
            source_table: Source bronze table
            target_table: Target silver SCD2 table
            business_keys: Business key columns
            compare_columns: Columns to compare for changes
        """
        logger.info(f"Applying SCD Type 2 from {source_table} to {target_table}")

        try:
            source_full_name = f"{self.catalog}.{self.schema}.{source_table}"
            target_full_name = f"{self.catalog}.{self.schema}.{target_table}"

            source_df = self.spark.table(source_full_name)

            # Add SCD2 columns if not exists
            scd2_df = (
                source_df.withColumn("effective_start_date", current_timestamp())
                .withColumn("effective_end_date", lit(None).cast("timestamp"))
                .withColumn("is_current", lit(True))
            )

            if DeltaTable.isDeltaTable(self.spark, target_full_name):
                delta_table = DeltaTable.forName(self.spark, target_full_name)

                # Build merge condition
                merge_condition = " AND ".join(
                    [f"target.{key} = source.{key}" for key in business_keys]
                )
                merge_condition += " AND target.is_current = true"

                # Build change detection condition
                change_condition = " OR ".join(
                    [f"target.{col} != source.{col}" for col in compare_columns]
                )

                # Perform SCD2 merge
                delta_table.alias("target").merge(
                    scd2_df.alias("source"), merge_condition
                ).whenMatchedUpdate(
                    condition=change_condition,
                    set={
                        "effective_end_date": current_timestamp(),
                        "is_current": lit(False),
                    },
                ).whenNotMatchedInsert(
                    values={
                        **{col: f"source.{col}" for col in scd2_df.columns},
                    }
                ).execute()

                logger.info(f"Applied SCD Type 2 changes to {target_table}")
            else:
                # First load
                scd2_df.write.format("delta").mode("overwrite").saveAsTable(
                    target_full_name
                )
                logger.info(f"Created initial SCD Type 2 table {target_table}")

        except Exception as e:
            logger.error(f"Error applying SCD Type 2: {str(e)}")
            raise
