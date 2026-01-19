"""
Unit tests for Lakeflow Connector functionality.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from ai_sdlc.agents.lakeflow_connector_agent import LakeflowConnectorAgent


@pytest.mark.unit
class TestLakeflowConnectorAgent:
    """Test suite for LakeflowConnectorAgent."""

    @pytest.fixture
    def agent(self, temp_dir):
        """Create Lakeflow connector agent."""
        return LakeflowConnectorAgent(work_item_id="12345", evidence_base_path=temp_dir)

    @pytest.fixture
    def kafka_config(self):
        """Sample Kafka connector configuration."""
        return {
            "kafka.bootstrap.servers": "localhost:9092",
            "subscribe": "events",
            "startingOffsets": "latest",
        }

    @pytest.fixture
    def kinesis_config(self):
        """Sample Kinesis connector configuration."""
        return {
            "streamName": "my-stream",
            "region": "us-east-1",
            "startingPosition": "latest",
        }

    @pytest.fixture
    def eventhub_config(self):
        """Sample Event Hub connector configuration."""
        return {
            "eventhubs.connectionString": "Endpoint=sb://test.servicebus.windows.net/;",
            "eventhubs.consumerGroup": "$Default",
        }

    @pytest.fixture
    def autoloader_config(self):
        """Sample Auto Loader connector configuration."""
        return {
            "cloudFiles.format": "json",
            "path": "s3://bucket/data/",
            "cloudFiles.schemaLocation": "/tmp/schema",
        }

    def test_execute_kafka_success(self, agent, kafka_config):
        """Test successful Kafka pipeline execution."""
        result = agent.execute(
            {
                "pipeline_name": "Kafka Events Pipeline",
                "connector_type": "kafka",
                "connector_config": kafka_config,
                "target_table": "events",
                "target_catalog": "main",
                "target_schema": "bronze",
                "latency_mode": "low_latency",
            }
        )

        assert result["success"] is True
        assert result["data"]["pipeline_name"] == "Kafka Events Pipeline"
        assert result["data"]["connector_type"] == "kafka"
        assert result["data"]["target_table"] == "main.bronze.events"
        assert result["data"]["latency_mode"] == "low_latency"

    def test_execute_kinesis_success(self, agent, kinesis_config):
        """Test successful Kinesis pipeline execution."""
        result = agent.execute(
            {
                "pipeline_name": "Kinesis Stream Pipeline",
                "connector_type": "kinesis",
                "connector_config": kinesis_config,
                "target_table": "stream_data",
                "latency_mode": "balanced",
            }
        )

        assert result["success"] is True
        assert result["data"]["connector_type"] == "kinesis"
        assert result["data"]["latency_mode"] == "balanced"

    def test_execute_eventhub_success(self, agent, eventhub_config):
        """Test successful Event Hub pipeline execution."""
        result = agent.execute(
            {
                "pipeline_name": "Azure Events Pipeline",
                "connector_type": "eventhub",
                "connector_config": eventhub_config,
                "target_table": "azure_events",
                "latency_mode": "high_throughput",
            }
        )

        assert result["success"] is True
        assert result["data"]["connector_type"] == "eventhub"
        assert result["data"]["latency_mode"] == "high_throughput"

    def test_execute_autoloader_success(self, agent, autoloader_config):
        """Test successful Auto Loader pipeline execution."""
        result = agent.execute(
            {
                "pipeline_name": "File Ingestion Pipeline",
                "connector_type": "autoloader",
                "connector_config": autoloader_config,
                "target_table": "file_data",
            }
        )

        assert result["success"] is True
        assert result["data"]["connector_type"] == "autoloader"

    def test_execute_with_no_pipeline_name(self, agent, kafka_config):
        """Test execution with no pipeline name."""
        result = agent.execute(
            {
                "connector_type": "kafka",
                "connector_config": kafka_config,
                "target_table": "events",
            }
        )

        assert result["success"] is False
        assert "Pipeline name is required" in result["error_message"]

    def test_execute_with_no_connector_type(self, agent, kafka_config):
        """Test execution with no connector type."""
        result = agent.execute(
            {"pipeline_name": "Test Pipeline", "target_table": "events"}
        )

        assert result["success"] is False
        assert "Connector type is required" in result["error_message"]

    def test_execute_with_invalid_connector_type(self, agent):
        """Test execution with invalid connector type."""
        result = agent.execute(
            {
                "pipeline_name": "Test Pipeline",
                "connector_type": "invalid",
                "target_table": "events",
            }
        )

        assert result["success"] is False
        assert "Invalid connector type" in result["error_message"]

    def test_execute_with_no_target_table(self, agent, kafka_config):
        """Test execution with no target table."""
        result = agent.execute(
            {
                "pipeline_name": "Test Pipeline",
                "connector_type": "kafka",
                "connector_config": kafka_config,
            }
        )

        assert result["success"] is False
        assert "Target table name is required" in result["error_message"]

    def test_validate_connector_config_kafka_success(self, agent, kafka_config):
        """Test validation of valid Kafka configuration."""
        validation = agent._validate_connector_config("kafka", kafka_config)

        assert validation["valid"] is True
        assert len(validation["errors"]) == 0

    def test_validate_connector_config_kafka_missing_params(self, agent):
        """Test validation of Kafka configuration with missing parameters."""
        config = {"kafka.bootstrap.servers": "localhost:9092"}  # Missing 'subscribe'

        validation = agent._validate_connector_config("kafka", config)

        assert validation["valid"] is False
        assert any(
            "Missing required parameter: subscribe" in e for e in validation["errors"]
        )

    def test_validate_connector_config_kinesis_missing_params(self, agent):
        """Test validation of Kinesis configuration with missing parameters."""
        config = {"streamName": "my-stream"}  # Missing 'region'

        validation = agent._validate_connector_config("kinesis", config)

        assert validation["valid"] is False
        assert any(
            "Missing required parameter: region" in e for e in validation["errors"]
        )

    def test_generate_dlt_pipeline_low_latency(self, agent, kafka_config):
        """Test DLT pipeline generation with low latency mode."""
        pipeline = agent._generate_dlt_pipeline(
            pipeline_name="Test Pipeline",
            connector_type="kafka",
            connector_config=kafka_config,
            target_table="events",
            target_catalog="main",
            target_schema="bronze",
            latency_mode="low_latency",
            enable_cdc=False,
            enable_scd2=False,
            checkpoint_location=None,
        )

        assert pipeline["name"] == "Test Pipeline"
        assert pipeline["catalog"] == "main"
        assert pipeline["target"] == "bronze"
        assert pipeline["continuous"] is True
        assert pipeline["photon"] is True

    def test_generate_dlt_pipeline_balanced(self, agent, kafka_config):
        """Test DLT pipeline generation with balanced mode."""
        pipeline = agent._generate_dlt_pipeline(
            pipeline_name="Test Pipeline",
            connector_type="kafka",
            connector_config=kafka_config,
            target_table="events",
            target_catalog="main",
            target_schema="default",
            latency_mode="balanced",
            enable_cdc=False,
            enable_scd2=False,
            checkpoint_location=None,
        )

        assert pipeline["continuous"] is False
        assert "spark.sql.shuffle.partitions" in pipeline["configuration"]

    def test_generate_dlt_pipeline_with_cdc(self, agent, kafka_config):
        """Test DLT pipeline generation with CDC enabled."""
        pipeline = agent._generate_dlt_pipeline(
            pipeline_name="Test Pipeline",
            connector_type="kafka",
            connector_config=kafka_config,
            target_table="events",
            target_catalog="main",
            target_schema="default",
            latency_mode="balanced",
            enable_cdc=True,
            enable_scd2=False,
            checkpoint_location=None,
        )

        assert "pipelines.enableTrackHistory" in pipeline["configuration"]
        assert "pipelines.cdc.enabled" in pipeline["configuration"]

    def test_generate_dlt_pipeline_with_checkpoint(self, agent, kafka_config):
        """Test DLT pipeline generation with checkpoint location."""
        pipeline = agent._generate_dlt_pipeline(
            pipeline_name="Test Pipeline",
            connector_type="kafka",
            connector_config=kafka_config,
            target_table="events",
            target_catalog="main",
            target_schema="default",
            latency_mode="balanced",
            enable_cdc=False,
            enable_scd2=False,
            checkpoint_location="dbfs:/checkpoints/pipeline",
        )

        assert "storage" in pipeline
        assert pipeline["storage"] == "dbfs:/checkpoints/pipeline"

    def test_generate_dlt_notebook_kafka(self, agent, kafka_config):
        """Test DLT notebook generation for Kafka."""
        notebook = agent._generate_dlt_notebook(
            pipeline_name="Test Pipeline",
            connector_type="kafka",
            connector_config=kafka_config,
            target_table="events",
            target_catalog="main",
            target_schema="bronze",
            enable_cdc=False,
            enable_scd2=False,
        )

        assert "# Databricks notebook source" in notebook
        assert "import dlt" in notebook
        assert "@dlt.table" in notebook
        assert "events_bronze" in notebook
        assert "events_silver" in notebook
        assert "events" in notebook  # Gold table
        assert ".readStream" in notebook
        assert '.format("kafka")' in notebook

    def test_generate_dlt_notebook_kinesis(self, agent, kinesis_config):
        """Test DLT notebook generation for Kinesis."""
        notebook = agent._generate_dlt_notebook(
            pipeline_name="Test Pipeline",
            connector_type="kinesis",
            connector_config=kinesis_config,
            target_table="stream_data",
            target_catalog="main",
            target_schema="default",
            enable_cdc=False,
            enable_scd2=False,
        )

        assert '.format("kinesis")' in notebook
        assert "streamName" in notebook
        assert "region" in notebook

    def test_generate_dlt_notebook_eventhub(self, agent, eventhub_config):
        """Test DLT notebook generation for Event Hub."""
        notebook = agent._generate_dlt_notebook(
            pipeline_name="Test Pipeline",
            connector_type="eventhub",
            connector_config=eventhub_config,
            target_table="azure_events",
            target_catalog="main",
            target_schema="default",
            enable_cdc=False,
            enable_scd2=False,
        )

        assert '.format("eventhubs")' in notebook
        assert "eventhubs.connectionString" in notebook

    def test_generate_dlt_notebook_autoloader(self, agent, autoloader_config):
        """Test DLT notebook generation for Auto Loader."""
        notebook = agent._generate_dlt_notebook(
            pipeline_name="Test Pipeline",
            connector_type="autoloader",
            connector_config=autoloader_config,
            target_table="file_data",
            target_catalog="main",
            target_schema="default",
            enable_cdc=False,
            enable_scd2=False,
        )

        assert '.format("cloudFiles")' in notebook
        assert "cloudFiles.format" in notebook

    def test_generate_dlt_notebook_with_cdc(self, agent, kafka_config):
        """Test DLT notebook generation with CDC."""
        notebook = agent._generate_dlt_notebook(
            pipeline_name="Test Pipeline",
            connector_type="kafka",
            connector_config=kafka_config,
            target_table="events",
            target_catalog="main",
            target_schema="bronze",
            enable_cdc=True,
            enable_scd2=False,
        )

        assert "events_cdc" in notebook
        assert "CDC (Change Data Capture)" in notebook
        assert '"operation"' in notebook

    def test_generate_dlt_notebook_with_scd2(self, agent, kafka_config):
        """Test DLT notebook generation with SCD Type 2."""
        notebook = agent._generate_dlt_notebook(
            pipeline_name="Test Pipeline",
            connector_type="kafka",
            connector_config=kafka_config,
            target_table="events",
            target_catalog="main",
            target_schema="bronze",
            enable_cdc=False,
            enable_scd2=True,
        )

        assert "events_scd2" in notebook
        assert "Slowly Changing Dimension" in notebook
        assert "effective_start_date" in notebook
        assert "effective_end_date" in notebook
        assert "is_current" in notebook

    def test_pipeline_config_file_creation(self, agent, kafka_config):
        """Test pipeline configuration file creation."""
        result = agent.execute(
            {
                "pipeline_name": "Test Pipeline",
                "connector_type": "kafka",
                "connector_config": kafka_config,
                "target_table": "events",
            }
        )

        assert result["success"] is True
        config_file = Path(result["data"]["pipeline_config_file"])
        assert config_file.exists()

        # Read and verify configuration
        with open(config_file, "r") as f:
            config = json.load(f)

        assert config["name"] == "Test Pipeline"
        assert config["photon"] is True

    def test_notebook_file_creation(self, agent, kafka_config):
        """Test DLT notebook file creation."""
        result = agent.execute(
            {
                "pipeline_name": "Test Pipeline",
                "connector_type": "kafka",
                "connector_config": kafka_config,
                "target_table": "events",
            }
        )

        assert result["success"] is True
        notebook_file = Path(result["data"]["notebook_file"])
        assert notebook_file.exists()

        # Read and verify notebook
        with open(notebook_file, "r") as f:
            notebook_code = f.read()

        assert "import dlt" in notebook_code
        assert "@dlt.table" in notebook_code

    def test_documentation_file_creation(self, agent, kafka_config):
        """Test documentation file creation."""
        result = agent.execute(
            {
                "pipeline_name": "Test Pipeline",
                "connector_type": "kafka",
                "connector_config": kafka_config,
                "target_table": "events",
            }
        )

        assert result["success"] is True
        doc_file = Path(result["data"]["doc_file"])
        assert doc_file.exists()

        # Read and verify documentation
        with open(doc_file, "r") as f:
            doc_content = f.read()

        assert "Test Pipeline" in doc_content
        assert "kafka" in doc_content.lower()
        assert "Bronze Layer" in doc_content
        assert "Silver Layer" in doc_content
        assert "Gold Layer" in doc_content

    def test_latency_mode_presets(self, agent, kafka_config):
        """Test all latency mode presets."""
        for mode in ["low_latency", "balanced", "high_throughput"]:
            result = agent.execute(
                {
                    "pipeline_name": f"{mode} Pipeline",
                    "connector_type": "kafka",
                    "connector_config": kafka_config,
                    "target_table": "events",
                    "latency_mode": mode,
                }
            )

            assert result["success"] is True
            assert result["data"]["latency_mode"] == mode

    def test_pipeline_with_all_options(self, agent, kafka_config):
        """Test pipeline with all options enabled."""
        result = agent.execute(
            {
                "pipeline_name": "Full Featured Pipeline",
                "connector_type": "kafka",
                "connector_config": kafka_config,
                "target_table": "events",
                "target_catalog": "prod",
                "target_schema": "streaming",
                "latency_mode": "low_latency",
                "enable_cdc": True,
                "enable_scd2": True,
                "checkpoint_location": "dbfs:/checkpoints/full_pipeline",
            }
        )

        assert result["success"] is True
        assert result["data"]["enable_cdc"] is True
        assert result["data"]["enable_scd2"] is True
        assert result["data"]["target_table"] == "prod.streaming.events"

        # Verify notebook has both CDC and SCD2
        notebook_file = Path(result["data"]["notebook_file"])
        with open(notebook_file, "r") as f:
            notebook = f.read()

        assert "events_cdc" in notebook
        assert "events_scd2" in notebook


@pytest.mark.integration
class TestLakeflowConnectorIntegration:
    """Integration tests for Lakeflow connector workflow."""

    def test_full_kafka_pipeline_workflow(self, temp_dir):
        """Test complete Kafka pipeline design workflow."""
        # Create agent
        agent = LakeflowConnectorAgent(
            work_item_id="integration_test", evidence_base_path=temp_dir
        )

        # Design pipeline
        result = agent.execute(
            {
                "pipeline_name": "Production Events Pipeline",
                "connector_type": "kafka",
                "connector_config": {
                    "kafka.bootstrap.servers": "prod-kafka:9092",
                    "subscribe": "production.events",
                    "startingOffsets": "earliest",
                },
                "target_table": "events",
                "target_catalog": "prod",
                "target_schema": "streaming",
                "latency_mode": "low_latency",
                "enable_cdc": True,
                "checkpoint_location": "dbfs:/checkpoints/prod_events",
            }
        )

        # Verify result
        assert result["success"] is True

        # Verify all files created
        pipeline_config_file = Path(result["data"]["pipeline_config_file"])
        notebook_file = Path(result["data"]["notebook_file"])
        doc_file = Path(result["data"]["doc_file"])

        assert pipeline_config_file.exists()
        assert notebook_file.exists()
        assert doc_file.exists()

        # Verify pipeline configuration
        with open(pipeline_config_file, "r") as f:
            config = json.load(f)

        assert config["name"] == "Production Events Pipeline"
        assert config["continuous"] is True
        assert config["photon"] is True

        # Verify notebook
        with open(notebook_file, "r") as f:
            notebook = f.read()

        assert "import dlt" in notebook
        assert "events_bronze" in notebook
        assert "events_silver" in notebook
        assert "events_cdc" in notebook
