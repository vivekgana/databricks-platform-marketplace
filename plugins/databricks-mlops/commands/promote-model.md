# Promote Model Command

**Last Updated:** 2026-01-01 22:45:49
**Version:** 1.0.0
**Category:** Lifecycle

## Overview

Promote models across environments (dev/staging/production) with validation gates and approval workflows.

## Command Usage

```bash
/databricks-mlops:promote-model --model-name <name> --version <version> --target-stage <stage>
```

## Model Promotion Script

```python
from mlflow.tracking import MlflowClient
import mlflow
from databricks.sdk import WorkspaceClient

client = MlflowClient()
w = WorkspaceClient()

def promote_model(
    model_name: str,
    version: int,
    target_stage: str,
    validation_required: bool = True
):
    """Promote model to target stage with validation"""

    # Validation gates
    if validation_required:
        if not run_promotion_validation(model_name, version, target_stage):
            raise ValueError("Model failed promotion validation")

    # Archive existing models in target stage
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage=target_stage,
        archive_existing_versions=True
    )

    # Set alias
    alias_map = {
        "Staging": "staging",
        "Production": "champion"
    }

    if target_stage in alias_map:
        client.set_registered_model_alias(
            name=model_name,
            alias=alias_map[target_stage],
            version=version
        )

    print(f"✓ Model {model_name} v{version} promoted to {target_stage}")

    # Update deployment
    if target_stage == "Production":
        update_production_endpoint(model_name, version)

    return True

def run_promotion_validation(model_name: str, version: int, target_stage: str):
    """Run validation checks before promotion"""

    checks = []

    # 1. Performance validation
    model_version = client.get_model_version(model_name, version)
    run = client.get_run(model_version.run_id)

    required_metrics = {
        "test_accuracy": 0.85,
        "test_precision": 0.80
    }

    for metric, threshold in required_metrics.items():
        actual = run.data.metrics.get(metric, 0)
        passed = actual >= threshold
        checks.append({
            "check": f"{metric} >= {threshold}",
            "passed": passed,
            "actual": actual
        })

    # 2. Model metadata check
    checks.append({
        "check": "Model has description",
        "passed": model_version.description is not None
    })

    # 3. Model signature check
    model_uri = f"models:/{model_name}/{version}"
    model = mlflow.pyfunc.load_model(model_uri)
    checks.append({
        "check": "Model has signature",
        "passed": hasattr(model, 'metadata') and model.metadata.signature is not None
    })

    # Print results
    print(f"\nPromotion Validation: {target_stage}")
    print("=" * 50)
    for check in checks:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['check']}")

    return all(check['passed'] for check in checks)

def update_production_endpoint(model_name: str, version: int):
    """Update production endpoint with new model version"""

    endpoint_name = f"{model_name.split('.')[-1]}_production"

    from databricks.sdk.service.serving import ServedModelInput

    served_model = ServedModelInput(
        model_name=model_name,
        model_version=str(version),
        workload_size="Small",
        scale_to_zero_enabled=False
    )

    try:
        w.serving_endpoints.update_config(
            name=endpoint_name,
            served_models=[served_model]
        )
        print(f"✓ Updated production endpoint: {endpoint_name}")
    except Exception as e:
        print(f"Warning: Could not update endpoint: {e}")

# Example usage
if __name__ == "__main__":
    promote_model(
        model_name="main.ml_models.churn_classifier",
        version=5,
        target_stage="Production",
        validation_required=True
    )
```

## Promotion Workflow

1. **Development → Staging**
   - Automated validation
   - Performance checks
   - Deploy to staging endpoint

2. **Staging → Production**
   - Manual approval (optional)
   - Comprehensive validation
   - Canary deployment
   - Full rollout

## Best Practices

1. Use validation gates
2. Require approvals for production
3. Implement rollback procedures
4. Monitor after promotion
5. Document promotion decisions

## References

- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)
