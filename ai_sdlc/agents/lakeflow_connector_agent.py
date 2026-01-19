"""
Lakeflow Connector Agent

Generates low-latency Lakeflow job configurations and connector setups.
Supports real-time data ingestion with optimized Delta Live Tables (DLT) pipelines.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent


class LakeflowConnectorAgent(BaseAgent):
    """
    Agent for designing low-latency Lakeflow jobs and connectors.

    Generates optimized configurations for:
    - Real-time data ingestion pipelines
    - Delta Live Tables with streaming
    - Connector configurations (Kafka, Kinesis, Event Hubs)
    - Low-latency table optimization
    - Change Data Capture (CDC) pipelines
    """

    # Connector type templates
    CONNECTOR_TYPES = {
        "kafka": {
            "source_format": "kafka",
            "required_params": ["kafka.bootstrap.servers", "subscribe"],
            "optional_params": [
                "startingOffsets",
                "kafka.security.protocol",
                "kafka.sasl.mechanism",
            ],
        },
        "kinesis": {
            "source_format": "kinesis",
            "required_params": ["streamName", "region"],
            "optional_params": ["startingPosition", "awsAccessKey", "awsSecretKey"],
        },
        "eventhub": {
            "source_format": "eventhub",
            "required_params": ["eventhubs.connectionString"],
            "optional_params": ["eventhubs.consumerGroup", "startingPosition"],
        },
        "autoloader": {
            "source_format": "cloudFiles",
            "required_params": ["cloudFiles.format", "path"],
            "optional_params": [
                "cloudFiles.schemaLocation",
                "cloudFiles.inferColumnTypes",
            ],
        },
    }

    # Pipeline optimization presets
    PIPELINE_PRESETS = {
        "low_latency": {
            "trigger": "continuous",
            "max_shuffle_partitions": 200,
            "enable_optimization": True,
            "checkpoint_interval": "5 seconds",
        },
        "balanced": {
            "trigger": "once_per_minute",
            "max_shuffle_partitions": 400,
            "enable_optimization": True,
            "checkpoint_interval": "30 seconds",
        },
        "high_throughput": {
            "trigger": "once",
            "max_shuffle_partitions": 800,
            "enable_optimization": True,
            "checkpoint_interval": "2 minutes",
        },
    }

    def execute(
        self, input_data: Dict[str, Any], timeout_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate Lakeflow connector configuration and DLT pipeline.

        Args:
            input_data: Dictionary with:
                - pipeline_name: Name of the pipeline
                - connector_type: Type of connector (kafka, kinesis, eventhub, autoloader)
                - connector_config: Connector-specific configuration
                - target_table: Target Delta table name
                - target_catalog: Unity Catalog name
                - target_schema: Schema name
                - latency_mode: Optimization mode (low_latency, balanced, high_throughput)
                - enable_cdc: Enable Change Data Capture (default: False)
                - enable_scd2: Enable Slowly Changing Dimension Type 2 (default: False)
                - checkpoint_location: Checkpoint storage location

        Returns:
            Result dictionary with pipeline and connector configuration
        """
        self._log_start()

        try:
            pipeline_name = input_data.get("pipeline_name")
            connector_type = input_data.get("connector_type")
            connector_config = input_data.get("connector_config", {})
            target_table = input_data.get("target_table")
            target_catalog = input_data.get("target_catalog", "main")
            target_schema = input_data.get("target_schema", "default")
            latency_mode = input_data.get("latency_mode", "balanced")
            enable_cdc = input_data.get("enable_cdc", False)
            enable_scd2 = input_data.get("enable_scd2", False)
            checkpoint_location = input_data.get("checkpoint_location")

            if not pipeline_name:
                return self._create_result(
                    success=False,
                    error_message="Pipeline name is required",
                )

            if not connector_type:
                return self._create_result(
                    success=False,
                    error_message="Connector type is required",
                )

            if connector_type not in self.CONNECTOR_TYPES:
                return self._create_result(
                    success=False,
                    error_message=f"Invalid connector type: {connector_type}. Must be one of: {', '.join(self.CONNECTOR_TYPES.keys())}",
                )

            if not target_table:
                return self._create_result(
                    success=False,
                    error_message="Target table name is required",
                )

            # Validate connector configuration
            validation_result = self._validate_connector_config(
                connector_type, connector_config
            )
            if not validation_result["valid"]:
                return self._create_result(
                    success=False,
                    error_message=f"Connector configuration validation failed: {validation_result['errors']}",
                )

            # Generate DLT pipeline configuration
            dlt_pipeline = self._generate_dlt_pipeline(
                pipeline_name=pipeline_name,
                connector_type=connector_type,
                connector_config=connector_config,
                target_table=target_table,
                target_catalog=target_catalog,
                target_schema=target_schema,
                latency_mode=latency_mode,
                enable_cdc=enable_cdc,
                enable_scd2=enable_scd2,
                checkpoint_location=checkpoint_location,
            )

            # Generate notebook code for DLT
            notebook_code = self._generate_dlt_notebook(
                pipeline_name=pipeline_name,
                connector_type=connector_type,
                connector_config=connector_config,
                target_table=target_table,
                target_catalog=target_catalog,
                target_schema=target_schema,
                enable_cdc=enable_cdc,
                enable_scd2=enable_scd2,
            )

            # Generate documentation
            pipeline_doc = self._generate_pipeline_documentation(
                pipeline_name, dlt_pipeline, connector_type, latency_mode
            )

            # Save artifacts
            pipeline_config_file = self._save_evidence_file(
                f"lakeflow-{pipeline_name.lower().replace(' ', '-')}-pipeline.json",
                json.dumps(dlt_pipeline, indent=2),
            )

            notebook_file = self._save_evidence_file(
                f"lakeflow-{pipeline_name.lower().replace(' ', '-')}-notebook.py",
                notebook_code,
            )

            doc_file = self._save_evidence_file(
                f"lakeflow-{pipeline_name.lower().replace(' ', '-')}-design.md",
                pipeline_doc,
            )

            evidence_paths = [pipeline_config_file, notebook_file, doc_file]

            self._log_complete(True)

            return self._create_result(
                success=True,
                data={
                    "pipeline_name": pipeline_name,
                    "connector_type": connector_type,
                    "target_table": f"{target_catalog}.{target_schema}.{target_table}",
                    "latency_mode": latency_mode,
                    "enable_cdc": enable_cdc,
                    "enable_scd2": enable_scd2,
                    "pipeline_config": dlt_pipeline,
                    "pipeline_config_file": pipeline_config_file,
                    "notebook_file": notebook_file,
                    "doc_file": doc_file,
                },
                evidence_paths=evidence_paths,
            )

        except Exception as e:
            self.logger.error(f"Error generating Lakeflow configuration: {e}")
            return self._create_result(
                success=False,
                error_message=f"Lakeflow design failed: {e}",
            )

    def _validate_connector_config(
        self, connector_type: str, connector_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate connector configuration has required parameters."""
        errors = []
        warnings = []

        connector_def = self.CONNECTOR_TYPES[connector_type]
        required_params = connector_def["required_params"]

        for param in required_params:
            if param not in connector_config:
                errors.append(f"Missing required parameter: {param}")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _generate_dlt_pipeline(
        self,
        pipeline_name: str,
        connector_type: str,
        connector_config: Dict[str, Any],
        target_table: str,
        target_catalog: str,
        target_schema: str,
        latency_mode: str,
        enable_cdc: bool,
        enable_scd2: bool,
        checkpoint_location: Optional[str],
    ) -> Dict[str, Any]:
        """Generate DLT pipeline configuration."""
        preset = self.PIPELINE_PRESETS.get(
            latency_mode, self.PIPELINE_PRESETS["balanced"]
        )

        pipeline = {
            "name": pipeline_name,
            "catalog": target_catalog,
            "target": target_schema,
            "continuous": latency_mode == "low_latency",
            "channel": "CURRENT",
            "photon": True,
            "libraries": [
                {
                    "notebook": {
                        "path": f"/Workspace/dlt/{pipeline_name.lower().replace(' ', '_')}"
                    }
                }
            ],
            "configuration": {
                "spark.sql.shuffle.partitions": str(preset["max_shuffle_partitions"]),
                "pipelines.trigger.interval": preset["checkpoint_interval"],
                "spark.databricks.delta.optimizeWrite.enabled": "true",
                "spark.databricks.delta.autoCompact.enabled": "true",
            },
            "clusters": [
                {
                    "label": "default",
                    "autoscale": {
                        "min_workers": 1,
                        "max_workers": 5,
                        "mode": "ENHANCED",
                    },
                    "spark_conf": {
                        "spark.databricks.cluster.profile": "singleNode",
                        "spark.master": "local[*, 4]",
                    },
                    "custom_tags": {
                        "pipeline": pipeline_name,
                        "connector_type": connector_type,
                        "latency_mode": latency_mode,
                    },
                }
            ],
        }

        # Add checkpoint location if provided
        if checkpoint_location:
            pipeline["storage"] = checkpoint_location

        # Add CDC configuration if enabled
        if enable_cdc:
            pipeline["configuration"]["pipelines.enableTrackHistory"] = "true"
            pipeline["configuration"]["pipelines.cdc.enabled"] = "true"

        return pipeline

    def _generate_dlt_notebook(
        self,
        pipeline_name: str,
        connector_type: str,
        connector_config: Dict[str, Any],
        target_table: str,
        target_catalog: str,
        target_schema: str,
        enable_cdc: bool,
        enable_scd2: bool,
    ) -> str:
        """Generate DLT notebook Python code."""
        code = f'''# Databricks notebook source
# MAGIC %md
# MAGIC # {pipeline_name}
# MAGIC
# MAGIC **Connector Type:** {connector_type}
# MAGIC **Target Table:** {target_catalog}.{target_schema}.{target_table}
# MAGIC **CDC Enabled:** {enable_cdc}
# MAGIC **SCD Type 2 Enabled:** {enable_scd2}
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ## Architecture
# MAGIC
# MAGIC ```
# MAGIC {connector_type.upper()} Source → Bronze (Raw) → Silver (Cleansed) → Gold (Business)
# MAGIC ```

# COMMAND ----------

import dlt
from pyspark.sql import functions as F
from pyspark.sql.types import *

# COMMAND ----------

# MAGIC %md
# MAGIC ## Bronze Layer - Raw Ingestion

# COMMAND ----------

@dlt.table(
    name="{target_table}_bronze",
    comment="Raw data from {connector_type} source",
    table_properties={{
        "quality": "bronze",
        "pipelines.autoOptimize.managed": "true"
    }}
)
def {target_table}_bronze():
    """
    Bronze layer: Raw data ingestion from {connector_type}.

    This table contains unmodified data from the source with metadata columns.
    """
'''

        # Add connector-specific read logic
        if connector_type == "kafka":
            code += f"""    return (
        spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", "{connector_config.get('kafka.bootstrap.servers', 'localhost:9092')}")
            .option("subscribe", "{connector_config.get('subscribe', 'topic')}")
            .option("startingOffsets", "{connector_config.get('startingOffsets', 'latest')}")
            .load()
            .select(
                F.col("key").cast("string").alias("event_key"),
                F.col("value").cast("string").alias("event_value"),
                F.col("topic"),
                F.col("partition"),
                F.col("offset"),
                F.col("timestamp").alias("kafka_timestamp"),
                F.current_timestamp().alias("ingestion_timestamp")
            )
    )
"""
        elif connector_type == "kinesis":
            code += f"""    return (
        spark.readStream
            .format("kinesis")
            .option("streamName", "{connector_config.get('streamName', 'stream')}")
            .option("region", "{connector_config.get('region', 'us-east-1')}")
            .option("startingPosition", "{connector_config.get('startingPosition', 'latest')}")
            .load()
            .select(
                F.col("partitionKey").alias("event_key"),
                F.col("data").cast("string").alias("event_value"),
                F.col("approximateArrivalTimestamp").alias("kinesis_timestamp"),
                F.current_timestamp().alias("ingestion_timestamp")
            )
    )
"""
        elif connector_type == "eventhub":
            code += f"""    return (
        spark.readStream
            .format("eventhubs")
            .option("eventhubs.connectionString", "{connector_config.get('eventhubs.connectionString', '')}")
            .option("eventhubs.consumerGroup", "{connector_config.get('eventhubs.consumerGroup', '$Default')}")
            .load()
            .select(
                F.col("body").cast("string").alias("event_value"),
                F.col("enqueuedTime").alias("eventhub_timestamp"),
                F.current_timestamp().alias("ingestion_timestamp")
            )
    )
"""
        elif connector_type == "autoloader":
            code += f"""    return (
        spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "{connector_config.get('cloudFiles.format', 'json')}")
            .option("cloudFiles.schemaLocation", "{connector_config.get('cloudFiles.schemaLocation', '/tmp/schema')}")
            .load("{connector_config.get('path', '/path/to/data')}")
            .select(
                "*",
                F.current_timestamp().alias("ingestion_timestamp")
            )
    )
