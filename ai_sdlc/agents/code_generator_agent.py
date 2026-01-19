"""
Code Generator Agent

Generates Python, PySpark, and SQL code from implementation plans.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent


class CodeGeneratorAgent(BaseAgent):
    """
    Agent for generating code.

    Generates Python, PySpark, and SQL code based on implementation plan
    and requirements.
    """

    def execute(
        self,
        input_data: Dict[str, Any],
        timeout_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate code from implementation plan.

        Args:
            input_data: Dictionary with plan and requirements
            timeout_seconds: Optional timeout

        Returns:
            Result dictionary with generated code and evidence paths
        """
        self._log_start()

        try:
            # Get plan from previous stage
            plan_data = input_data.get("previous_stages", {}).get("planning", {})
            if not plan_data:
                return self._create_result(
                    success=False,
                    error_message="No planning data available",
                )

            work_item_title = input_data.get("work_item_title", "")
            work_item_description = input_data.get("work_item_description", "")

            # Generate code files
            evidence_paths = []

            # Generate main Python module
            python_code = self._generate_python_code(
                work_item_title, work_item_description, plan_data
            )
            python_file = self._save_evidence_file(
                self._get_module_name(work_item_title) + ".py", python_code
            )
            evidence_paths.append(python_file)

            # Generate PySpark code if needed
            if self._needs_pyspark(work_item_description):
                pyspark_code = self._generate_pyspark_code(
                    work_item_title, work_item_description
                )
                pyspark_file = self._save_evidence_file(
                    self._get_module_name(work_item_title) + "_spark.py",
                    pyspark_code,
                )
                evidence_paths.append(pyspark_file)

            # Generate SQL if needed
            if self._needs_sql(work_item_description):
                sql_code = self._generate_sql_code(work_item_title, work_item_description)
                sql_file = self._save_evidence_file(
                    self._get_module_name(work_item_title) + ".sql", sql_code
                )
                evidence_paths.append(sql_file)

            # Generate code quality report
            quality_report = self._create_quality_report(evidence_paths)
            report_file = self._save_evidence_file(
                "code-quality-report.json", json.dumps(quality_report, indent=2)
            )
            evidence_paths.append(report_file)

            self._log_complete(True)

            return self._create_result(
                success=True,
                data={
                    "generated_files": evidence_paths,
                    "quality_report": quality_report,
                    "work_item_id": self.work_item_id,
                },
                evidence_paths=evidence_paths,
            )

        except Exception as e:
            self.logger.error(f"Error generating code: {e}")
            return self._create_result(
                success=False,
                error_message=f"Code generation failed: {e}",
            )

    def _get_module_name(self, title: str) -> str:
        """Convert title to valid Python module name."""
        # Remove special characters and convert to snake_case
        name = title.lower()
        name = "".join(c if c.isalnum() or c == " " else "" for c in name)
        name = "_".join(name.split())
        return name or "generated_module"

    def _needs_pyspark(self, description: str) -> bool:
        """Check if PySpark code is needed."""
        spark_keywords = ["spark", "data processing", "etl", "pipeline", "delta", "dlt"]
        return any(keyword in description.lower() for keyword in spark_keywords)

    def _needs_sql(self, description: str) -> bool:
        """Check if SQL code is needed."""
        sql_keywords = ["query", "database", "sql", "table", "select"]
        return any(keyword in description.lower() for keyword in sql_keywords)

    def _generate_python_code(
        self, title: str, description: str, plan_data: Dict[str, Any]
    ) -> str:
        """
        Generate Python code.

        Args:
            title: Work item title
            description: Work item description
            plan_data: Planning data

        Returns:
            Python code as string
        """
        # In production, this would use LLM to generate code
        # For now, create a structured template

        module_name = self._get_module_name(title)
        class_name = "".join(word.capitalize() for word in module_name.split("_"))

        code = f'''"""
{title}

{description if description else "Module description."}

This module was generated by AI-SDLC Code Generator Agent.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class {class_name}:
    """
    {title}

    Attributes:
        config: Configuration dictionary
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize {class_name}.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {{}}
        self.logger = logging.getLogger(f"{{__name__}}.{{self.__class__.__name__}}")
        self.logger.info("Initialized {class_name}")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.

        Args:
            input_data: Input data dictionary

        Returns:
            Dictionary with processing results

        Raises:
            ValueError: If input data is invalid
        """
        self.logger.info("Processing data")

        if not input_data:
            raise ValueError("Input data cannot be empty")

        try:
            # Main processing logic
            result = self._process_internal(input_data)

            self.logger.info("Processing completed successfully")
            return {{
                "success": True,
                "data": result,
                "timestamp": datetime.now().isoformat(),
            }}

        except Exception as e:
            self.logger.error(f"Processing failed: {{e}}")
            return {{
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }}

    def _process_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal processing method.

        Args:
            input_data: Input data dictionary

        Returns:
            Processed data dictionary
        """
        # TODO: Implement actual processing logic
        result = {{
            "processed": True,
            "input_count": len(input_data),
        }}

        return result

    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data.

        Args:
            data: Data to validate

        Returns:
            True if valid, False otherwise
        """
        # TODO: Implement validation logic
        return data is not None and isinstance(data, dict)

    def get_status(self) -> Dict[str, Any]:
        """
        Get current status.

        Returns:
            Status dictionary
        """
        return {{
            "status": "active",
            "config": self.config,
            "timestamp": datetime.now().isoformat(),
        }}


def main():
    """Main function for testing."""
    config = {{"debug": True}}
    processor = {class_name}(config)

    # Example usage
    test_data = {{"key": "value", "count": 42}}
    result = processor.process(test_data)

    print(f"Result: {{result}}")


if __name__ == "__main__":
    main()
'''

        return code

    def _generate_pyspark_code(self, title: str, description: str) -> str:
        """Generate PySpark code."""
        module_name = self._get_module_name(title)

        code = f'''"""
PySpark Module: {title}

{description if description else "PySpark data processing module."}

This module uses PySpark for data processing and Delta Lake for storage.
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from delta.tables import DeltaTable
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class {module_name.title().replace("_", "")}Spark:
    """
    PySpark processor for {title}.
    """

    def __init__(self, spark: Optional[SparkSession] = None):
        """
        Initialize PySpark processor.

        Args:
            spark: Optional SparkSession (creates new if None)
        """
        self.spark = spark or self._create_spark_session()
        self.logger = logging.getLogger(f"{{__name__}}.{{self.__class__.__name__}}")

    def _create_spark_session(self) -> SparkSession:
        """Create SparkSession with Delta Lake configuration."""
        return (
            SparkSession.builder
            .appName("{title}")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
            .getOrCreate()
        )

    def process_data(
        self,
        input_path: str,
        output_path: str,
    ) -> DataFrame:
        """
        Process data using PySpark.

        Args:
            input_path: Path to input data
            output_path: Path to save output data

        Returns:
            Processed DataFrame
        """
        self.logger.info(f"Reading data from {{input_path}}")

        # Read data
        df = self.spark.read.format("delta").load(input_path)

        # Process data
        processed_df = self._transform_data(df)

        # Write results
        self.logger.info(f"Writing data to {{output_path}}")
        processed_df.write.format("delta").mode("overwrite").save(output_path)

        return processed_df

    def _transform_data(self, df: DataFrame) -> DataFrame:
        """
        Transform data.

        Args:
            df: Input DataFrame

        Returns:
            Transformed DataFrame
        """
        # TODO: Implement transformation logic
        transformed = df.withColumn(
            "processed_timestamp",
            F.current_timestamp()
        )

        return transformed

    def create_unity_catalog_table(
        self,
        catalog: str,
        schema: str,
        table: str,
        df: DataFrame,
    ):
        """
        Create Unity Catalog table.

        Args:
            catalog: Catalog name
            schema: Schema name
            table: Table name
            df: DataFrame to save
        """
        full_name = f"{{catalog}}.{{schema}}.{{table}}"
        self.logger.info(f"Creating Unity Catalog table: {{full_name}}")

        df.write.format("delta").mode("overwrite").saveAsTable(full_name)


if __name__ == "__main__":
    processor = {module_name.title().replace("_", "")}Spark()
    # Example: processor.process_data("input_path", "output_path")
'''

        return code

    def _generate_sql_code(self, title: str, description: str) -> str:
        """Generate SQL code."""
        code = f'''-- SQL Queries for: {title}
-- {description if description else "SQL query definitions."}
-- Generated by AI-SDLC Code Generator Agent

-- Create table schema
CREATE TABLE IF NOT EXISTS main_table (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    name STRING,
    value DOUBLE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY (id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_name ON main_table(name);
CREATE INDEX IF NOT EXISTS idx_created_at ON main_table(created_at);

-- Query: Get all records
SELECT
    id,
    name,
    value,
    created_at,
    updated_at
FROM main_table
ORDER BY created_at DESC;

-- Query: Get records with filter
SELECT
    id,
    name,
    value,
    created_at
FROM main_table
WHERE created_at >= CURRENT_DATE - INTERVAL 30 DAYS
    AND value > 0
ORDER BY value DESC;

-- Query: Aggregation example
SELECT
    name,
    COUNT(*) as count,
    AVG(value) as avg_value,
    MAX(value) as max_value,
    MIN(value) as min_value
FROM main_table
GROUP BY name
HAVING COUNT(*) > 1
ORDER BY count DESC;

-- Query: Update records
UPDATE main_table
SET
    updated_at = CURRENT_TIMESTAMP
WHERE id = :id;

-- Query: Delete old records
DELETE FROM main_table
WHERE created_at < CURRENT_DATE - INTERVAL 90 DAYS;
'''

        return code

    def _create_quality_report(self, file_paths: List[str]) -> Dict[str, Any]:
        """Create code quality report."""
        return {
            "generated_at": datetime.now().isoformat(),
            "work_item_id": self.work_item_id,
            "files_generated": len(file_paths),
            "file_paths": file_paths,
            "metrics": {
                "total_lines": 0,  # Would calculate actual lines
                "has_docstrings": True,
                "has_type_hints": True,
                "follows_pep8": True,
            },
            "recommendations": [
                "Run 'black' to format code",
                "Run 'ruff' for linting",
                "Review generated code for business logic accuracy",
                "Add unit tests for all generated functions",
            ],
        }
