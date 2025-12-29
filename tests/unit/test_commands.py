"""
Unit tests for Databricks Engineering Plugin commands and utilities.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import json


class TestPlanPipelineCommand:
    """Tests for plan-pipeline command functionality."""
    
    @pytest.fixture
    def mock_workspace_client(self):
        """Mock Databricks WorkspaceClient."""
        with patch('databricks.sdk.WorkspaceClient') as mock:
            yield mock
    
    @pytest.fixture
    def sample_pipeline_spec(self):
        """Sample pipeline specification for testing."""
        return {
            "name": "customer_360",
            "description": "Customer 360 data pipeline",
            "source": {
                "type": "salesforce",
                "tables": ["Account", "Contact", "Opportunity"]
            },
            "architecture": "medallion",
            "target_catalog": "prod_data",
            "refresh_schedule": "daily"
        }
    
    def test_plan_pipeline_basic(self, mock_workspace_client, sample_pipeline_spec):
        """Test basic pipeline planning."""
        from plugins.databricks_engineering.commands import plan_pipeline
        
        result = plan_pipeline.create_plan(sample_pipeline_spec)
        
        assert result is not None
        assert "bronze" in result["layers"]
        assert "silver" in result["layers"]
        assert "gold" in result["layers"]
        assert result["estimated_cost"] > 0
    
    def test_plan_pipeline_with_quality_checks(self, sample_pipeline_spec):
        """Test pipeline planning with data quality requirements."""
        from plugins.databricks_engineering.commands import plan_pipeline
        
        sample_pipeline_spec["quality_level"] = "high"
        result = plan_pipeline.create_plan(sample_pipeline_spec)
        
        assert "quality_checks" in result
        assert len(result["quality_checks"]) > 0
        assert "great_expectations" in result["quality_checks"]
    
    def test_plan_pipeline_cost_estimation(self, sample_pipeline_spec):
        """Test cost estimation accuracy."""
        from plugins.databricks_engineering.commands import plan_pipeline
        
        result = plan_pipeline.estimate_costs(
            data_volume_gb=100,
            daily_runs=1,
            cluster_size="medium"
        )
        
        assert result["compute_cost"] > 0
        assert result["storage_cost"] > 0
        assert result["total_monthly_cost"] > 0
        assert result["total_monthly_cost"] == result["compute_cost"] + result["storage_cost"]
    
    def test_plan_pipeline_invalid_architecture(self, sample_pipeline_spec):
        """Test error handling for invalid architecture."""
        from plugins.databricks_engineering.commands import plan_pipeline
        
        sample_pipeline_spec["architecture"] = "invalid"
        
        with pytest.raises(ValueError, match="Invalid architecture type"):
            plan_pipeline.create_plan(sample_pipeline_spec)


class TestDataProductManager:
    """Tests for data product creation and management."""
    
    @pytest.fixture
    def sample_data_product(self):
        """Sample data product configuration."""
        return {
            "name": "customer_insights",
            "owner": "analytics_team",
            "catalog": "prod_data_products",
            "schema": "customer",
            "table": "customer_360_gold",
            "sla": {
                "availability": 99.5,
                "latency_hours": 6,
                "refresh_schedule": "0 2 * * *"
            },
            "data_contract": {
                "schema": {
                    "customer_id": "BIGINT",
                    "email": "STRING",
                    "lifetime_value": "DECIMAL(10,2)"
                },
                "quality_rules": [
                    {
                        "name": "no_duplicate_customers",
                        "rule": "COUNT(*) = COUNT(DISTINCT customer_id)",
                        "severity": "critical"
                    }
                ]
            }
        }
    
    def test_create_data_product(self, sample_data_product):
        """Test data product creation."""
        from plugins.databricks_engineering.commands import create_data_product
        
        result = create_data_product.create(sample_data_product)
        
        assert result["status"] == "success"
        assert "contract_file" in result
        assert "sla_definition" in result
    
    def test_validate_data_contract(self, sample_data_product):
        """Test data contract validation."""
        from plugins.databricks_engineering.utils import validate_contract
        
        contract = sample_data_product["data_contract"]
        validation_result = validate_contract(contract)
        
        assert validation_result["valid"] is True
        assert len(validation_result["errors"]) == 0
    
    def test_invalid_sla_definition(self, sample_data_product):
        """Test SLA validation."""
        from plugins.databricks_engineering.commands import create_data_product
        
        sample_data_product["sla"]["availability"] = 101  # Invalid
        
        with pytest.raises(ValueError, match="Availability must be between 0 and 100"):
            create_data_product.create(sample_data_product)


class TestDeltaSharingManager:
    """Tests for Delta Sharing functionality."""
    
    @pytest.fixture
    def mock_shares_api(self):
        """Mock Delta Sharing API."""
        with patch('databricks.sdk.service.sharing.SharesAPI') as mock:
            yield mock
    
    def test_create_share(self, mock_shares_api):
        """Test creating a Delta share."""
        from plugins.databricks_engineering.commands import configure_delta_share
        
        share_config = {
            "name": "customer_insights_share",
            "tables": [
                "prod_data_products.customer.customer_summary",
                "prod_data_products.customer.customer_trends"
            ]
        }
        
        result = configure_delta_share.create_share(share_config)
        
        assert result["share_name"] == "customer_insights_share"
        assert len(result["tables"]) == 2
        mock_shares_api.create.assert_called_once()
    
    def test_create_recipient(self, mock_shares_api):
        """Test creating a share recipient."""
        from plugins.databricks_engineering.commands import configure_delta_share
        
        recipient_config = {
            "name": "partner_abc",
            "email": "data@partnerabc.com",
            "rate_limit_per_day": 1000,
            "expiration_days": 90
        }
        
        result = configure_delta_share.create_recipient(recipient_config)
        
        assert result["recipient_name"] == "partner_abc"
        assert "activation_url" in result
        assert result["expiration_days"] == 90


class TestDatabricksAssetBundles:
    """Tests for Databricks Asset Bundle deployment."""
    
    @pytest.fixture
    def sample_bundle_config(self, tmp_path):
        """Sample bundle configuration."""
        bundle_dir = tmp_path / "test_bundle"
        bundle_dir.mkdir()
        
        bundle_config = {
            "bundle": {
                "name": "test_pipeline"
            },
            "targets": {
                "dev": {
                    "mode": "development",
                    "workspace": {
                        "host": "https://dev.databricks.com"
                    }
                },
                "prod": {
                    "mode": "production",
                    "workspace": {
                        "host": "https://prod.databricks.com"
                    }
                }
            }
        }
        
        config_file = bundle_dir / "databricks.yml"
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(bundle_config, f)
        
        return bundle_dir
    
    def test_validate_bundle_config(self, sample_bundle_config):
        """Test bundle configuration validation."""
        from plugins.databricks_engineering.commands import validate_deployment
        
        result = validate_deployment.validate_bundle(sample_bundle_config)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_bundle_missing_target(self, sample_bundle_config, tmp_path):
        """Test validation with missing target."""
        from plugins.databricks_engineering.commands import validate_deployment
        
        # Create config without targets
        invalid_bundle = tmp_path / "invalid_bundle"
        invalid_bundle.mkdir()
        
        config = {"bundle": {"name": "test"}}
        config_file = invalid_bundle / "databricks.yml"
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(config, f)
        
        result = validate_deployment.validate_bundle(invalid_bundle)
        
        assert result["valid"] is False
        assert "Missing required field: targets" in result["errors"]
    
    def test_cost_estimation(self):
        """Test deployment cost estimation."""
        from plugins.databricks_engineering.commands import validate_deployment
        
        bundle_config = {
            "jobs": {
                "main_pipeline": {
                    "cluster": {
                        "num_workers": 5,
                        "node_type": "i3.xlarge"
                    },
                    "schedule": "daily"
                }
            }
        }
        
        result = validate_deployment.estimate_costs(bundle_config, environment="prod")
        
        assert result["monthly_cost"] > 0
        assert "compute_cost" in result
        assert "storage_cost" in result


class TestDataQuality:
    """Tests for data quality validation."""
    
    @pytest.fixture
    def sample_quality_config(self):
        """Sample quality check configuration."""
        return {
            "table": "customer_360_gold",
            "checks": [
                {
                    "name": "no_nulls_in_id",
                    "column": "customer_id",
                    "constraint": "not_null"
                },
                {
                    "name": "valid_email_format",
                    "column": "email",
                    "constraint": "regex",
                    "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                },
                {
                    "name": "positive_ltv",
                    "column": "lifetime_value",
                    "constraint": "min_value",
                    "value": 0
                }
            ]
        }
    
    def test_generate_quality_checks(self, sample_quality_config):
        """Test quality check generation."""
        from plugins.databricks_engineering.commands import test_data_quality
        
        result = test_data_quality.generate_checks(sample_quality_config)
        
        assert "great_expectations" in result
        assert len(result["expectations"]) == 3
    
    def test_run_quality_checks(self, spark_session, sample_data):
        """Test executing quality checks."""
        from plugins.databricks_engineering.utils import quality_checker
        
        checks = [
            {"column": "customer_id", "constraint": "not_null"},
            {"column": "email", "constraint": "unique"}
        ]
        
        result = quality_checker.run_checks(sample_data, checks)
        
        assert result["passed"] >= 0
        assert result["failed"] >= 0
        assert result["total"] == len(checks)


class TestCostOptimization:
    """Tests for cost optimization features."""
    
    def test_analyze_cluster_costs(self):
        """Test cluster cost analysis."""
        from plugins.databricks_engineering.commands import optimize_costs
        
        cluster_config = {
            "node_type": "i3.xlarge",
            "num_workers": 10,
            "autoscale": {
                "min_workers": 2,
                "max_workers": 10
            },
            "usage_hours_per_day": 8
        }
        
        result = optimize_costs.analyze_cluster(cluster_config)
        
        assert "current_cost" in result
        assert "optimized_cost" in result
        assert "savings" in result
        assert result["savings"] >= 0
    
    def test_suggest_optimizations(self):
        """Test optimization suggestions."""
        from plugins.databricks_engineering.commands import optimize_costs
        
        query_profile = {
            "shuffle_read_gb": 100,
            "shuffle_write_gb": 100,
            "spill_to_disk_gb": 50,
            "task_skew_ratio": 5.0
        }
        
        suggestions = optimize_costs.suggest_optimizations(query_profile)
        
        assert len(suggestions) > 0
        assert any("shuffle" in s.lower() for s in suggestions)
        assert any("skew" in s.lower() for s in suggestions)


@pytest.fixture(scope="session")
def spark_session():
    """Create Spark session for testing."""
    from pyspark.sql import SparkSession
    from delta import configure_spark_with_delta_pip
    
    builder = (SparkSession.builder
        .appName("pytest-spark")
        .master("local[*]")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", 
                "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    )
    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    
    yield spark
    
    spark.stop()


@pytest.fixture
def sample_data(spark_session):
    """Generate sample DataFrame for testing."""
    data = [
        (1, "alice@example.com", 1000.0, "2024-01-01"),
        (2, "bob@example.com", 2000.0, "2024-01-02"),
        (3, "charlie@example.com", 1500.0, "2024-01-03"),
    ]
    
    return spark_session.createDataFrame(
        data,
        ["customer_id", "email", "lifetime_value", "created_at"]
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=plugins", "--cov-report=html"])
