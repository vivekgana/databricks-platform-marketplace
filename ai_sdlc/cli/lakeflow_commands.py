"""
CLI commands for Lakeflow connector and pipeline design.

Usage:
    python -m ai_sdlc.cli.lakeflow_commands design-kafka --pipeline-name "Events Pipeline" --brokers "localhost:9092" --topic "events"
    python -m ai_sdlc.cli.lakeflow_commands design-kinesis --pipeline-name "Stream Pipeline" --stream "my-stream" --region "us-east-1"
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from ai_sdlc.agents.lakeflow_connector_agent import LakeflowConnectorAgent


def design_kafka_pipeline(
    pipeline_name: str,
    bootstrap_servers: str,
    topic: str,
    target_table: str,
    target_catalog: str = "main",
    target_schema: str = "default",
    latency_mode: str = "balanced",
    enable_cdc: bool = False,
    enable_scd2: bool = False,
    checkpoint_location: Optional[str] = None,
    work_item_id: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> int:
    """Design Kafka-based Lakeflow pipeline."""
    connector_config = {
        "kafka.bootstrap.servers": bootstrap_servers,
        "subscribe": topic,
        "startingOffsets": "latest",
    }

    return design_pipeline(
        pipeline_name=pipeline_name,
        connector_type="kafka",
        connector_config=connector_config,
        target_table=target_table,
        target_catalog=target_catalog,
        target_schema=target_schema,
        latency_mode=latency_mode,
        enable_cdc=enable_cdc,
        enable_scd2=enable_scd2,
        checkpoint_location=checkpoint_location,
        work_item_id=work_item_id,
        output_dir=output_dir,
    )


def design_kinesis_pipeline(
    pipeline_name: str,
    stream_name: str,
    region: str,
    target_table: str,
    target_catalog: str = "main",
    target_schema: str = "default",
    latency_mode: str = "balanced",
    enable_cdc: bool = False,
    enable_scd2: bool = False,
    checkpoint_location: Optional[str] = None,
    work_item_id: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> int:
    """Design Kinesis-based Lakeflow pipeline."""
    connector_config = {
        "streamName": stream_name,
        "region": region,
        "startingPosition": "latest",
    }

    return design_pipeline(
        pipeline_name=pipeline_name,
        connector_type="kinesis",
        connector_config=connector_config,
        target_table=target_table,
        target_catalog=target_catalog,
        target_schema=target_schema,
        latency_mode=latency_mode,
        enable_cdc=enable_cdc,
        enable_scd2=enable_scd2,
        checkpoint_location=checkpoint_location,
        work_item_id=work_item_id,
        output_dir=output_dir,
    )


def design_eventhub_pipeline(
    pipeline_name: str,
    connection_string: str,
    target_table: str,
    consumer_group: str = "$Default",
    target_catalog: str = "main",
    target_schema: str = "default",
    latency_mode: str = "balanced",
    enable_cdc: bool = False,
    enable_scd2: bool = False,
    checkpoint_location: Optional[str] = None,
    work_item_id: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> int:
    """Design Event Hub-based Lakeflow pipeline."""
    connector_config = {
        "eventhubs.connectionString": connection_string,
        "eventhubs.consumerGroup": consumer_group,
    }

    return design_pipeline(
        pipeline_name=pipeline_name,
        connector_type="eventhub",
        connector_config=connector_config,
        target_table=target_table,
        target_catalog=target_catalog,
        target_schema=target_schema,
        latency_mode=latency_mode,
        enable_cdc=enable_cdc,
        enable_scd2=enable_scd2,
        checkpoint_location=checkpoint_location,
        work_item_id=work_item_id,
        output_dir=output_dir,
    )


def design_autoloader_pipeline(
    pipeline_name: str,
    source_path: str,
    file_format: str,
    target_table: str,
    schema_location: Optional[str] = None,
    target_catalog: str = "main",
    target_schema: str = "default",
    latency_mode: str = "balanced",
    enable_cdc: bool = False,
    enable_scd2: bool = False,
    checkpoint_location: Optional[str] = None,
    work_item_id: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> int:
    """Design Auto Loader-based Lakeflow pipeline."""
    connector_config = {
        "cloudFiles.format": file_format,
        "path": source_path,
    }

    if schema_location:
        connector_config["cloudFiles.schemaLocation"] = schema_location

    return design_pipeline(
        pipeline_name=pipeline_name,
        connector_type="autoloader",
        connector_config=connector_config,
        target_table=target_table,
        target_catalog=target_catalog,
        target_schema=target_schema,
        latency_mode=latency_mode,
        enable_cdc=enable_cdc,
        enable_scd2=enable_scd2,
        checkpoint_location=checkpoint_location,
        work_item_id=work_item_id,
        output_dir=output_dir,
    )


def design_pipeline(
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
    work_item_id: Optional[str],
    output_dir: Optional[str],
) -> int:
    """Common pipeline design logic."""
    # Initialize agent
    agent = LakeflowConnectorAgent(
        work_item_id=work_item_id or "local",
        evidence_base_path=output_dir or "./lakeflow-designs",
    )

    # Design pipeline
    print(f"🔧 Designing Lakeflow pipeline: {pipeline_name}")
    print(f"   Connector type: {connector_type}")
    print(f"   Target table: {target_catalog}.{target_schema}.{target_table}")
    print(f"   Latency mode: {latency_mode}")
    if enable_cdc:
        print("   CDC: Enabled")
    if enable_scd2:
        print("   SCD Type 2: Enabled")
    print()

    result = agent.execute(
        {
            "pipeline_name": pipeline_name,
            "connector_type": connector_type,
            "connector_config": connector_config,
            "target_table": target_table,
            "target_catalog": target_catalog,
            "target_schema": target_schema,
            "latency_mode": latency_mode,
            "enable_cdc": enable_cdc,
            "enable_scd2": enable_scd2,
            "checkpoint_location": checkpoint_location,
        }
    )

    if not result["success"]:
        print(f"❌ Pipeline design failed: {result.get('error_message')}")
        return 1

    data = result["data"]

    # Print summary
    print("=" * 70)
    print(f"📊 Lakeflow Pipeline Summary")
    print("=" * 70)
    print()
    print(f"Pipeline name:      {data['pipeline_name']}")
    print(f"Connector type:     {data['connector_type']}")
    print(f"Target table:       {data['target_table']}")
    print(f"Latency mode:       {data['latency_mode']}")
    print(f"CDC enabled:        {data['enable_cdc']}")
    print(f"SCD2 enabled:       {data['enable_scd2']}")
    print()

    # Print output files
    print(f"📄 Pipeline config:  {data['pipeline_config_file']}")
    print(f"📄 DLT notebook:     {data['notebook_file']}")
    print(f"📄 Documentation:    {data['doc_file']}")
    print()

    # Print next steps
    print("Next steps:")
    print("1. Review the generated DLT notebook")
    print("2. Customize the pipeline configuration if needed")
    print("3. Deploy the notebook:")
    print(
        f"   databricks workspace import {data['notebook_file']} /Workspace/dlt/{pipeline_name.lower().replace(' ', '_')} --language PYTHON"
    )
    print("4. Create the DLT pipeline:")
    print(f"   databricks pipelines create --json-file {data['pipeline_config_file']}")
    print()

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lakeflow Connector and Pipeline Design CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Design Kafka pipeline
  python -m ai_sdlc.cli.lakeflow_commands design-kafka \\
    --pipeline-name "Events Pipeline" \\
    --brokers "localhost:9092" \\
    --topic "events" \\
    --target-table "events" \\
    --latency-mode low_latency

  # Design Kinesis pipeline with CDC
  python -m ai_sdlc.cli.lakeflow_commands design-kinesis \\
    --pipeline-name "Stream Pipeline" \\
    --stream "my-stream" \\
    --region "us-east-1" \\
    --target-table "stream_data" \\
    --enable-cdc

  # Design Event Hub pipeline
  python -m ai_sdlc.cli.lakeflow_commands design-eventhub \\
    --pipeline-name "Azure Events" \\
    --connection-string "Endpoint=..." \\
    --target-table "azure_events"

  # Design Auto Loader pipeline
  python -m ai_sdlc.cli.lakeflow_commands design-autoloader \\
    --pipeline-name "File Ingestion" \\
    --source-path "s3://bucket/data/" \\
    --file-format "json" \\
    --target-table "file_data"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Kafka pipeline
    kafka_parser = subparsers.add_parser(
        "design-kafka", help="Design Kafka-based pipeline"
    )
    kafka_parser.add_argument("--pipeline-name", required=True, help="Pipeline name")
    kafka_parser.add_argument(
        "--brokers", required=True, help="Kafka bootstrap servers"
    )
    kafka_parser.add_argument("--topic", required=True, help="Kafka topic to subscribe")
    kafka_parser.add_argument("--target-table", required=True, help="Target table name")
    kafka_parser.add_argument(
        "--target-catalog", default="main", help="Target catalog (default: main)"
    )
    kafka_parser.add_argument(
        "--target-schema", default="default", help="Target schema (default: default)"
    )
    kafka_parser.add_argument(
        "--latency-mode",
        choices=["low_latency", "balanced", "high_throughput"],
        default="balanced",
        help="Latency optimization mode (default: balanced)",
    )
    kafka_parser.add_argument(
        "--enable-cdc", action="store_true", help="Enable Change Data Capture"
    )
    kafka_parser.add_argument(
        "--enable-scd2",
        action="store_true",
        help="Enable Slowly Changing Dimension Type 2",
    )
    kafka_parser.add_argument(
        "--checkpoint-location", help="Checkpoint storage location"
    )
    kafka_parser.add_argument("--work-item-id", help="Work item ID (optional)")
    kafka_parser.add_argument(
        "--output-dir",
        help="Output directory (default: ./lakeflow-designs)",
    )

    # Kinesis pipeline
    kinesis_parser = subparsers.add_parser(
        "design-kinesis", help="Design Kinesis-based pipeline"
    )
    kinesis_parser.add_argument("--pipeline-name", required=True, help="Pipeline name")
    kinesis_parser.add_argument("--stream", required=True, help="Kinesis stream name")
    kinesis_parser.add_argument("--region", required=True, help="AWS region")
    kinesis_parser.add_argument(
        "--target-table", required=True, help="Target table name"
    )
    kinesis_parser.add_argument(
        "--target-catalog", default="main", help="Target catalog (default: main)"
    )
    kinesis_parser.add_argument(
        "--target-schema", default="default", help="Target schema (default: default)"
    )
    kinesis_parser.add_argument(
        "--latency-mode",
        choices=["low_latency", "balanced", "high_throughput"],
        default="balanced",
        help="Latency optimization mode (default: balanced)",
    )
    kinesis_parser.add_argument(
        "--enable-cdc", action="store_true", help="Enable Change Data Capture"
    )
    kinesis_parser.add_argument(
        "--enable-scd2",
        action="store_true",
        help="Enable Slowly Changing Dimension Type 2",
    )
    kinesis_parser.add_argument(
        "--checkpoint-location", help="Checkpoint storage location"
    )
    kinesis_parser.add_argument("--work-item-id", help="Work item ID (optional)")
    kinesis_parser.add_argument(
        "--output-dir",
        help="Output directory (default: ./lakeflow-designs)",
    )

    # Event Hub pipeline
    eventhub_parser = subparsers.add_parser(
        "design-eventhub", help="Design Event Hub-based pipeline"
    )
    eventhub_parser.add_argument("--pipeline-name", required=True, help="Pipeline name")
    eventhub_parser.add_argument(
        "--connection-string", required=True, help="Event Hub connection string"
    )
    eventhub_parser.add_argument(
        "--consumer-group",
        default="$Default",
        help="Consumer group (default: $Default)",
    )
    eventhub_parser.add_argument(
        "--target-table", required=True, help="Target table name"
    )
    eventhub_parser.add_argument(
        "--target-catalog", default="main", help="Target catalog (default: main)"
    )
    eventhub_parser.add_argument(
        "--target-schema", default="default", help="Target schema (default: default)"
    )
    eventhub_parser.add_argument(
        "--latency-mode",
        choices=["low_latency", "balanced", "high_throughput"],
        default="balanced",
        help="Latency optimization mode (default: balanced)",
    )
    eventhub_parser.add_argument(
        "--enable-cdc", action="store_true", help="Enable Change Data Capture"
    )
    eventhub_parser.add_argument(
        "--enable-scd2",
        action="store_true",
        help="Enable Slowly Changing Dimension Type 2",
    )
    eventhub_parser.add_argument(
        "--checkpoint-location", help="Checkpoint storage location"
    )
    eventhub_parser.add_argument("--work-item-id", help="Work item ID (optional)")
    eventhub_parser.add_argument(
        "--output-dir",
        help="Output directory (default: ./lakeflow-designs)",
    )

    # Auto Loader pipeline
    autoloader_parser = subparsers.add_parser(
        "design-autoloader", help="Design Auto Loader-based pipeline"
    )
    autoloader_parser.add_argument(
        "--pipeline-name", required=True, help="Pipeline name"
    )
    autoloader_parser.add_argument(
        "--source-path", required=True, help="Source cloud storage path"
    )
    autoloader_parser.add_argument(
        "--file-format", required=True, help="File format (json, csv, parquet, etc.)"
    )
    autoloader_parser.add_argument(
        "--schema-location", help="Schema inference location"
    )
    autoloader_parser.add_argument(
        "--target-table", required=True, help="Target table name"
    )
    autoloader_parser.add_argument(
        "--target-catalog", default="main", help="Target catalog (default: main)"
    )
    autoloader_parser.add_argument(
        "--target-schema", default="default", help="Target schema (default: default)"
    )
    autoloader_parser.add_argument(
        "--latency-mode",
        choices=["low_latency", "balanced", "high_throughput"],
        default="balanced",
        help="Latency optimization mode (default: balanced)",
    )
    autoloader_parser.add_argument(
        "--enable-cdc", action="store_true", help="Enable Change Data Capture"
    )
    autoloader_parser.add_argument(
        "--enable-scd2",
        action="store_true",
        help="Enable Slowly Changing Dimension Type 2",
    )
    autoloader_parser.add_argument(
        "--checkpoint-location", help="Checkpoint storage location"
    )
    autoloader_parser.add_argument("--work-item-id", help="Work item ID (optional)")
    autoloader_parser.add_argument(
        "--output-dir",
        help="Output directory (default: ./lakeflow-designs)",
    )

    args = parser.parse_args()

    if args.command == "design-kafka":
        exit_code = design_kafka_pipeline(
            pipeline_name=args.pipeline_name,
            bootstrap_servers=args.brokers,
            topic=args.topic,
            target_table=args.target_table,
            target_catalog=args.target_catalog,
            target_schema=args.target_schema,
            latency_mode=args.latency_mode,
            enable_cdc=args.enable_cdc,
            enable_scd2=args.enable_scd2,
            checkpoint_location=args.checkpoint_location,
            work_item_id=args.work_item_id,
            output_dir=args.output_dir,
        )
    elif args.command == "design-kinesis":
        exit_code = design_kinesis_pipeline(
            pipeline_name=args.pipeline_name,
            stream_name=args.stream,
            region=args.region,
            target_table=args.target_table,
            target_catalog=args.target_catalog,
            target_schema=args.target_schema,
            latency_mode=args.latency_mode,
            enable_cdc=args.enable_cdc,
            enable_scd2=args.enable_scd2,
            checkpoint_location=args.checkpoint_location,
            work_item_id=args.work_item_id,
            output_dir=args.output_dir,
        )
    elif args.command == "design-eventhub":
        exit_code = design_eventhub_pipeline(
            pipeline_name=args.pipeline_name,
            connection_string=args.connection_string,
            consumer_group=args.consumer_group,
            target_table=args.target_table,
            target_catalog=args.target_catalog,
            target_schema=args.target_schema,
            latency_mode=args.latency_mode,
            enable_cdc=args.enable_cdc,
            enable_scd2=args.enable_scd2,
            checkpoint_location=args.checkpoint_location,
            work_item_id=args.work_item_id,
            output_dir=args.output_dir,
        )
    elif args.command == "design-autoloader":
        exit_code = design_autoloader_pipeline(
            pipeline_name=args.pipeline_name,
            source_path=args.source_path,
            file_format=args.file_format,
            schema_location=args.schema_location,
            target_table=args.target_table,
            target_catalog=args.target_catalog,
            target_schema=args.target_schema,
            latency_mode=args.latency_mode,
            enable_cdc=args.enable_cdc,
            enable_scd2=args.enable_scd2,
            checkpoint_location=args.checkpoint_location,
            work_item_id=args.work_item_id,
            output_dir=args.output_dir,
        )
    else:
        parser.print_help()
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
