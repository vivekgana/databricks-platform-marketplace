# Deploy Model Command

**Last Updated:** 2026-01-01 22:45:49
**Version:** 1.0.0
**Category:** Deployment

## Overview

Deploy ML models to Databricks Model Serving endpoints with auto-scaling, monitoring, and A/B testing support.

## Command Usage

```bash
/databricks-mlops:deploy-model --model-name <name> --version <version> --endpoint-name <endpoint>
```

## Deployment Script

```python
import requests
import json
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import EndpointCoreConfigInput, ServedModelInput

w = WorkspaceClient()

def create_model_serving_endpoint(
    endpoint_name: str,
    model_name: str,
    model_version: str,
    workload_size: str = "Small",
    scale_to_zero: bool = True
):
    """Create or update model serving endpoint"""

    served_models = [
        ServedModelInput(
            model_name=model_name,
            model_version=model_version,
            workload_size=workload_size,
            scale_to_zero_enabled=scale_to_zero
        )
    ]

    config = EndpointCoreConfigInput(served_models=served_models)

    try:
        # Try to get existing endpoint
        existing = w.serving_endpoints.get(endpoint_name)

        # Update existing endpoint
        w.serving_endpoints.update_config(
            name=endpoint_name,
            served_models=served_models
        )
        print(f"✓ Updated endpoint: {endpoint_name}")

    except Exception:
        # Create new endpoint
        w.serving_endpoints.create(
            name=endpoint_name,
            config=config
        )
        print(f"✓ Created endpoint: {endpoint_name}")

    # Wait for endpoint to be ready
    w.serving_endpoints.wait_get_serving_endpoint_not_updating(endpoint_name)

    return endpoint_name

def test_endpoint(endpoint_name: str, test_data: dict):
    """Test deployed model endpoint"""

    endpoint = w.serving_endpoints.get(endpoint_name)
    url = f"{w.config.host}/serving-endpoints/{endpoint_name}/invocations"

    headers = {
        "Authorization": f"Bearer {w.config.token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=test_data)

    return response.json()

def setup_ab_testing(
    endpoint_name: str,
    model_a: tuple,  # (model_name, version, traffic_percentage)
    model_b: tuple
):
    """Setup A/B testing with traffic split"""

    served_models = [
        ServedModelInput(
            model_name=model_a[0],
            model_version=model_a[1],
            workload_size="Small",
            scale_to_zero_enabled=True,
            traffic_percentage=model_a[2]
        ),
        ServedModelInput(
            model_name=model_b[0],
            model_version=model_b[1],
            workload_size="Small",
            scale_to_zero_enabled=True,
            traffic_percentage=model_b[2]
        )
    ]

    w.serving_endpoints.update_config(
        name=endpoint_name,
        served_models=served_models
    )

    print(f"✓ A/B testing configured:")
    print(f"  Model A ({model_a[0]} v{model_a[1]}): {model_a[2]}% traffic")
    print(f"  Model B ({model_b[0]} v{model_b[1]}): {model_b[2]}% traffic")

# Example usage
if __name__ == "__main__":
    endpoint = create_model_serving_endpoint(
        endpoint_name="my_model_endpoint",
        model_name="main.ml_models.my_model",
        model_version="1"
    )

    # Test endpoint
    test_data = {"dataframe_records": [{"feature1": 1.0, "feature2": 2.0}]}
    result = test_endpoint(endpoint, test_data)
    print(f"Prediction: {result}")
```

## Best Practices

1. **Endpoint Configuration**
   - Start with small workload size
   - Enable scale-to-zero for cost savings
   - Use appropriate timeout settings

2. **Testing**
   - Test in staging environment first
   - Validate latency and throughput
   - Run load tests before production

3. **Monitoring**
   - Set up CloudWatch/monitoring
   - Track latency, throughput, errors
   - Alert on anomalies

4. **Rollout Strategy**
   - Use canary deployments
   - Implement A/B testing
   - Have rollback plan ready

## References

- [Databricks Model Serving](https://docs.databricks.com/machine-learning/model-serving/index.html)