"""

        code += (
            '''
# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver Layer - Cleansed Data

# COMMAND ----------

@dlt.table(
    name="'''
            + f"{target_table}_silver"
            + """",
    comment="Cleansed and validated data",
    table_properties={
        "quality": "silver",
        "pipelines.autoOptimize.managed": "true"
    }
)
@dlt.expect_or_drop("valid_event", "event_value IS NOT NULL")
def """
            + f"{target_table}_silver"
            + '''():
    """
    Silver layer: Cleansed and validated data.

    This table contains parsed JSON data with data quality checks applied.
    """
    return (
        dlt.read_stream("'''
            + f"{target_table}_bronze"
            + '''")
            .select(
                F.from_json(F.col("event_value"), "struct<id:string, timestamp:timestamp, data:string>").alias("parsed"),
                "*"
            )
            .select(
                F.col("parsed.id").alias("event_id"),
                F.col("parsed.timestamp").alias("event_timestamp"),
                F.col("parsed.data").alias("event_data"),
                F.col("ingestion_timestamp")
            )
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold Layer - Business Logic

# COMMAND ----------

@dlt.table(
    name="'''
            + f"{target_table}"
            + """",
    comment="Business-ready aggregated data",
    table_properties={
        "quality": "gold",
        "pipelines.autoOptimize.managed": "true"
    }
)
def """
            + f"{target_table}"
            + '''():
    """
    Gold layer: Business-ready data with aggregations and enrichments.

    This table contains the final business-ready data.
    """
    return (
        dlt.read_stream("'''
            + f"{target_table}_silver"
            + """")
            # Add your business logic transformations here
            .select("*")
    )
