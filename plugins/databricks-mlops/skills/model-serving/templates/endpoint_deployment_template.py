"""Model Serving Endpoint Deployment Template"""

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ServedModelInput, EndpointCoreConfigInput
import requests

w = WorkspaceClient()

def deploy_model_endpoint(
    endpoint_name: str,
    model_name: str,
    model_version: str,
    workload_size: str = "Small"
):
    """Deploy model to serving endpoint"""

    served_model = ServedModelInput(
        model_name=model_name,
        model_version=model_version,
        workload_size=workload_size,
        scale_to_zero_enabled=True
    )

    try:
        # Try to update existing endpoint
        w.serving_endpoints.update_config(
            name=endpoint_name,
            served_models=[served_model]
        )
        print(f"✓ Updated endpoint: {endpoint_name}")
    except:
        # Create new endpoint
        w.serving_endpoints.create(
            name=endpoint_name,
            config=EndpointCoreConfigInput(served_models=[served_model])
        )
        print(f"✓ Created endpoint: {endpoint_name}")

    return endpoint_name

def test_endpoint(endpoint_name: str, test_data: dict):
    """Test deployed endpoint"""

    url = f"{w.config.host}/serving-endpoints/{endpoint_name}/invocations"
    headers = {
        "Authorization": f"Bearer {w.config.token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=test_data)
    return response.json()
