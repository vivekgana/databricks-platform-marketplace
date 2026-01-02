# Register Model Command

**Last Updated:** 2026-01-01 22:45:49
**Version:** 1.0.0
**Category:** Registry

## Overview

Register trained models to MLflow Model Registry with versioning, stage management, and governance. This command handles model registration, version management, and Unity Catalog integration.

## Command Usage

```bash
/databricks-mlops:register-model [--run-id <id>] [--model-name <name>]
```

## Parameters

- `--run-id`: MLflow run ID containing the model to register
- `--model-name`: Name for the registered model in Unity Catalog
- `--description`: Model description and metadata
- `--tags`: Tags for model categorization

## Registration Process

You are an expert in MLflow Model Registry and model governance. Guide the user through:

### 1. Model Registration Script

```python
import mlflow
from mlflow.tracking import MlflowClient
from databricks import feature_store
import json
from datetime import datetime

# Configuration
CATALOG = "main"
SCHEMA = "ml_models"
MODEL_NAME = "{model_name}"

client = MlflowClient()
fs_client = feature_store.FeatureStoreClient()

def register_model_from_run(run_id: str, model_name: str, description: str = None):
    """Register model from MLflow run to Unity Catalog"""

    # Get run information
    run = client.get_run(run_id)
    model_uri = f"runs:/{run_id}/model"

    # Full model name with Unity Catalog
    full_model_name = f"{CATALOG}.{SCHEMA}.{model_name}"

    print(f"Registering model: {full_model_name}")
    print(f"Source run: {run_id}")

    # Register model
    model_version = mlflow.register_model(
        model_uri=model_uri,
        name=full_model_name,
        tags={
            "source_run_id": run_id,
            "registration_date": datetime.now().isoformat(),
            "framework": run.data.tags.get("mlflow.runName", "unknown")
        }
    )

    # Update model description
    if description:
        client.update_model_version(
            name=full_model_name,
            version=model_version.version,
            description=description
        )

    # Add model metadata
    metadata = {
        "training_date": run.info.start_time,
        "metrics": run.data.metrics,
        "parameters": run.data.params,
        "features": run.data.tags.get("features", [])
    }

    client.set_model_version_tag(
        name=full_model_name,
        version=model_version.version,
        key="metadata",
        value=json.dumps(metadata)
    )

    print(f"✓ Model registered: {full_model_name}")
    print(f"✓ Version: {model_version.version}")
    print(f"✓ Status: {model_version.status}")

    return model_version

def transition_model_stage(model_name: str, version: int, stage: str):
    """Transition model to different stage (Staging/Production)"""

    full_model_name = f"{CATALOG}.{SCHEMA}.{model_name}"

    client.transition_model_version_stage(
        name=full_model_name,
        version=version,
        stage=stage,
        archive_existing_versions=True
    )

    print(f"✓ Model {full_model_name} v{version} transitioned to {stage}")

def set_model_alias(model_name: str, version: int, alias: str):
    """Set alias for model version (e.g., 'champion', 'challenger')"""

    full_model_name = f"{CATALOG}.{SCHEMA}.{model_name}"

    client.set_registered_model_alias(
        name=full_model_name,
        alias=alias,
        version=version
    )

    print(f"✓ Set alias '{alias}' for {full_model_name} v{version}")

def get_model_version_details(model_name: str, version: int = None):
    """Get detailed information about a model version"""

    full_model_name = f"{CATALOG}.{SCHEMA}.{model_name}"

    if version:
        mv = client.get_model_version(full_model_name, version)
    else:
        # Get latest version
        model_versions = client.search_model_versions(f"name='{full_model_name}'")
        mv = sorted(model_versions, key=lambda x: x.version, reverse=True)[0]

    details = {
        "name": mv.name,
        "version": mv.version,
        "stage": mv.current_stage,
        "status": mv.status,
        "creation_time": mv.creation_timestamp,
        "run_id": mv.run_id,
        "description": mv.description,
        "tags": mv.tags
    }

    return details

def compare_model_versions(model_name: str, version1: int, version2: int):
    """Compare two model versions"""

    full_model_name = f"{CATALOG}.{SCHEMA}.{model_name}"

    mv1 = client.get_model_version(full_model_name, version1)
    mv2 = client.get_model_version(full_model_name, version2)

    # Get metrics from runs
    run1 = client.get_run(mv1.run_id)
    run2 = client.get_run(mv2.run_id)

    comparison = {
        "version_1": {
            "version": version1,
            "metrics": run1.data.metrics,
            "stage": mv1.current_stage
        },
        "version_2": {
            "version": version2,
            "metrics": run2.data.metrics,
            "stage": mv2.current_stage
        }
    }

    print(f"\nModel Comparison: {model_name}")
    print(f"Version {version1} vs Version {version2}")
    print("-" * 50)

    for metric in run1.data.metrics.keys():
        val1 = run1.data.metrics.get(metric, 0)
        val2 = run2.data.metrics.get(metric, 0)
        diff = val2 - val1
        print(f"{metric}: {val1:.4f} -> {val2:.4f} (Δ {diff:+.4f})")

    return comparison

# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python register_model.py <run_id> <model_name>")
        sys.exit(1)

    run_id = sys.argv[1]
    model_name = sys.argv[2]
    description = sys.argv[3] if len(sys.argv) > 3 else None

    # Register model
    model_version = register_model_from_run(run_id, model_name, description)

    # Get model details
    details = get_model_version_details(model_name, model_version.version)
    print(f"\nModel Details:")
    print(json.dumps(details, indent=2, default=str))
```

