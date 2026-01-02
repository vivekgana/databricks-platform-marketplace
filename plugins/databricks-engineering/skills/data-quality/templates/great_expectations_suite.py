"""
Great Expectations Suite Template
Template for creating comprehensive quality suites with Great Expectations.
"""
import great_expectations as gx
from great_expectations.core.batch import RuntimeBatchRequest
from pyspark.sql import DataFrame, SparkSession
from typing import Dict, Any, List, Optional
from datetime import datetime


class QualitySuiteTemplate:
    """Template for Great Expectations quality suite."""

    def __init__(
        self,
        context_root_dir: Optional[str] = None,
        suite_name: str = "default_quality_suite"
    ):
        """
        Initialize quality suite.

        Args:
            context_root_dir: Path to GX context directory
            suite_name: Name for the expectation suite
        """
        self.context = gx.get_context(context_root_dir=context_root_dir)
        self.suite_name = suite_name
        self.suite = None

    def create_completeness_expectations(
        self,
        columns: List[str]
    ) -> List[gx.core.ExpectationConfiguration]:
        """Create completeness expectations for columns."""
        return [
            gx.core.ExpectationConfiguration(
                expectation_type="expect_column_values_to_not_be_null",
                kwargs={"column": col}
            )
            for col in columns
        ]

    def create_uniqueness_expectations(
        self,
        columns: List[str]
    ) -> List[gx.core.ExpectationConfiguration]:
        """Create uniqueness expectations for columns."""
        return [
            gx.core.ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_unique",
                kwargs={"column": col}
            )
            for col in columns
        ]

    def create_format_expectations(
        self,
        column_patterns: Dict[str, str]
    ) -> List[gx.core.ExpectationConfiguration]:
        """Create format validation expectations."""
        return [
            gx.core.ExpectationConfiguration(
                expectation_type="expect_column_values_to_match_regex",
                kwargs={"column": col, "regex": pattern}
            )
            for col, pattern in column_patterns.items()
        ]

    def create_range_expectations(
        self,
        column_ranges: Dict[str, tuple]
    ) -> List[gx.core.ExpectationConfiguration]:
        """Create range validation expectations."""
        return [
            gx.core.ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_between",
                kwargs={
                    "column": col,
                    "min_value": min_val,
                    "max_value": max_val
                }
            )
            for col, (min_val, max_val) in column_ranges.items()
        ]

    def create_set_expectations(
        self,
        column_values: Dict[str, List[Any]]
    ) -> List[gx.core.ExpectationConfiguration]:
        """Create value set expectations."""
        return [
            gx.core.ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_in_set",
                kwargs={"column": col, "value_set": values}
            )
            for col, values in column_values.items()
        ]

    def build_suite(
        self,
        schema_columns: List[str],
        required_columns: List[str],
        unique_columns: List[str],
        format_rules: Dict[str, str],
        range_rules: Dict[str, tuple],
        set_rules: Dict[str, List[Any]]
    ) -> gx.core.ExpectationSuite:
        """Build complete expectation suite."""

        suite = self.context.create_expectation_suite(
            expectation_suite_name=self.suite_name,
            overwrite_existing=True
        )

        # Schema validation
        suite.add_expectation(
            gx.core.ExpectationConfiguration(
                expectation_type="expect_table_columns_to_match_ordered_list",
                kwargs={"column_list": schema_columns}
            )
        )

        # Add all expectations
        for exp in self.create_completeness_expectations(required_columns):
            suite.add_expectation(exp)

        for exp in self.create_uniqueness_expectations(unique_columns):
            suite.add_expectation(exp)

        for exp in self.create_format_expectations(format_rules):
            suite.add_expectation(exp)

        for exp in self.create_range_expectations(range_rules):
            suite.add_expectation(exp)

        for exp in self.create_set_expectations(set_rules):
            suite.add_expectation(exp)

        self.context.save_expectation_suite(suite)
        self.suite = suite
        return suite

    def validate(self, df: DataFrame) -> Dict[str, Any]:
        """Run validation against dataframe."""

        batch_request = RuntimeBatchRequest(
            datasource_name="spark_datasource",
            data_connector_name="runtime_connector",
            data_asset_name="validation_data",
            runtime_parameters={"batch_data": df},
            batch_identifiers={"default_identifier_name": "default"}
        )

        checkpoint_result = self.context.run_checkpoint(
            checkpoint_name=f"{self.suite_name}_checkpoint",
            validations=[
                {
                    "batch_request": batch_request,
                    "expectation_suite_name": self.suite_name
                }
            ]
        )

        return {
            "success": checkpoint_result.success,
            "statistics": checkpoint_result.run_results,
            "timestamp": datetime.now().isoformat()
        }
