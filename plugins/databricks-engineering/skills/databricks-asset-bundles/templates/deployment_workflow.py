"""
Deployment Workflow Utilities
"""
import subprocess
import json
from typing import Dict, Any


class BundleDeployer:
    """Deploy Databricks Asset Bundles."""

    def __init__(self, bundle_path: str):
        self.bundle_path = bundle_path

    def validate(self, target: str) -> bool:
        """Validate bundle configuration."""
        result = subprocess.run(
            ["databricks", "bundle", "validate", "-t", target],
            cwd=self.bundle_path,
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    def deploy(self, target: str) -> Dict[str, Any]:
        """Deploy bundle to target environment."""
        # Validate first
        if not self.validate(target):
            raise ValueError(f"Bundle validation failed for {target}")

        # Deploy
        result = subprocess.run(
            ["databricks", "bundle", "deploy", "-t", target],
            cwd=self.bundle_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Deployment failed: {result.stderr}")

        return {
            "status": "success",
            "target": target,
            "output": result.stdout
        }