### 2. Model Governance

Implement model governance policies:

```python
def validate_model_for_registration(run_id: str, min_metrics: dict):
    """Validate model meets minimum requirements before registration"""

    run = client.get_run(run_id)
    metrics = run.data.metrics

    validation_results = {}
    all_passed = True

    for metric_name, min_value in min_metrics.items():
        actual_value = metrics.get(metric_name)

        if actual_value is None:
            validation_results[metric_name] = {
                "status": "FAILED",
                "reason": f"Metric {metric_name} not found in run"
            }
            all_passed = False
        elif actual_value < min_value:
            validation_results[metric_name] = {
                "status": "FAILED",
                "expected": f">= {min_value}",
                "actual": actual_value
            }
            all_passed = False
        else:
            validation_results[metric_name] = {
                "status": "PASSED",
                "actual": actual_value
            }

    return all_passed, validation_results

def register_model_with_validation(run_id: str, model_name: str):
    """Register model with automatic validation"""

    # Define minimum requirements
    min_metrics = {
        "test_accuracy": 0.85,
        "test_precision": 0.80,
        "test_recall": 0.80
    }

    # Validate
    passed, results = validate_model_for_registration(run_id, min_metrics)

    if not passed:
        print("❌ Model validation failed:")
        print(json.dumps(results, indent=2))
        return None

    print("✓ Model validation passed")

    # Register model
    model_version = register_model_from_run(run_id, model_name)

    return model_version
```

### 3. Model Versioning Strategy

```python
def manage_model_versions(model_name: str, max_versions: int = 10):
    """Manage model versions and cleanup old versions"""

    full_model_name = f"{CATALOG}.{SCHEMA}.{model_name}"

    # Get all versions
    versions = client.search_model_versions(f"name='{full_model_name}'")
    sorted_versions = sorted(versions, key=lambda x: x.creation_timestamp, reverse=True)

    print(f"Found {len(sorted_versions)} versions of {model_name}")

    # Keep production and staging versions
    protected_stages = ["Production", "Staging"]
    protected_versions = [v for v in sorted_versions if v.current_stage in protected_stages]

    # Archive old versions (keeping max_versions)
    archived_count = 0
    for version in sorted_versions[max_versions:]:
        if version.current_stage not in protected_stages:
            client.transition_model_version_stage(
                name=full_model_name,
                version=version.version,
                stage="Archived"
            )
            archived_count += 1

    print(f"✓ Archived {archived_count} old versions")
    print(f"✓ Protected {len(protected_versions)} versions in {protected_stages}")

    return archived_count
```

## Best Practices

1. **Version Control**
   - Use semantic versioning
   - Document changes between versions
   - Maintain version history

2. **Model Metadata**
   - Add comprehensive descriptions
   - Tag models appropriately
   - Link to training runs

3. **Stage Management**
   - Use staging before production
   - Implement approval workflows
   - Test thoroughly in staging

4. **Governance**
   - Set minimum quality thresholds
   - Require approval for production
   - Audit model changes

## Next Steps

After registration:
1. Use `/databricks-mlops:validate-model` to validate in staging
2. Use `/databricks-mlops:deploy-model` to deploy to endpoints
3. Use `/databricks-mlops:setup-monitoring` for production monitoring

## References

- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)
- [Unity Catalog for ML](https://docs.databricks.com/machine-learning/manage-model-lifecycle/index.html)