"""
        )

        # Add CDC logic if enabled
        if enable_cdc:
            code += (
                '''
# COMMAND ----------

# MAGIC %md
# MAGIC ## CDC (Change Data Capture)

# COMMAND ----------

@dlt.table(
    name="'''
                + f"{target_table}_cdc"
                + """",
    comment="Change data capture stream"
)
def """
                + f"{target_table}_cdc"
                + '''():
    """
    CDC table for tracking changes over time.
    """
    return (
        dlt.read_stream("'''
                + f"{target_table}_silver"
                + """")
            .select(
                "*",
                F.lit("INSERT").alias("operation"),
                F.current_timestamp().alias("cdc_timestamp")
            )
    )
"""
            )

        # Add SCD Type 2 logic if enabled
        if enable_scd2:
            code += (
                '''
# COMMAND ----------

# MAGIC %md
# MAGIC ## SCD Type 2 (Slowly Changing Dimension)

# COMMAND ----------

@dlt.table(
    name="'''
                + f"{target_table}_scd2"
                + """",
    comment="Slowly Changing Dimension Type 2"
)
def """
                + f"{target_table}_scd2"
                + '''():
    """
    SCD Type 2 table for historical tracking.
    """
    return (
        dlt.read_stream("'''
                + f"{target_table}_silver"
                + """")
            .select(
                "*",
                F.current_timestamp().alias("effective_start_date"),
                F.lit(None).cast("timestamp").alias("effective_end_date"),
                F.lit(True).alias("is_current")
            )
    )
