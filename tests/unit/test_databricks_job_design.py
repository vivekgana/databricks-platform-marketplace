"""
Unit tests for Databricks Job Design functionality.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from ai_sdlc.agents.databricks_job_design_agent import DatabricksJobDesignAgent


@pytest.mark.unit
class TestDatabricksJobDesignAgent:
    """Test suite for DatabricksJobDesignAgent."""

    @pytest.fixture
    def agent(self, temp_dir):
        """Create job design agent."""
        return DatabricksJobDesignAgent(
            work_item_id="12345", evidence_base_path=temp_dir
        )

    @pytest.fixture
    def sample_tasks(self):
        """Sample task definitions."""
        return [
            {
                "task_name": "extract_data",
                "task_type": "notebook",
                "description": "Extract data from source",
                "notebook_path": "/Workspace/notebooks/extract",
                "parameters": {"source": "s3://bucket/data"},
                "max_retries": 2,
                "timeout_seconds": 3600,
            },
            {
                "task_name": "transform_data",
                "task_type": "notebook",
                "description": "Transform extracted data",
                "notebook_path": "/Workspace/notebooks/transform",
                "parameters": {"format": "parquet"},
                "depends_on": ["extract_data"],
                "max_retries": 2,
                "timeout_seconds": 3600,
            },
            {
                "task_name": "load_data",
                "task_type": "notebook",
                "description": "Load transformed data",
                "notebook_path": "/Workspace/notebooks/load",
                "parameters": {"target": "delta_table"},
                "depends_on": ["transform_data"],
                "max_retries": 1,
                "timeout_seconds": 1800,
            },
        ]

    def test_execute_success(self, agent, sample_tasks):
        """Test successful job design execution."""
        result = agent.execute(
            {
                "job_name": "ETL Pipeline",
                "job_description": "Daily ETL job",
                "tasks": sample_tasks,
                "cluster_size": "medium",
            }
        )

        assert result["success"] is True
        assert result["data"]["job_name"] == "ETL Pipeline"
        assert result["data"]["task_count"] == 3
        assert result["data"]["cluster_size"] == "medium"
        assert result["data"]["validation"]["valid"] is True

    def test_execute_with_no_job_name(self, agent, sample_tasks):
        """Test execution with no job name."""
        result = agent.execute({"tasks": sample_tasks})

        assert result["success"] is False
        assert "Job name is required" in result["error_message"]

    def test_execute_with_no_tasks(self, agent):
        """Test execution with no tasks."""
        result = agent.execute({"job_name": "Test Job", "tasks": []})

        assert result["success"] is False
        assert "At least one task is required" in result["error_message"]

    def test_execute_with_invalid_cluster_size(self, agent, sample_tasks):
        """Test execution with invalid cluster size."""
        result = agent.execute(
            {
                "job_name": "Test Job",
                "tasks": sample_tasks,
                "cluster_size": "invalid",
            }
        )

        assert result["success"] is False
        assert "Invalid cluster size" in result["error_message"]

    def test_generate_job_config_with_schedule(self, agent, sample_tasks):
        """Test job configuration generation with schedule."""
        result = agent.execute(
            {
                "job_name": "Scheduled Job",
                "job_description": "Runs daily at 2 AM",
                "tasks": sample_tasks,
                "cluster_size": "small",
                "schedule": {
                    "quartz_cron_expression": "0 0 2 * * ?",
                    "timezone_id": "America/New_York",
                    "pause_status": "UNPAUSED",
                },
            }
        )

        assert result["success"] is True
        job_config = result["data"]["job_config"]
        assert "schedule" in job_config
        assert job_config["schedule"]["quartz_cron_expression"] == "0 0 2 * * ?"
        assert result["data"]["has_schedule"] is True

    def test_generate_job_config_with_notifications(self, agent, sample_tasks):
        """Test job configuration generation with email notifications."""
        emails = ["user1@example.com", "user2@example.com"]
        result = agent.execute(
            {
                "job_name": "Notified Job",
                "tasks": sample_tasks,
                "cluster_size": "medium",
                "notification_emails": emails,
            }
        )

        assert result["success"] is True
        job_config = result["data"]["job_config"]
        assert "email_notifications" in job_config
        assert job_config["email_notifications"]["on_start"] == emails
        assert job_config["email_notifications"]["on_success"] == emails
        assert job_config["email_notifications"]["on_failure"] == emails

    def test_generate_task_config_notebook(self, agent):
        """Test notebook task configuration generation."""
        task_spec = {
            "task_name": "notebook_task",
            "task_type": "notebook",
            "notebook_path": "/Workspace/notebooks/test",
            "parameters": {"param1": "value1"},
            "max_retries": 3,
            "timeout_seconds": 7200,
        }

        task_config = agent._generate_task_config(task_spec, "medium", 0, [task_spec])

        assert task_config["task_key"] == "notebook_task"
        assert task_config["max_retries"] == 3
        assert task_config["timeout_seconds"] == 7200
        assert "notebook_task" in task_config
        assert (
            task_config["notebook_task"]["notebook_path"] == "/Workspace/notebooks/test"
        )
        assert task_config["notebook_task"]["base_parameters"] == {"param1": "value1"}

    def test_generate_task_config_python_wheel(self, agent):
        """Test Python wheel task configuration generation."""
        task_spec = {
            "task_name": "python_task",
            "task_type": "python",
            "package_name": "my_package",
            "entry_point": "main",
            "parameters": ["arg1", "arg2"],
        }

        task_config = agent._generate_task_config(task_spec, "small", 0, [task_spec])

        assert "python_wheel_task" in task_config
        assert task_config["python_wheel_task"]["package_name"] == "my_package"
        assert task_config["python_wheel_task"]["entry_point"] == "main"
        assert task_config["python_wheel_task"]["parameters"] == ["arg1", "arg2"]

    def test_generate_task_config_jar(self, agent):
        """Test Spark JAR task configuration generation."""
        task_spec = {
            "task_name": "jar_task",
            "task_type": "jar",
            "main_class_name": "com.example.Main",
            "parameters": ["param1", "param2"],
        }

        task_config = agent._generate_task_config(task_spec, "medium", 0, [task_spec])

        assert "spark_jar_task" in task_config
        assert task_config["spark_jar_task"]["main_class_name"] == "com.example.Main"
        assert task_config["spark_jar_task"]["parameters"] == ["param1", "param2"]

    def test_generate_task_config_sql(self, agent):
        """Test SQL task configuration generation."""
        task_spec = {
            "task_name": "sql_task",
            "task_type": "sql",
            "query_id": "query123",
            "warehouse_id": "warehouse456",
        }

        task_config = agent._generate_task_config(task_spec, "small", 0, [task_spec])

        assert "sql_task" in task_config
        assert task_config["sql_task"]["query"]["query_id"] == "query123"
        assert task_config["sql_task"]["warehouse_id"] == "warehouse456"

    def test_generate_task_config_dlt(self, agent):
        """Test DLT pipeline task configuration generation."""
        task_spec = {
            "task_name": "dlt_task",
            "task_type": "dlt",
            "pipeline_id": "pipeline789",
        }

        task_config = agent._generate_task_config(task_spec, "medium", 0, [task_spec])

        assert "pipeline_task" in task_config
        assert task_config["pipeline_task"]["pipeline_id"] == "pipeline789"

    def test_cluster_config_new_cluster(self, agent):
        """Test new cluster configuration."""
        task_spec = {"task_name": "test_task"}
        cluster_config = agent._get_cluster_config(task_spec, "large")

        assert "new_cluster" in cluster_config
        cluster = cluster_config["new_cluster"]
        assert cluster["node_type_id"] == "Standard_DS5_v2"
        assert "autoscale" in cluster
        assert cluster["autoscale"]["min_workers"] == 4
        assert cluster["autoscale"]["max_workers"] == 16
        assert cluster["runtime_engine"] == "PHOTON"
        assert "aws_attributes" in cluster
        assert cluster["aws_attributes"]["availability"] == "SPOT_WITH_FALLBACK"

    def test_cluster_config_existing_cluster(self, agent):
        """Test existing cluster configuration."""
        task_spec = {"task_name": "test_task", "existing_cluster_id": "cluster123"}
        cluster_config = agent._get_cluster_config(task_spec, "medium")

        assert "existing_cluster_id" in cluster_config
        assert cluster_config["existing_cluster_id"] == "cluster123"
        assert "new_cluster" not in cluster_config

    def test_cluster_config_with_custom_spark_conf(self, agent):
        """Test cluster configuration with custom Spark settings."""
        task_spec = {
            "task_name": "test_task",
            "spark_conf": {
                "spark.sql.shuffle.partitions": "200",
                "spark.executor.memory": "4g",
            },
        }
        cluster_config = agent._get_cluster_config(task_spec, "medium")

        cluster = cluster_config["new_cluster"]
        assert "spark_conf" in cluster
        assert cluster["spark_conf"]["spark.sql.shuffle.partitions"] == "200"
        assert cluster["spark_conf"]["spark.executor.memory"] == "4g"

    def test_validate_job_config_success(self, agent, sample_tasks):
        """Test validation of valid job configuration."""
        result = agent.execute(
            {
                "job_name": "Valid Job",
                "tasks": sample_tasks,
                "cluster_size": "medium",
            }
        )

        validation = result["data"]["validation"]
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0

    def test_validate_job_config_no_name(self, agent):
        """Test validation with missing job name."""
        job_config = {"tasks": [{"task_key": "task1", "notebook_task": {}}]}

        validation = agent._validate_job_config(job_config)

        assert validation["valid"] is False
        assert any("Job name is required" in e for e in validation["errors"])

    def test_validate_job_config_no_tasks(self, agent):
        """Test validation with no tasks."""
        job_config = {"name": "Test Job", "tasks": []}

        validation = agent._validate_job_config(job_config)

        assert validation["valid"] is False
        assert any("At least one task is required" in e for e in validation["errors"])

    def test_validate_job_config_duplicate_task_key(self, agent):
        """Test validation with duplicate task keys."""
        job_config = {
            "name": "Test Job",
            "tasks": [
                {
                    "task_key": "task1",
                    "notebook_task": {"notebook_path": "/test"},
                    "new_cluster": {},
                },
                {
                    "task_key": "task1",
                    "notebook_task": {"notebook_path": "/test2"},
                    "new_cluster": {},
                },
            ],
        }

        validation = agent._validate_job_config(job_config)

        assert validation["valid"] is False
        assert any("Duplicate task key" in e for e in validation["errors"])

    def test_validate_job_config_missing_task_type(self, agent):
        """Test validation with missing task type."""
        job_config = {
            "name": "Test Job",
            "tasks": [{"task_key": "task1", "new_cluster": {}}],
        }

        validation = agent._validate_job_config(job_config)

        assert validation["valid"] is False
        assert any(
            "must have a task type configuration" in e for e in validation["errors"]
        )

    def test_validate_job_config_missing_cluster(self, agent):
        """Test validation with missing cluster configuration."""
        job_config = {
            "name": "Test Job",
            "tasks": [
                {"task_key": "task1", "notebook_task": {"notebook_path": "/test"}}
            ],
        }

        validation = agent._validate_job_config(job_config)

        assert validation["valid"] is False
        assert any("must have cluster configuration" in e for e in validation["errors"])

    def test_has_circular_dependencies(self, agent):
        """Test circular dependency detection."""
        tasks = [
            {"task_key": "task1", "depends_on": [{"task_key": "task2"}]},
            {"task_key": "task2", "depends_on": [{"task_key": "task3"}]},
            {"task_key": "task3", "depends_on": [{"task_key": "task1"}]},
        ]

        has_cycle = agent._has_circular_dependencies(tasks)
        assert has_cycle is True

    def test_no_circular_dependencies(self, agent, sample_tasks):
        """Test valid dependency chain."""
        # Convert sample_tasks to task config format
        tasks = [
            {"task_key": "extract_data", "depends_on": []},
            {
                "task_key": "transform_data",
                "depends_on": [{"task_key": "extract_data"}],
            },
            {"task_key": "load_data", "depends_on": [{"task_key": "transform_data"}]},
        ]

        has_cycle = agent._has_circular_dependencies(tasks)
        assert has_cycle is False

    def test_generate_job_documentation(self, agent, sample_tasks):
        """Test job documentation generation."""
        result = agent.execute(
            {
                "job_name": "Test Job",
                "job_description": "Test description",
                "tasks": sample_tasks,
                "cluster_size": "medium",
            }
        )

        assert result["success"] is True
        doc_file = result["data"]["doc_file"]
        assert Path(doc_file).exists()

        # Read and verify documentation
        with open(doc_file, "r") as f:
            doc_content = f.read()

        assert "Test Job" in doc_content
        assert "Test description" in doc_content
        assert "extract_data" in doc_content
        assert "transform_data" in doc_content
        assert "load_data" in doc_content
        assert "Best Practices Applied" in doc_content

    def test_job_config_file_creation(self, agent, sample_tasks):
        """Test job configuration file creation."""
        result = agent.execute(
            {
                "job_name": "Test Job",
                "tasks": sample_tasks,
                "cluster_size": "small",
            }
        )

        assert result["success"] is True
        config_file = result["data"]["config_file"]
        assert Path(config_file).exists()

        # Read and verify configuration
        with open(config_file, "r") as f:
            config = json.load(f)

        assert config["name"] == "Test Job"
        assert len(config["tasks"]) == 3
        assert config["format"] == "MULTI_TASK"

    def test_max_concurrent_runs(self, agent, sample_tasks):
        """Test max concurrent runs configuration."""
        result = agent.execute(
            {
                "job_name": "Concurrent Job",
                "tasks": sample_tasks,
                "cluster_size": "medium",
                "max_concurrent_runs": 5,
            }
        )

        assert result["success"] is True
        job_config = result["data"]["job_config"]
        assert job_config["max_concurrent_runs"] == 5
        assert result["data"]["max_concurrent_runs"] == 5

    def test_job_timeout(self, agent, sample_tasks):
        """Test job timeout configuration."""
        result = agent.execute(
            {
                "job_name": "Timeout Job",
                "tasks": sample_tasks,
                "cluster_size": "medium",
                "timeout_seconds": 7200,
            }
        )

        assert result["success"] is True
        job_config = result["data"]["job_config"]
        assert job_config["timeout_seconds"] == 7200

    def test_cluster_size_presets(self, agent):
        """Test all cluster size presets."""
        for size in ["small", "medium", "large", "xlarge"]:
            task_spec = {"task_name": f"test_{size}"}
            cluster_config = agent._get_cluster_config(task_spec, size)

            assert "new_cluster" in cluster_config
            cluster = cluster_config["new_cluster"]
            assert "node_type_id" in cluster
            assert "autoscale" in cluster
            assert "spark_version" in cluster

    def test_task_with_init_scripts(self, agent):
        """Test task configuration with init scripts."""
        task_spec = {
            "task_name": "init_task",
            "task_type": "notebook",
            "notebook_path": "/test",
            "init_scripts": [{"dbfs": {"destination": "dbfs:/init.sh"}}],
        }

        cluster_config = agent._get_cluster_config(task_spec, "medium")
        cluster = cluster_config["new_cluster"]

        assert "init_scripts" in cluster
        assert cluster["init_scripts"] == [{"dbfs": {"destination": "dbfs:/init.sh"}}]

    def test_task_with_spark_env_vars(self, agent):
        """Test task configuration with Spark environment variables."""
        task_spec = {
            "task_name": "env_task",
            "task_type": "notebook",
            "notebook_path": "/test",
            "spark_env_vars": {"ENV_VAR_1": "value1", "ENV_VAR_2": "value2"},
        }

        cluster_config = agent._get_cluster_config(task_spec, "medium")
        cluster = cluster_config["new_cluster"]

        assert "spark_env_vars" in cluster
        assert cluster["spark_env_vars"] == {
            "ENV_VAR_1": "value1",
            "ENV_VAR_2": "value2",
        }


@pytest.mark.integration
class TestDatabricksJobDesignIntegration:
    """Integration tests for Databricks job design workflow."""

    def test_full_job_design_workflow(self, temp_dir):
        """Test complete job design workflow."""
        # Define tasks
        tasks = [
            {
                "task_name": "ingest",
                "task_type": "notebook",
                "description": "Ingest raw data",
                "notebook_path": "/Workspace/notebooks/ingest",
                "parameters": {"source": "s3://bucket/data"},
                "max_retries": 2,
                "timeout_seconds": 3600,
            },
            {
                "task_name": "process",
                "task_type": "python",
                "description": "Process ingested data",
                "package_name": "data_processor",
                "entry_point": "main",
                "parameters": ["--mode", "batch"],
                "depends_on": ["ingest"],
                "max_retries": 2,
                "timeout_seconds": 7200,
            },
            {
                "task_name": "validate",
                "task_type": "notebook",
                "description": "Validate processed data",
                "notebook_path": "/Workspace/notebooks/validate",
                "parameters": {"threshold": "0.95"},
                "depends_on": ["process"],
                "max_retries": 1,
                "timeout_seconds": 1800,
            },
        ]

        # Create agent
        agent = DatabricksJobDesignAgent(
            work_item_id="integration_test", evidence_base_path=temp_dir
        )

        # Design job
        result = agent.execute(
            {
                "job_name": "Data Pipeline",
                "job_description": "Complete data processing pipeline",
                "tasks": tasks,
                "cluster_size": "large",
                "schedule": {
                    "quartz_cron_expression": "0 0 2 * * ?",
                    "timezone_id": "UTC",
                    "pause_status": "UNPAUSED",
                },
                "notification_emails": ["data-team@example.com"],
                "max_concurrent_runs": 3,
                "timeout_seconds": 14400,
            }
        )

        # Verify result
        assert result["success"] is True
        assert result["data"]["validation"]["valid"] is True

        # Verify configuration file
        config_file = Path(result["data"]["config_file"])
        assert config_file.exists()

        with open(config_file, "r") as f:
            config = json.load(f)

        assert config["name"] == "Data Pipeline"
        assert len(config["tasks"]) == 3
        assert config["max_concurrent_runs"] == 3
        assert "schedule" in config

        # Verify documentation file
        doc_file = Path(result["data"]["doc_file"])
        assert doc_file.exists()
