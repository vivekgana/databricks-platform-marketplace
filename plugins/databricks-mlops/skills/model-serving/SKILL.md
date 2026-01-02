# Model Serving Skill

**Last Updated:** 2026-01-01 22:45:49
**Version:** 1.0.0

## Overview

Master model deployment strategies using Databricks Model Serving with auto-scaling, A/B testing, and performance optimization.

## Key Patterns

### Pattern 1: Basic Endpoint Deployment

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ServedModelInput, EndpointCoreConfigInput

w = WorkspaceClient()

served_model = ServedModelInput(
    model_name="catalog.schema.model",
    model_version="1",
    workload_size="Small",
    scale_to_zero_enabled=True
)

endpoint = w.serving_endpoints.create(
    name="my_endpoint",
    config=EndpointCoreConfigInput(served_models=[served_model])
)
```

### Pattern 2: A/B Testing

```python
# Deploy two model versions
served_models = [
    ServedModelInput(
        model_name="catalog.schema.model",
        model_version="1",
        workload_size="Small",
        traffic_percentage=90
    ),
    ServedModelInput(
        model_name="catalog.schema.model",
        model_version="2",
        workload_size="Small",
        traffic_percentage=10
    )
]

w.serving_endpoints.update_config(
    name="my_endpoint",
    served_models=served_models
)
```

### Pattern 3: Endpoint Testing

```python
import requests

def test_endpoint(endpoint_name: str, data: dict):
    """Test serving endpoint"""
    url = f"{w.config.host}/serving-endpoints/{endpoint_name}/invocations"

    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {w.config.token}"},
        json=data
    )

    return response.json()
```

## Best Practices

1. Start with small workload size
2. Enable scale-to-zero for cost savings
3. Test thoroughly before production
4. Implement gradual rollouts
5. Monitor latency and throughput
6. Have rollback plan ready

## References

- [Model Serving Documentation](https://docs.databricks.com/machine-learning/model-serving/)