"""
            )

        return code

    def _generate_pipeline_documentation(
        self,
        pipeline_name: str,
        dlt_pipeline: Dict[str, Any],
        connector_type: str,
        latency_mode: str,
    ) -> str:
        """Generate comprehensive pipeline documentation."""
        doc = f"""# Lakeflow Pipeline Design: {pipeline_name}

**Work Item ID:** {self.work_item_id}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Connector Type:** {connector_type}
**Latency Mode:** {latency_mode}

---

## Pipeline Overview

**Pipeline Name:** {pipeline_name}
**Catalog:** {dlt_pipeline.get('catalog', 'N/A')}
**Schema:** {dlt_pipeline.get('target', 'N/A')}
**Continuous:** {dlt_pipeline.get('continuous', False)}
**Photon Enabled:** {dlt_pipeline.get('photon', True)}

---

## Architecture

```
{connector_type.upper()} Source
    ↓
Bronze Layer (Raw Ingestion)
    ↓
Silver Layer (Cleansed & Validated)
    ↓
Gold Layer (Business Ready)
```

### Data Flow

1. **Bronze Layer**: Raw data ingestion from {connector_type} source
   - Preserves original data format
   - Adds ingestion metadata
   - No data quality checks

2. **Silver Layer**: Cleansed and validated data
   - JSON parsing and schema enforcement
   - Data quality expectations
   - Dropped invalid records

3. **Gold Layer**: Business-ready aggregated data
   - Business logic transformations
   - Aggregations and enrichments
   - Ready for analytics and BI

---

## Connector Configuration

