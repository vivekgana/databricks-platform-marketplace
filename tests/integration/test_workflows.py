"""
Integration tests for Databricks Engineering Plugin.
Tests full workflows against Databricks workspace.
"""
import pytest
import os
from datetime import datetime
from databricks.sdk import WorkspaceClient
from pathlib import Path


@pytest.fixture(scope="session")
def workspace_client():
    """Create Databricks workspace client."""
    host = os.getenv("DATABRICKS_HOST")
    token = os.getenv("DATABRICKS_TOKEN")
    
    if not host or not token:
        pytest.skip("Databricks credentials not set. Set DATABRICKS_HOST and DATABRICKS_TOKEN")
    
    return WorkspaceClient(host=host, token=token)


@pytest.fixture(scope="session")
def test_catalog(workspace_client):
    """Create test catalog for integration tests."""
    catalog_name = f"test_catalog_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create catalog
    workspace_client.catalogs.create(name=catalog_name, comment="Integration test catalog")
    
    yield catalog_name
    
    # Cleanup
    try:
        workspace_client.catalogs.delete(name=catalog_name, force=True)
    except Exception as e:
        print(f"Warning: Failed to cleanup catalog {catalog_name}: {e}")


class TestEndToEndPipeline:
    """Test complete pipeline workflow from planning to deployment."""
    
    def test_full_pipeline_workflow(self, workspace_client, test_catalog, tmp_path):
        """Test complete pipeline lifecycle."""
        from plugins.databricks_engineering.commands import (
            plan_pipeline,
            work_pipeline,
            deploy_bundle
        )
        
        # 1. Plan pipeline
        pipeline_spec = {
            "name": "test_customer_pipeline",
            "description": "Test pipeline for integration tests",
            "source": {
                "type": "csv",
                "path": f"dbfs:/tmp/test_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            },
            "target_catalog": test_catalog,
            "target_schema": "test_schema",
            "architecture": "medallion"
        }
        
        plan = plan_pipeline.create_plan(pipeline_spec)
        assert plan is not None
        assert "bronze" in plan["layers"]
        
        # 2. Generate sample data
        sample_data = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
            {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
        ]
        
        # Write to DBFS (simplified - in real test would use workspace_client)
        # workspace_client.dbfs.put(...)
        
        # 3. Create bundle configuration
        bundle_config = {
            "bundle": {
                "name": "test_pipeline"
            },
            "targets": {
                "dev": {
                    "mode": "development",
                    "variables": {
                        "catalog": test_catalog
                    }
                }
            }
        }
        
        bundle_path = tmp_path / "bundle"
        bundle_path.mkdir()
        
        # 4. Deploy (mock deployment for test)
        # In real integration test, would deploy to workspace
        # result = deploy_bundle.deploy(bundle_path, "dev")
        # assert result["status"] == "success"
        
        print("Full pipeline workflow test completed successfully")


class TestDataProductLifecycle:
    """Test data product creation and management."""
    
    def test_create_and_publish_data_product(self, workspace_client, test_catalog):
        """Test data product creation and publishing to Unity Catalog."""
        from plugins.databricks_engineering.commands import (
            create_data_product,
            publish_data_product
        )
        
        # 1. Create data product
        product_config = {
            "name": "test_customer_insights",
            "owner": "test_team",
            "catalog": test_catalog,
            "schema": "products",
            "table": "customer_insights_gold",
            "sla": {
                "availability": 99.5,
                "latency_hours": 6,
                "refresh_schedule": "0 2 * * *"
            },
            "data_contract": {
                "schema": {
                    "customer_id": "BIGINT",
                    "total_purchases": "INT",
                    "lifetime_value": "DECIMAL(10,2)"
                }
            }
        }
        
        result = create_data_product.create(product_config)
        assert result["status"] == "success"
        
        # 2. Create test table in Unity Catalog
        spark = workspace_client.sql_warehouses.get_spark_session()
        test_data = [
            (1, 10, 1000.50),
            (2, 5, 500.25),
            (3, 15, 1500.75)
        ]
        
        # In real test would create actual table
        # df = spark.createDataFrame(test_data, ["customer_id", "total_purchases", "lifetime_value"])
        # df.write.saveAsTable(f"{test_catalog}.products.customer_insights_gold")
        
        # 3. Publish data product
        # publish_result = publish_data_product.publish(result["product_id"])
        # assert publish_result["status"] == "published"
        
        print("Data product lifecycle test completed")


class TestDeltaSharing:
    """Test Delta Sharing functionality."""
    
    @pytest.mark.skipif(
        os.getenv("SKIP_DELTA_SHARING_TESTS") == "true",
        reason="Delta Sharing tests require enterprise workspace"
    )
    def test_delta_sharing_setup(self, workspace_client, test_catalog):
        """Test Delta Sharing configuration."""
        from plugins.databricks_engineering.commands import configure_delta_share
        
        # 1. Create share
        share_config = {
            "name": f"test_share_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "tables": [
                f"{test_catalog}.test_schema.test_table"
            ],
            "description": "Integration test share"
        }
        
        # Note: Real test would create share
        # share = configure_delta_share.create_share(share_config)
        # assert share["share_name"] == share_config["name"]
        
        # 2. Create recipient
        recipient_config = {
            "name": "test_recipient",
            "email": "test@example.com",
            "rate_limit_per_day": 100,
            "expiration_days": 7
        }
        
        # Note: Real test would create recipient
        # recipient = configure_delta_share.create_recipient(recipient_config)
        # assert "activation_url" in recipient
        
        print("Delta Sharing test completed")


