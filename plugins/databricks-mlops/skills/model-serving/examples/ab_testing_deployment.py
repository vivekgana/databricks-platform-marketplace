"""A/B Testing Deployment Example"""

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ServedModelInput

w = WorkspaceClient()

def setup_ab_testing(
    endpoint_name: str,
    model_name: str,
    champion_version: str,
    challenger_version: str,
    challenger_traffic: int = 10
):
    """Setup A/B testing between two model versions"""

    served_models = [
        ServedModelInput(
            model_name=model_name,
            model_version=champion_version,
            workload_size="Small",
            scale_to_zero_enabled=False,
            traffic_percentage=100 - challenger_traffic
        ),
        ServedModelInput(
            model_name=model_name,
            model_version=challenger_version,
            workload_size="Small",
            scale_to_zero_enabled=False,
            traffic_percentage=challenger_traffic
        )
    ]

    w.serving_endpoints.update_config(
        name=endpoint_name,
        served_models=served_models
    )

    print(f"✓ A/B testing configured:")
    print(f"  Champion v{champion_version}: {100-challenger_traffic}%")
    print(f"  Challenger v{challenger_version}: {challenger_traffic}%")