**Connector Type:** {connector_type.upper()}

"""

        # Add connector-specific details
        if connector_type == "kafka":
            doc += """**Kafka Configuration:**
- Bootstrap servers for cluster connection
- Topic subscription for data ingestion
- Starting offsets (latest or earliest)
- Optional security configuration (SASL, SSL)

**Benefits:**
- Real-time event streaming
- High throughput
- Fault-tolerant and scalable
"""
        elif connector_type == "kinesis":
            doc += """**Kinesis Configuration:**
- Stream name for data source
- AWS region for stream location
- Starting position (latest or trim_horizon)
- Optional AWS credentials

**Benefits:**
- Real-time data streaming
- Automatic scaling
- AWS native integration
"""
        elif connector_type == "eventhub":
            doc += """**Event Hub Configuration:**
- Connection string for authentication
- Consumer group for parallel processing
- Starting position configuration

**Benefits:**
- Azure-native event streaming
- Seamless Azure integration
- Enterprise-grade reliability
"""
        elif connector_type == "autoloader":
            doc += """**Auto Loader Configuration:**
- Cloud storage path (S3, ADLS, GCS)
- File format (json, csv, parquet, etc.)
- Schema inference and evolution
- Checkpoint management

**Benefits:**
- Automatically processes new files
- Schema evolution support
- Exactly-once processing guarantee
- Cost-effective batch streaming
"""

        doc += f"""
---

## Performance Optimization

**Latency Mode:** {latency_mode}

### Optimizations Applied

✅ **Photon Runtime** - 2-3x performance boost
✅ **Auto Compaction** - Automatic small file compaction
✅ **Optimize Write** - Optimized file sizes during writes
✅ **Adaptive Query Execution** - Dynamic query optimization
✅ **Enhanced Autoscaling** - Intelligent cluster scaling

### Configuration

```json
{{
  "spark.sql.shuffle.partitions": "{dlt_pipeline['configuration'].get('spark.sql.shuffle.partitions', '200')}",
  "pipelines.trigger.interval": "{dlt_pipeline['configuration'].get('pipelines.trigger.interval', '30 seconds')}",
  "spark.databricks.delta.optimizeWrite.enabled": "true",
  "spark.databricks.delta.autoCompact.enabled": "true"
}}
```

---

## Cluster Configuration

**Autoscaling:**
- Min workers: 1
- Max workers: 5
- Mode: Enhanced

**Features:**
- Single-node mode for development
- Automatic scale-up for high load
- Automatic scale-down for cost savings

---

## Data Quality

### Expectations

The pipeline includes data quality checks:

```python
@dlt.expect_or_drop("valid_event", "event_value IS NOT NULL")
```

**Quality Expectations:**
- Non-null event values
- Valid JSON structure
- Schema conformance

**Actions on Violation:**
- Drop invalid records
- Log violations
- Monitor data quality metrics

---

## Deployment

### Create Pipeline

```bash
# Create DLT pipeline
databricks pipelines create --json-file lakeflow-{pipeline_name.lower().replace(' ', '-')}-pipeline.json

# Start pipeline
databricks pipelines start --pipeline-id <pipeline-id>

# Monitor pipeline
databricks pipelines get --pipeline-id <pipeline-id>
```

### Deploy Notebook

```bash
# Upload notebook to Databricks workspace
databricks workspace import lakeflow-{pipeline_name.lower().replace(' ', '-')}-notebook.py \\
  /Workspace/dlt/{pipeline_name.lower().replace(' ', '_')} \\
  --language PYTHON --format SOURCE
```

---

## Monitoring

### Key Metrics

- **Ingestion Rate**: Events/second from source
- **Latency**: End-to-end processing time
- **Data Quality**: % records passing expectations
- **Cluster Utilization**: CPU, memory, disk usage
- **Cost**: DBU consumption and storage

### Dashboards

Access pipeline metrics in Databricks:
- Delta Live Tables UI
- System metrics
- Data quality metrics
- Lineage view

---

## Best Practices Applied

✅ **Bronze-Silver-Gold Architecture** - Industry-standard medallion architecture
✅ **Streaming Ingestion** - Real-time data processing
✅ **Data Quality Checks** - Automatic validation and cleansing
✅ **Auto Compaction** - Optimized file sizes
✅ **Schema Evolution** - Handles schema changes gracefully
✅ **Checkpoint Management** - Exactly-once processing guarantee

---

**Generated by:** AI-SDLC Lakeflow Connector Agent
"""

        return doc