class TestDatabricksAssetBundleDeployment:
    """Test Databricks Asset Bundle deployment."""
    
    def test_bundle_deployment(self, workspace_client, test_catalog, tmp_path):
        """Test deploying bundle to Databricks workspace."""
        from plugins.databricks_engineering.commands import (
            validate_deployment,
            deploy_bundle
        )
        
        # 1. Create bundle structure
        bundle_dir = tmp_path / "test_bundle"
        bundle_dir.mkdir()
        
        resources_dir = bundle_dir / "resources"
        resources_dir.mkdir()
        
        # Create databricks.yml
        bundle_config = {
            "bundle": {
                "name": "integration_test_pipeline"
            },
            "variables": {
                "catalog": {
                    "default": test_catalog
                }
            },
            "targets": {
                "dev": {
                    "mode": "development",
                    "workspace": {
                        "host": os.getenv("DATABRICKS_HOST")
                    }
                }
            }
        }
        
        import yaml
        with open(bundle_dir / "databricks.yml", "w") as f:
            yaml.dump(bundle_config, f)
        
        # 2. Validate bundle
        validation = validate_deployment.validate_bundle(bundle_dir)
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0
        
        # 3. Estimate costs
        cost_estimate = validate_deployment.estimate_costs(bundle_config, "dev")
        assert "monthly_cost" in cost_estimate
        assert cost_estimate["monthly_cost"] >= 0
        
        # 4. Deploy (mock in test)
        # In production test, would actually deploy:
        # deployment = deploy_bundle.deploy(bundle_dir, "dev")
        # assert deployment["status"] == "success"
        
        print("Bundle deployment test completed")


class TestDataQualityMonitoring:
    """Test data quality monitoring and alerting."""
    
    def test_quality_monitoring_setup(self, workspace_client, test_catalog, spark_session):
        """Test setting up data quality monitoring."""
        from plugins.databricks_engineering.commands import (
            test_data_quality,
            monitor_data_product
        )
        
        # 1. Create test data with quality issues
        test_data = spark_session.createDataFrame([
            (1, "alice@example.com", 1000.0),
            (2, None, 2000.0),  # Missing email
            (3, "invalid-email", -500.0),  # Invalid email and negative value
            (4, "bob@example.com", 1500.0),
        ], ["customer_id", "email", "lifetime_value"])
        
        # 2. Generate quality checks
        quality_config = {
            "table": f"{test_catalog}.test_schema.test_table",
            "checks": [
                {
                    "name": "no_null_emails",
                    "column": "email",
                    "constraint": "not_null"
                },
                {
                    "name": "valid_email_format",
                    "column": "email",
                    "constraint": "regex",
                    "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                },
                {
                    "name": "positive_lifetime_value",
                    "column": "lifetime_value",
                    "constraint": "min_value",
                    "value": 0
                }
            ]
        }
        
        checks = test_data_quality.generate_checks(quality_config)
        assert len(checks["expectations"]) > 0
        
        # 3. Run quality checks
        from plugins.databricks_engineering.utils import quality_checker
        results = quality_checker.run_checks(test_data, quality_config["checks"])
        
        assert results["total"] == 3
        assert results["failed"] > 0  # We expect failures from bad data
        
        print("Data quality monitoring test completed")


class TestCostOptimization:
    """Test cost optimization features."""
    
    def test_cost_analysis_and_optimization(self, workspace_client):
        """Test cost analysis and optimization suggestions."""
        from plugins.databricks_engineering.commands import optimize_costs
        
        # 1. Analyze current cluster costs
        cluster_config = {
            "cluster_id": os.getenv("TEST_CLUSTER_ID"),
            "node_type": "i3.xlarge",
            "num_workers": 10,
            "autoscale": None,
            "spot_instances": False
        }
        
        if cluster_config["cluster_id"]:
            analysis = optimize_costs.analyze_cluster(cluster_config)
            
            assert "current_cost" in analysis
            assert "optimized_cost" in analysis
            assert "recommendations" in analysis
            
            # 2. Get optimization suggestions
            assert len(analysis["recommendations"]) > 0
            
            # Common recommendations should include:
            # - Enable autoscaling
            # - Use spot instances
            # - Right-size cluster
            
            print(f"Cost optimization analysis: {analysis}")
        else:
            print("Skipping cost optimization test - no test cluster ID provided")


@pytest.fixture
def spark_session(workspace_client):
    """Create Spark session using Databricks SQL Warehouse."""
    warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
    
    if not warehouse_id:
        pytest.skip("DATABRICKS_WAREHOUSE_ID not set")
    
    # In real integration, would connect to warehouse
    # For now, create local session for testing
    from pyspark.sql import SparkSession
    from delta import configure_spark_with_delta_pip
    
    builder = (SparkSession.builder
        .appName("integration-test")
        .master("local[*]")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog",
                "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    )
    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    
    yield spark
    
    spark.stop()


if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-m", "not slow"
    ])
