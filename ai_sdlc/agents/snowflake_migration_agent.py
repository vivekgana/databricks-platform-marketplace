"""
Snowflake to Databricks Migration Agent

Automates migration from Snowflake to Databricks including:
- Schema migration (tables, views, stored procedures)
- Data migration with validation
- SQL dialect conversion
- Performance comparison and optimization
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base_agent import BaseAgent


class SnowflakeMigrationAgent(BaseAgent):
    """
    Agent for migrating from Snowflake to Databricks.

    Handles complete migration workflow:
    - Schema discovery and mapping
    - Data type conversion
    - SQL dialect translation
    - Data migration strategies
    - Validation and testing
    """

    # Snowflake to Databricks data type mapping
    DATA_TYPE_MAPPING = {
        # Numeric types
        "NUMBER": "DECIMAL",
        "DECIMAL": "DECIMAL",
        "NUMERIC": "DECIMAL",
        "INT": "INT",
        "INTEGER": "INT",
        "BIGINT": "BIGINT",
        "SMALLINT": "SMALLINT",
        "TINYINT": "TINYINT",
        "BYTEINT": "TINYINT",
        "FLOAT": "FLOAT",
        "FLOAT4": "FLOAT",
        "FLOAT8": "DOUBLE",
        "DOUBLE": "DOUBLE",
        "DOUBLE PRECISION": "DOUBLE",
        "REAL": "FLOAT",
        # String types
        "VARCHAR": "STRING",
        "CHAR": "STRING",
        "CHARACTER": "STRING",
        "STRING": "STRING",
        "TEXT": "STRING",
        "BINARY": "BINARY",
        "VARBINARY": "BINARY",
        # Boolean type
        "BOOLEAN": "BOOLEAN",
        # Date/time types
        "DATE": "DATE",
        "DATETIME": "TIMESTAMP",
        "TIME": "STRING",  # Databricks doesn't have TIME type
        "TIMESTAMP": "TIMESTAMP",
        "TIMESTAMP_LTZ": "TIMESTAMP",
        "TIMESTAMP_NTZ": "TIMESTAMP",
        "TIMESTAMP_TZ": "TIMESTAMP",
        # Semi-structured types
        "VARIANT": "STRING",  # Store as JSON string
        "OBJECT": "STRING",  # Store as JSON string
        "ARRAY": "ARRAY<STRING>",
        # Geospatial types
        "GEOGRAPHY": "STRING",  # Store as WKT or GeoJSON
        "GEOMETRY": "STRING",
    }

    # SQL dialect conversion patterns
    SQL_CONVERSION_PATTERNS = [
        # Snowflake-specific functions to Databricks equivalents
        (r"\bIFF\s*\(", "IF("),
        (r"\bNVL\s*\(", "COALESCE("),
        (r"\bGETDATE\s*\(\s*\)", "CURRENT_TIMESTAMP()"),
        (r"\bDATEDIFF\s*\(\s*day\s*,", "DATEDIFF("),
        (r"\bTRY_CAST\s*\(", "TRY_CAST("),
        (r"\bTO_VARCHAR\s*\(", "CAST("),
        (r"\bTO_CHAR\s*\(", "CAST("),
        (r"\bTO_NUMBER\s*\(", "CAST("),
        (r"\bTO_DATE\s*\(", "TO_DATE("),
        (r"\bTO_TIMESTAMP\s*\(", "TO_TIMESTAMP("),
        # Table syntax
        (r"\bCREATE\s+OR\s+REPLACE\s+TABLE", "CREATE OR REPLACE TABLE"),
        (r"\bCREATE\s+TABLE\s+IF\s+NOT\s+EXISTS", "CREATE TABLE IF NOT EXISTS"),
        # Comments
        (r"--", "--"),
        (r"/\*", "/*"),
    ]

    def execute(
        self, input_data: Dict[str, Any], timeout_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute Snowflake to Databricks migration.

        Args:
            input_data: Dictionary with:
                - migration_type: Type of migration (schema, data, sql, full)
                - source_schema: Snowflake schema definition (for schema migration)
                - source_sql: Snowflake SQL to convert (for SQL migration)
                - source_tables: List of tables to migrate (for data migration)
                - target_catalog: Target Unity Catalog name
                - target_schema: Target schema name
                - migration_strategy: Data migration strategy (bulk, incremental, streaming)
                - validate: Enable validation (default: True)

        Returns:
            Result dictionary with migration artifacts
        """
        self._log_start()

        try:
            migration_type = input_data.get("migration_type", "full")
            source_schema = input_data.get("source_schema", {})
            source_sql = input_data.get("source_sql", "")
            source_tables = input_data.get("source_tables", [])
            target_catalog = input_data.get("target_catalog", "main")
            target_schema = input_data.get("target_schema", "default")
            migration_strategy = input_data.get("migration_strategy", "bulk")
            validate = input_data.get("validate", True)

            results = {}
            evidence_paths = []

            # Schema migration
            if migration_type in ["schema", "full"]:
                schema_result = self._migrate_schema(
                    source_schema, target_catalog, target_schema
                )
                results["schema_migration"] = schema_result

                # Save schema migration artifacts
                schema_file = self._save_evidence_file(
                    "schema-migration.sql", schema_result["ddl"]
                )
                evidence_paths.append(schema_file)

            # SQL dialect conversion
            if migration_type in ["sql", "full"] and source_sql:
                sql_result = self._convert_sql(source_sql)
                results["sql_conversion"] = sql_result

                # Save converted SQL
                sql_file = self._save_evidence_file(
                    "converted-sql.sql", sql_result["converted_sql"]
                )
                evidence_paths.append(sql_file)

            # Data migration planning
            if migration_type in ["data", "full"] and source_tables:
                data_result = self._plan_data_migration(
                    source_tables, target_catalog, target_schema, migration_strategy
                )
                results["data_migration"] = data_result

                # Save migration plan
                plan_file = self._save_evidence_file(
                    "data-migration-plan.md", data_result["plan"]
                )
                evidence_paths.append(plan_file)

            # Generate comprehensive migration guide
            migration_guide = self._generate_migration_guide(
                migration_type, results, target_catalog, target_schema
            )
            guide_file = self._save_evidence_file("migration-guide.md", migration_guide)
            evidence_paths.append(guide_file)

            # Generate validation tests if requested
            if validate:
                validation_tests = self._generate_validation_tests(results)
                tests_file = self._save_evidence_file(
                    "validation-tests.py", validation_tests
                )
                evidence_paths.append(tests_file)

            self._log_complete(True)

            return self._create_result(
                success=True,
                data={
                    "migration_type": migration_type,
                    "target_catalog": target_catalog,
                    "target_schema": target_schema,
                    "migration_strategy": migration_strategy,
                    "results": results,
                    "guide_file": guide_file,
                },
                evidence_paths=evidence_paths,
            )

        except Exception as e:
            self.logger.error(f"Error during Snowflake migration: {e}")
            return self._create_result(
                success=False,
                error_message=f"Migration failed: {e}",
            )

    def _migrate_schema(
        self, source_schema: Dict[str, Any], target_catalog: str, target_schema: str
    ) -> Dict[str, Any]:
        """Migrate Snowflake schema to Databricks."""
        tables = source_schema.get("tables", [])
        views = source_schema.get("views", [])

        ddl_statements = []
        table_mappings = []

        # Generate CREATE TABLE statements
        for table in tables:
            table_name = table.get("name")
            columns = table.get("columns", [])
            primary_key = table.get("primary_key", [])
            comment = table.get("comment", "")

            # Convert table definition
            converted_table = self._convert_table_definition(
                table_name, columns, primary_key, comment, target_catalog, target_schema
            )

            ddl_statements.append(converted_table["ddl"])
            table_mappings.append(converted_table["mapping"])

        # Generate CREATE VIEW statements
        for view in views:
            view_name = view.get("name")
            view_sql = view.get("definition", "")

            # Convert view definition
            converted_view = self._convert_view_definition(
                view_name, view_sql, target_catalog, target_schema
            )

            ddl_statements.append(converted_view["ddl"])

        return {
            "tables_migrated": len(tables),
            "views_migrated": len(views),
            "ddl": "\n\n".join(ddl_statements),
            "table_mappings": table_mappings,
        }

    def _convert_table_definition(
        self,
        table_name: str,
        columns: List[Dict[str, Any]],
        primary_key: List[str],
        comment: str,
        target_catalog: str,
        target_schema: str,
    ) -> Dict[str, Any]:
        """Convert Snowflake table definition to Databricks."""
        full_table_name = f"{target_catalog}.{target_schema}.{table_name}"

        # Build column definitions
        column_defs = []
        type_conversions = []

        for col in columns:
            col_name = col.get("name")
            col_type = col.get("type", "STRING").upper()
            nullable = col.get("nullable", True)
            col_comment = col.get("comment", "")

            # Convert data type
            databricks_type = self._convert_data_type(col_type)

            # Track type conversion
            if col_type != databricks_type:
                type_conversions.append(
                    {
                        "column": col_name,
                        "snowflake_type": col_type,
                        "databricks_type": databricks_type,
                    }
                )

            # Build column definition
            nullable_str = "" if nullable else " NOT NULL"
            comment_str = f" COMMENT '{col_comment}'" if col_comment else ""

            column_defs.append(
                f"  {col_name} {databricks_type}{nullable_str}{comment_str}"
            )

        # Build DDL statement
        ddl = f"CREATE TABLE IF NOT EXISTS {full_table_name} (\n"
        ddl += ",\n".join(column_defs)
        ddl += "\n)"

        # Add table properties
        ddl += "\nUSING DELTA"

        if comment:
            ddl += f"\nCOMMENT '{comment}'"

        # Add table properties for optimization
        ddl += "\nTBLPROPERTIES ("
        ddl += "\n  'delta.autoOptimize.optimizeWrite' = 'true',"
        ddl += "\n  'delta.autoOptimize.autoCompact' = 'true'"
        ddl += "\n)"

        ddl += ";"

        return {
            "ddl": ddl,
            "mapping": {
                "source_table": table_name,
                "target_table": full_table_name,
                "columns": len(columns),
                "type_conversions": type_conversions,
            },
        }

    def _convert_view_definition(
        self, view_name: str, view_sql: str, target_catalog: str, target_schema: str
    ) -> Dict[str, Any]:
        """Convert Snowflake view definition to Databricks."""
        full_view_name = f"{target_catalog}.{target_schema}.{view_name}"

        # Convert SQL dialect
        converted_sql = self._convert_sql(view_sql)["converted_sql"]

        ddl = f"CREATE OR REPLACE VIEW {full_view_name} AS\n{converted_sql};"

        return {"ddl": ddl}

    def _convert_data_type(self, snowflake_type: str) -> str:
        """Convert Snowflake data type to Databricks."""
        # Handle parameterized types (e.g., VARCHAR(100), DECIMAL(10,2))
        type_match = re.match(r"([A-Z_]+)(?:\(([^)]+)\))?", snowflake_type)

        if not type_match:
            return "STRING"  # Default fallback

        base_type = type_match.group(1)
        params = type_match.group(2)

        # Get base type mapping
        databricks_type = self.DATA_TYPE_MAPPING.get(base_type, "STRING")

        # Handle parameterized types
        if params and base_type in ["VARCHAR", "CHAR", "NUMBER", "DECIMAL", "NUMERIC"]:
            if base_type in ["VARCHAR", "CHAR"]:
                # Databricks STRING doesn't need length parameter
                return "STRING"
            else:
                # Keep precision/scale for numeric types
                return f"{databricks_type}({params})"

        return databricks_type

    def _convert_sql(self, source_sql: str) -> Dict[str, Any]:
        """Convert Snowflake SQL to Databricks SQL."""
        converted_sql = source_sql
        conversions_applied = []

        for pattern, replacement in self.SQL_CONVERSION_PATTERNS:
            if re.search(pattern, converted_sql, re.IGNORECASE):
                converted_sql = re.sub(
                    pattern, replacement, converted_sql, flags=re.IGNORECASE
                )
                conversions_applied.append(
                    {"pattern": pattern, "replacement": replacement}
                )

        return {
            "original_sql": source_sql,
            "converted_sql": converted_sql,
            "conversions_applied": conversions_applied,
            "manual_review_needed": self._needs_manual_review(source_sql),
        }

    def _needs_manual_review(self, sql: str) -> List[str]:
        """Identify SQL features that need manual review."""
        review_items = []

        # Check for Snowflake-specific features
        if "QUALIFY" in sql.upper():
            review_items.append("QUALIFY clause - no direct Databricks equivalent")

        if "FLATTEN" in sql.upper():
            review_items.append("FLATTEN function - use EXPLODE or LATERAL VIEW")

        if "LATERAL" in sql.upper():
            review_items.append("LATERAL join - verify compatibility")

        if re.search(r"\$\d+", sql):
            review_items.append("Positional parameters ($1, $2) - use named parameters")

        if "COPY INTO" in sql.upper():
            review_items.append("COPY INTO - use Databricks Auto Loader or COPY INTO")

        if "STAGE" in sql.upper():
            review_items.append("Snowflake stages - use cloud storage paths")

        if "STREAM" in sql.upper():
            review_items.append(
                "Snowflake streams - use Delta Live Tables or streaming"
            )

        if "TASK" in sql.upper():
            review_items.append("Snowflake tasks - use Databricks jobs or workflows")

        return review_items

    def _plan_data_migration(
        self,
        source_tables: List[str],
        target_catalog: str,
        target_schema: str,
        migration_strategy: str,
    ) -> Dict[str, Any]:
        """Plan data migration strategy."""
        migration_steps = []

        for table in source_tables:
            step = self._generate_migration_step(
                table, target_catalog, target_schema, migration_strategy
            )
            migration_steps.append(step)

        # Generate migration plan markdown
        plan = self._generate_migration_plan_doc(migration_steps, migration_strategy)

        return {
            "tables": len(source_tables),
            "strategy": migration_strategy,
            "migration_steps": migration_steps,
            "plan": plan,
        }

    def _generate_migration_step(
        self,
        table_name: str,
        target_catalog: str,
        target_schema: str,
        migration_strategy: str,
    ) -> Dict[str, Any]:
        """Generate migration step for a table."""
        target_table = f"{target_catalog}.{target_schema}.{table_name}"

        if migration_strategy == "bulk":
            method = "Full table copy"
            code = f"""
-- Bulk migration for {table_name}
CREATE OR REPLACE TABLE {target_table}
AS SELECT * FROM snowflake_connection.{table_name};

-- Verify row count
SELECT COUNT(*) as row_count FROM {target_table};
"""

        elif migration_strategy == "incremental":
            method = "Incremental load with watermark"
            code = f"""
-- Incremental migration for {table_name}
MERGE INTO {target_table} AS target
USING (
  SELECT * FROM snowflake_connection.{table_name}
  WHERE updated_at > (SELECT MAX(updated_at) FROM {target_table})
) AS source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
"""

        elif migration_strategy == "streaming":
            method = "Streaming ingestion"
            code = f"""
-- Streaming migration for {table_name}
-- Use Databricks Auto Loader or Structured Streaming
spark.readStream \\
  .format("snowflake") \\
  .option("dbtable", "{table_name}") \\
  .load() \\
  .writeStream \\
  .format("delta") \\
  .option("checkpointLocation", "/checkpoints/{table_name}") \\
  .toTable("{target_table}")
"""

        else:
            method = "Custom migration"
            code = f"-- Define custom migration logic for {table_name}"

        return {
            "table": table_name,
            "target": target_table,
            "method": method,
            "migration_code": code,
        }

    def _generate_migration_plan_doc(
        self, migration_steps: List[Dict[str, Any]], migration_strategy: str
    ) -> str:
        """Generate data migration plan documentation."""
        doc = f"""# Data Migration Plan

**Migration Strategy:** {migration_strategy}
**Tables to Migrate:** {len(migration_steps)}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Migration Steps

"""

        for idx, step in enumerate(migration_steps, 1):
            doc += f"""
### Step {idx}: Migrate {step['table']}

**Target Table:** {step['target']}
**Method:** {step['method']}

**Migration Code:**
```sql
{step['migration_code']}
```

---
"""

        doc += """
## Validation Checklist

For each migrated table:
- [ ] Row count matches source
- [ ] Data types are correct
- [ ] NULL values preserved
- [ ] Primary keys migrated
- [ ] Sample data spot-checked
- [ ] Performance baseline established

---

## Rollback Plan

If migration fails:
1. Drop target tables: `DROP TABLE IF EXISTS {target_table}`
2. Review error logs
3. Fix issues and retry
4. Verify data integrity

---

**Generated by:** AI-SDLC Snowflake Migration Agent
"""

        return doc

    def _generate_migration_guide(
        self,
        migration_type: str,
        results: Dict[str, Any],
        target_catalog: str,
        target_schema: str,
    ) -> str:
        """Generate comprehensive migration guide."""
        doc = f"""# Snowflake to Databricks Migration Guide

**Work Item ID:** {self.work_item_id}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Migration Type:** {migration_type}
**Target:** {target_catalog}.{target_schema}

---

## Overview

This guide provides step-by-step instructions for migrating from Snowflake to Databricks.

### Migration Components

"""

        if "schema_migration" in results:
            schema_result = results["schema_migration"]
            doc += f"""
#### Schema Migration
- Tables migrated: {schema_result['tables_migrated']}
- Views migrated: {schema_result['views_migrated']}
- DDL file: `schema-migration.sql`
"""

        if "sql_conversion" in results:
            sql_result = results["sql_conversion"]
            doc += f"""
#### SQL Conversion
- Conversions applied: {len(sql_result['conversions_applied'])}
- Manual review items: {len(sql_result['manual_review_needed'])}
- Converted SQL file: `converted-sql.sql`
"""

        if "data_migration" in results:
            data_result = results["data_migration"]
            doc += f"""
#### Data Migration
- Tables to migrate: {data_result['tables']}
- Migration strategy: {data_result['strategy']}
- Migration plan: `data-migration-plan.md`
"""

        doc += (
            """
---

## Step-by-Step Migration

### 1. Pre-Migration

**Setup Snowflake Connection:**
```python
# Configure Snowflake connection in Databricks
spark.conf.set("snowflake.url", "account.snowflakecomputing.com")
spark.conf.set("snowflake.user", "username")
spark.conf.set("snowflake.password", dbutils.secrets.get("scope", "snowflake-password"))
spark.conf.set("snowflake.database", "source_database")
spark.conf.set("snowflake.schema", "source_schema")
```

**Create Target Catalog and Schema:**
```sql
-- Create catalog if not exists
CREATE CATALOG IF NOT EXISTS """
            + target_catalog
            + """;

-- Create schema
CREATE SCHEMA IF NOT EXISTS """
            + target_catalog
            + "."
            + target_schema
            + """;

-- Grant permissions
GRANT ALL PRIVILEGES ON CATALOG """
            + target_catalog
            + """ TO `data_engineers`;
GRANT ALL PRIVILEGES ON SCHEMA """
            + target_catalog
            + "."
            + target_schema
            + """ TO `data_engineers`;
```

### 2. Schema Migration

Run the generated DDL statements from `schema-migration.sql`:

```bash
databricks sql execute --file schema-migration.sql
```

### 3. Data Migration

Execute data migration according to `data-migration-plan.md`.

**For Bulk Migration:**
```python
# Read from Snowflake
df = spark.read \\
  .format("snowflake") \\
  .option("dbtable", "source_table") \\
  .load()

# Write to Delta
df.write \\
  .format("delta") \\
  .mode("overwrite") \\
  .saveAsTable("target_catalog.target_schema.target_table")
```

**For Incremental Migration:**
```python
# Use Delta MERGE for incremental loads
# See data-migration-plan.md for table-specific code
```

### 4. SQL Conversion

Review converted SQL in `converted-sql.sql` and apply manual fixes as needed.

### 5. Validation

Run validation tests from `validation-tests.py`:

```bash
pytest validation-tests.py -v
```

### 6. Performance Optimization

**Optimize Delta Tables:**
```sql
-- Optimize for better query performance
OPTIMIZE target_catalog.target_schema.table_name;

-- Z-order for frequently filtered columns
OPTIMIZE target_catalog.target_schema.table_name
ZORDER BY (date_column, id_column);
```

**Enable Auto-Optimization:**
```sql
ALTER TABLE target_catalog.target_schema.table_name
SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);
```

---

## Key Differences: Snowflake vs Databricks

### Data Types
- `VARIANT` → Store as `STRING` (JSON)
- `TIME` → Store as `STRING` or convert to `TIMESTAMP`
- `GEOGRAPHY/GEOMETRY` → Store as `STRING` (WKT or GeoJSON)

### SQL Functions
- `IFF()` → `IF()`
- `NVL()` → `COALESCE()`
- `DATEIFF(day, ...)` → `DATEDIFF(...)`
- `FLATTEN()` → `EXPLODE()` or `LATERAL VIEW`

### Features
- **Snowflake Streams** → Delta Live Tables or Structured Streaming
- **Snowflake Tasks** → Databricks Jobs or Workflows
- **Snowflake Stages** → Cloud storage (S3, ADLS, GCS)
- **QUALIFY clause** → Use window functions with WHERE clause

---

## Troubleshooting

### Issue: Connection timeout
**Solution:** Increase timeout settings:
```python
spark.conf.set("snowflake.timeout", "600")
```

### Issue: Data type mismatch
**Solution:** Review `schema-migration.sql` and adjust data types manually.

### Issue: Performance degradation
**Solution:**
1. Enable Photon for faster query execution
2. Use Z-ordering on frequently filtered columns
3. Enable auto-optimization
4. Review query plans with `EXPLAIN`

---

## Post-Migration Checklist

- [ ] All tables migrated successfully
- [ ] Row counts validated
- [ ] Data types verified
- [ ] Views recreated and tested
- [ ] SQL queries converted and tested
- [ ] Performance benchmarked
- [ ] Users granted appropriate permissions
- [ ] Documentation updated
- [ ] Old Snowflake resources decommissioned

---

**Generated by:** AI-SDLC Snowflake Migration Agent
"""
        )

        return doc

    def _generate_validation_tests(self, results: Dict[str, Any]) -> str:
        """Generate validation test code."""
        code = '''"""
Snowflake to Databricks Migration Validation Tests
"""

import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    """Create Spark session."""
    return SparkSession.builder.appName("migration-validation").getOrCreate()


class TestSchemaValidation:
    """Validate schema migration."""

'''

        if "schema_migration" in results:
            schema_result = results["schema_migration"]
            for mapping in schema_result.get("table_mappings", []):
                target_table = mapping["target_table"]
                code += f'''
    def test_table_{mapping["source_table"]}_exists(self, spark):
        """Test that {mapping["source_table"]} was migrated."""
        result = spark.sql("SHOW TABLES IN {target_table.rsplit('.', 1)[0]}").filter(
            f"tableName = '{mapping['source_table']}'"
        )
        assert result.count() > 0, "Table {mapping['source_table']} not found"

    def test_table_{mapping["source_table"]}_column_count(self, spark):
        """Test that {mapping["source_table"]} has correct number of columns."""
        df = spark.table("{target_table}")
        assert len(df.columns) == {mapping['columns']}, "Column count mismatch"
'''

        code += '''

class TestDataValidation:
    """Validate data migration."""

    def test_row_counts_match(self, spark):
        """Test that row counts match between source and target."""
        # TODO: Implement row count comparison
        # source_count = spark.read.format("snowflake").option("query", "SELECT COUNT(*) FROM source").load()
        # target_count = spark.sql("SELECT COUNT(*) FROM target").collect()[0][0]
        # assert source_count == target_count
        pass

    def test_null_values_preserved(self, spark):
        """Test that NULL values are preserved."""
        # TODO: Implement NULL value validation
        pass

    def test_data_types_correct(self, spark):
        """Test that data types are correct."""
        # TODO: Implement data type validation
        pass


class TestQueryValidation:
    """Validate SQL query conversion."""

    def test_converted_queries_execute(self, spark):
        """Test that converted queries execute without errors."""
        # TODO: Execute converted queries and verify results
        pass

    def test_query_results_match(self, spark):
        """Test that query results match between Snowflake and Databricks."""
        # TODO: Compare query results
        pass
'''

        return code
