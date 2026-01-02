"""
Deployment Script for Databricks
"""
import os
import sys
from databricks.sdk import WorkspaceClient
from typing import Dict, Any


class DatabricksDeployer:
    """Deploy artifacts to Databricks workspace."""

    def __init__(self, host: str, token: str):
        self.client = WorkspaceClient(host=host, token=token)

    def deploy_notebooks(self, source_dir: str, target_path: str):
        """Deploy notebooks to workspace."""
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith('.py') or file.endswith('.sql'):
                    local_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_path, source_dir)
                    workspace_path = os.path.join(target_path, relative_path)

                    with open(local_path, 'rb') as f:
                        self.client.workspace.upload(
                            workspace_path,
                            f.read(),
                            overwrite=True
                        )
                    print(f"Deployed: {workspace_path}")

    def run_job(self, job_id: int) -> Dict[str, Any]:
        """Trigger job run."""
        run = self.client.jobs.run_now(job_id=job_id)
        return {
            "run_id": run.run_id,
            "status": "TRIGGERED"
        }


if __name__ == "__main__":
    host = os.getenv("DATABRICKS_HOST")
    token = os.getenv("DATABRICKS_TOKEN")

    deployer = DatabricksDeployer(host, token)
    deployer.deploy_notebooks("./notebooks", "/Shared/production")
