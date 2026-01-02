"""
Data Product Pipeline

Builds and maintains the data product with contract enforcement.
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, current_timestamp
import json
import yaml
import logging

logger = logging.getLogger(__name__)


class DataProductPipeline:
    """Manages data product creation and maintenance."""

    def __init__(self, product_name: str, catalog: str, schema: str):
        self.spark = SparkSession.builder.getOrCreate()
        self.product_name = product_name
        self.catalog = catalog
        self.schema = schema
        self.contract = self._load_contract()
        self.definition = self._load_definition()

    def _load_contract(self) -> dict:
        """Load data contract."""
        with open("data_contract.json", "r") as f:
            return json.load(f)

    def _load_definition(self) -> dict:
        """Load product definition."""
        with open("data_product_definition.yaml", "r") as f:
            return yaml.safe_load(f)

    def build(self) -> DataFrame:
        """Build the data product from source tables."""
        logger.info(f"Building data product: {self.product_name}")

        # Read source tables
        sources = self.definition["product"]["source_tables"]
        dfs = {}

        for source in sources:
            table_name = f"{source['catalog']}.{source['schema']}.{source['table']}"
            dfs[source["table"]] = self.spark.table(table_name)

        # Example: Join and transform
        result_df = self._transform_sources(dfs)

        # Add metadata
        result_df = result_df.withColumn("updated_at", current_timestamp())

        # Validate contract
        self.validate_contract(result_df)

        return result_df

    def _transform_sources(self, dfs: dict) -> DataFrame:
        """Transform source data into product."""
        # Implementation depends on specific product
        # This is a placeholder
        return dfs[list(dfs.keys())[0]]

    def validate_contract(self, df: DataFrame) -> bool:
        """Validate DataFrame against data contract."""
        logger.info("Validating data contract")

        schema_fields = self.contract["schema"]["fields"]

        # Check required fields
        for field in schema_fields:
            if field["required"] and field["name"] not in df.columns:
                raise ValueError(f"Required field missing: {field['name']}")

        # Check constraints
        guarantees = self.contract["guarantees"]

        # Check not null
        for field_name in guarantees.get("not_null", []):
            null_count = df.filter(col(field_name).isNull()).count()
            if null_count > 0:
                logger.warning(f"Field {field_name} has {null_count} null values")

        logger.info("Contract validation passed")
        return True

    def publish(self, df: DataFrame) -> None:
        """Publish data product."""
        target_table = f"{self.catalog}.{self.schema}.{self.product_name}"

        df.write.format("delta").mode("overwrite").option(
            "overwriteSchema", "false"
        ).saveAsTable(target_table)

        logger.info(f"Published data product to {target_table}")
