"""
Databricks Job Design Agent

Generates optimized Databricks job configurations from requirements.
Supports multiple task types, cluster configurations, and workflow orchestration.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent


class DatabricksJobDesignAgent(BaseAgent):
    """
    Agent for designing Databricks job configurations.

    Generates job definitions including:
    - Task configurations (notebook, jar, python, sql)
    - Cluster specifications with auto-scaling
    - Workflow dependencies and orchestration
    - Best practices for cost and performance
    """

    # Cluster presets for common workloads
    CLUSTER_PRESETS = {
        "small": {
            "node_type_id": "Standard_DS3_v2",
            "num_workers": 2,
            "autoscale": {"min_workers": 1, "max_workers": 4},
            "spark_version": "13.3.x-scala2.12",
        },
        "medium": {
            "node_type_id": "Standard_DS4_v2",
            "num_workers": 4,
            "autoscale": {"min_workers": 2, "max_workers": 8},
            "spark_version": "13.3.x-scala2.12",
        },
        "large": {
            "node_type_id": "Standard_DS5_v2",
            "num_workers": 8,
            "autoscale": {"min_workers": 4, "max_workers": 16},
            "spark_version": "13.3.x-scala2.12",
        },
        "xlarge": {
            "node_type_id": "Standard_E8s_v3",
            "num_workers": 16,
            "autoscale": {"min_workers": 8, "max_workers": 32},
            "spark_version": "13.3.x-scala2.12",
        },
    }

    # Task type templates
    TASK_TEMPLATES = {
        "notebook": {
            "notebook_task": {
                "notebook_path": "",
                "source": "WORKSPACE",
                "base_parameters": {},
            }
        },
        "python": {
            "python_wheel_task": {
                "package_name": "",
                "entry_point": "",
                "parameters": [],
            }
        },
        "jar": {"spark_jar_task": {"main_class_name": "", "parameters": []}},
        "sql": {"sql_task": {"query": {"query_id": ""}, "warehouse_id": ""}},
        "dlt": {"pipeline_task": {"pipeline_id": ""}},
    }

    def execute(
        self, input_data: Dict[str, Any], timeout_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate Databricks job configuration.

        Args:
            input_data: Dictionary with:
                - job_name: Name of the job
                - job_description: Description of the job
                - tasks: List of task definitions
                - cluster_size: Cluster preset (small, medium, large, xlarge)
                - schedule: Optional schedule configuration
                - notification_emails: Optional list of emails for notifications
                - max_concurrent_runs: Maximum concurrent runs (default: 1)
                - timeout_seconds: Job timeout in seconds (default: 0 = no timeout)

        Returns:
            Result dictionary with job configuration
        """
        self._log_start()

        try:
            job_name = input_data.get("job_name")
            job_description = input_data.get("job_description", "")
            tasks = input_data.get("tasks", [])
            cluster_size = input_data.get("cluster_size", "medium")
            schedule = input_data.get("schedule")
            notification_emails = input_data.get("notification_emails", [])
            max_concurrent_runs = input_data.get("max_concurrent_runs", 1)
            job_timeout = input_data.get("timeout_seconds", 0)

            if not job_name:
                return self._create_result(
                    success=False,
                    error_message="Job name is required",
                )

            if not tasks:
                return self._create_result(
                    success=False,
                    error_message="At least one task is required",
                )

            # Validate cluster size
            if cluster_size not in self.CLUSTER_PRESETS:
                return self._create_result(
                    success=False,
                    error_message=f"Invalid cluster size: {cluster_size}. Must be one of: {', '.join(self.CLUSTER_PRESETS.keys())}",
                )

            # Generate job configuration
            job_config = self._generate_job_config(
                job_name=job_name,
                job_description=job_description,
                tasks=tasks,
                cluster_size=cluster_size,
                schedule=schedule,
                notification_emails=notification_emails,
                max_concurrent_runs=max_concurrent_runs,
                job_timeout=job_timeout,
            )

            # Validate configuration
            validation_result = self._validate_job_config(job_config)
            if not validation_result["valid"]:
                return self._create_result(
                    success=False,
                    error_message=f"Job configuration validation failed: {validation_result['errors']}",
                )

            # Generate documentation
            job_doc = self._generate_job_documentation(job_config, tasks)
            job_doc_file = self._save_evidence_file(
                f"job-{job_name.lower().replace(' ', '-')}-design.md", job_doc
            )

            # Save job configuration
            job_config_json = json.dumps(job_config, indent=2)
            job_config_file = self._save_evidence_file(
                f"job-{job_name.lower().replace(' ', '-')}-config.json",
                job_config_json,
            )

            evidence_paths = [job_doc_file, job_config_file]

            self._log_complete(True)

            return self._create_result(
                success=True,
                data={
                    "job_name": job_name,
                    "job_config": job_config,
                    "task_count": len(tasks),
                    "cluster_size": cluster_size,
                    "has_schedule": schedule is not None,
                    "max_concurrent_runs": max_concurrent_runs,
                    "validation": validation_result,
                    "config_file": job_config_file,
                    "doc_file": job_doc_file,
                },
                evidence_paths=evidence_paths,
            )

        except Exception as e:
            self.logger.error(f"Error generating job configuration: {e}")
            return self._create_result(
                success=False,
                error_message=f"Job design failed: {e}",
            )

    def _generate_job_config(
        self,
        job_name: str,
        job_description: str,
        tasks: List[Dict[str, Any]],
        cluster_size: str,
        schedule: Optional[Dict[str, Any]],
        notification_emails: List[str],
        max_concurrent_runs: int,
        job_timeout: int,
    ) -> Dict[str, Any]:
        """Generate complete job configuration."""
        # Base job configuration
        job_config = {
            "name": job_name,
            "description": job_description,
            "max_concurrent_runs": max_concurrent_runs,
            "timeout_seconds": job_timeout,
            "email_notifications": {},
            "notification_settings": {
                "no_alert_for_skipped_runs": False,
                "no_alert_for_canceled_runs": False,
            },
            "tasks": [],
            "format": "MULTI_TASK",
        }

        # Add email notifications
        if notification_emails:
            job_config["email_notifications"] = {
                "on_start": notification_emails,
                "on_success": notification_emails,
                "on_failure": notification_emails,
            }

        # Add schedule if provided
        if schedule:
            job_config["schedule"] = schedule

        # Generate tasks
        for idx, task_spec in enumerate(tasks):
            task_config = self._generate_task_config(
                task_spec, cluster_size, idx, tasks
            )
            job_config["tasks"].append(task_config)

        return job_config

    def _generate_task_config(
        self,
        task_spec: Dict[str, Any],
        cluster_size: str,
        task_idx: int,
        all_tasks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate configuration for a single task."""
        task_name = task_spec.get("task_name", f"task_{task_idx + 1}")
        task_type = task_spec.get("task_type", "notebook")
        task_description = task_spec.get("description", "")
        depends_on = task_spec.get("depends_on", [])
        max_retries = task_spec.get("max_retries", 2)
        timeout_seconds = task_spec.get("timeout_seconds", 0)

        # Base task configuration
        task_config = {
            "task_key": task_name,
            "description": task_description,
            "timeout_seconds": timeout_seconds,
            "max_retries": max_retries,
            "min_retry_interval_millis": 2000,
            "retry_on_timeout": True,
        }

        # Add task-specific configuration
        if task_type not in self.TASK_TEMPLATES:
            task_type = "notebook"  # Default to notebook

        task_config.update(self._get_task_type_config(task_spec, task_type))

        # Add cluster configuration
        task_config.update(self._get_cluster_config(task_spec, cluster_size))

        # Add dependencies
        if depends_on:
            task_config["depends_on"] = [{"task_key": dep} for dep in depends_on]

        return task_config

    def _get_task_type_config(
        self, task_spec: Dict[str, Any], task_type: str
    ) -> Dict[str, Any]:
        """Get task type specific configuration."""
        config = {}

        if task_type == "notebook":
            config["notebook_task"] = {
                "notebook_path": task_spec.get("notebook_path", ""),
                "source": "WORKSPACE",
                "base_parameters": task_spec.get("parameters", {}),
            }

        elif task_type == "python":
            config["python_wheel_task"] = {
                "package_name": task_spec.get("package_name", ""),
                "entry_point": task_spec.get("entry_point", ""),
                "parameters": task_spec.get("parameters", []),
            }

        elif task_type == "jar":
            config["spark_jar_task"] = {
                "main_class_name": task_spec.get("main_class_name", ""),
                "parameters": task_spec.get("parameters", []),
            }

        elif task_type == "sql":
            config["sql_task"] = {
                "query": {"query_id": task_spec.get("query_id", "")},
                "warehouse_id": task_spec.get("warehouse_id", ""),
            }

        elif task_type == "dlt":
            config["pipeline_task"] = {"pipeline_id": task_spec.get("pipeline_id", "")}

        return config

    def _get_cluster_config(
        self, task_spec: Dict[str, Any], cluster_size: str
    ) -> Dict[str, Any]:
        """Get cluster configuration for task."""
        # Check if task specifies a job cluster or uses existing cluster
        if "existing_cluster_id" in task_spec:
            return {"existing_cluster_id": task_spec["existing_cluster_id"]}

        # Use new job cluster with preset
        cluster_preset = self.CLUSTER_PRESETS[cluster_size].copy()

        # Add spot instance policy for cost savings
        cluster_preset["aws_attributes"] = {
            "availability": "SPOT_WITH_FALLBACK",
            "zone_id": "auto",
            "spot_bid_price_percent": 100,
            "ebs_volume_type": "GENERAL_PURPOSE_SSD",
            "ebs_volume_count": 1,
            "ebs_volume_size": 100,
        }

        # Add runtime engine
        cluster_preset["runtime_engine"] = "PHOTON"

        # Add init scripts if provided
        if "init_scripts" in task_spec:
            cluster_preset["init_scripts"] = task_spec["init_scripts"]

        # Add spark configuration if provided
        if "spark_conf" in task_spec:
            cluster_preset["spark_conf"] = task_spec["spark_conf"]
        else:
            # Default Spark configuration
            cluster_preset["spark_conf"] = {
                "spark.databricks.delta.preview.enabled": "true",
                "spark.databricks.delta.retentionDurationCheck.enabled": "false",
                "spark.sql.adaptive.enabled": "true",
                "spark.sql.adaptive.coalescePartitions.enabled": "true",
            }

        # Add environment variables if provided
        if "spark_env_vars" in task_spec:
            cluster_preset["spark_env_vars"] = task_spec["spark_env_vars"]

        return {"new_cluster": cluster_preset}

    def _validate_job_config(self, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate job configuration."""
        errors = []
        warnings = []

        # Check job name
        if not job_config.get("name"):
            errors.append("Job name is required")

        # Check tasks
        tasks = job_config.get("tasks", [])
        if not tasks:
            errors.append("At least one task is required")

        # Validate task configurations
        task_keys = set()
        for task in tasks:
            task_key = task.get("task_key")
            if not task_key:
                errors.append("Task key is required for all tasks")
            elif task_key in task_keys:
                errors.append(f"Duplicate task key: {task_key}")
            else:
                task_keys.add(task_key)

            # Validate dependencies
            depends_on = task.get("depends_on", [])
            for dep in depends_on:
                dep_key = dep.get("task_key")
                if dep_key not in task_keys:
                    warnings.append(
                        f"Task {task_key} depends on {dep_key} which appears later or doesn't exist"
                    )

            # Validate task type
            has_task_type = any(
                key in task
                for key in [
                    "notebook_task",
                    "python_wheel_task",
                    "spark_jar_task",
                    "sql_task",
                    "pipeline_task",
                ]
            )
            if not has_task_type:
                errors.append(f"Task {task_key} must have a task type configuration")

            # Validate cluster configuration
            has_cluster = "new_cluster" in task or "existing_cluster_id" in task
            if not has_cluster:
                errors.append(f"Task {task_key} must have cluster configuration")

        # Check for circular dependencies
        if self._has_circular_dependencies(tasks):
            errors.append("Circular dependencies detected in task workflow")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _has_circular_dependencies(self, tasks: List[Dict[str, Any]]) -> bool:
        """Check for circular dependencies in task workflow."""
        # Build dependency graph
        graph = {}
        for task in tasks:
            task_key = task.get("task_key")
            depends_on = [dep.get("task_key") for dep in task.get("depends_on", [])]
            graph[task_key] = depends_on

        # DFS to detect cycles
        visited = set()
        rec_stack = set()

        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for task_key in graph:
            if task_key not in visited:
                if has_cycle(task_key):
                    return True

        return False

    def _generate_job_documentation(
        self, job_config: Dict[str, Any], task_specs: List[Dict[str, Any]]
    ) -> str:
        """Generate comprehensive job documentation."""
        doc = f"""# Databricks Job Design: {job_config['name']}

**Work Item ID:** {self.work_item_id}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Job Format:** {job_config.get('format', 'MULTI_TASK')}

---

## Job Overview

**Description:** {job_config.get('description', 'N/A')}

**Configuration:**
- Max Concurrent Runs: {job_config.get('max_concurrent_runs', 1)}
- Timeout: {job_config.get('timeout_seconds', 0)} seconds (0 = no timeout)
- Retry on Timeout: Enabled
- Task Count: {len(job_config.get('tasks', []))}

---

## Schedule

"""

        if "schedule" in job_config:
            schedule = job_config["schedule"]
            doc += f"""**Schedule Type:** {schedule.get('schedule_type', 'N/A')}
**Schedule:** {schedule.get('quartz_cron_expression', 'N/A')}
**Timezone:** {schedule.get('timezone_id', 'UTC')}
**Pause Status:** {'Paused' if schedule.get('pause_status') == 'PAUSED' else 'Active'}

"""
        else:
            doc += "**Manual Trigger Only** - No schedule configured\n\n"

        doc += """---

## Email Notifications

"""

        email_notifications = job_config.get("email_notifications", {})
        if email_notifications:
            doc += f"""**On Start:** {', '.join(email_notifications.get('on_start', []))}
**On Success:** {', '.join(email_notifications.get('on_success', []))}
**On Failure:** {', '.join(email_notifications.get('on_failure', []))}

"""
        else:
            doc += "No email notifications configured\n\n"

        doc += """---

## Tasks

"""

        for idx, task in enumerate(job_config.get("tasks", [])):
            task_key = task.get("task_key")
            task_desc = task.get("description", "N/A")
            depends_on = task.get("depends_on", [])
            max_retries = task.get("max_retries", 0)
            timeout = task.get("timeout_seconds", 0)

            # Determine task type
            task_type = "Unknown"
            if "notebook_task" in task:
                task_type = "Notebook"
                task_path = task["notebook_task"].get("notebook_path", "N/A")
            elif "python_wheel_task" in task:
                task_type = "Python Wheel"
                task_path = task["python_wheel_task"].get("package_name", "N/A")
            elif "spark_jar_task" in task:
                task_type = "Spark JAR"
                task_path = task["spark_jar_task"].get("main_class_name", "N/A")
            elif "sql_task" in task:
                task_type = "SQL"
                task_path = task["sql_task"]["query"].get("query_id", "N/A")
            elif "pipeline_task" in task:
                task_type = "DLT Pipeline"
                task_path = task["pipeline_task"].get("pipeline_id", "N/A")
            else:
                task_path = "N/A"

            # Get cluster info
            cluster_info = "Unknown"
            if "new_cluster" in task:
                cluster = task["new_cluster"]
                node_type = cluster.get("node_type_id", "N/A")
                autoscale = cluster.get("autoscale", {})
                if autoscale:
                    cluster_info = f"New Cluster ({node_type}, {autoscale.get('min_workers')}-{autoscale.get('max_workers')} workers)"
                else:
                    num_workers = cluster.get("num_workers", 0)
                    cluster_info = f"New Cluster ({node_type}, {num_workers} workers)"
            elif "existing_cluster_id" in task:
                cluster_info = f"Existing Cluster ({task['existing_cluster_id']})"

            doc += f"""### Task {idx + 1}: {task_key}

**Type:** {task_type}
**Path/Target:** {task_path}
**Description:** {task_desc}

**Configuration:**
- Max Retries: {max_retries}
- Timeout: {timeout} seconds (0 = no timeout)
- Retry on Timeout: {task.get('retry_on_timeout', False)}
- Min Retry Interval: {task.get('min_retry_interval_millis', 0)} ms

**Cluster:** {cluster_info}

"""

            if depends_on:
                doc += f"""**Dependencies:**
"""
                for dep in depends_on:
                    doc += f"- {dep.get('task_key')}\n"
                doc += "\n"

        doc += """---

## Workflow Diagram

```
"""

        # Generate simple workflow diagram
        for task in job_config.get("tasks", []):
            task_key = task.get("task_key")
            depends_on = task.get("depends_on", [])
            if depends_on:
                for dep in depends_on:
                    doc += f"{dep.get('task_key')} → {task_key}\n"
            else:
                doc += f"[START] → {task_key}\n"

        doc += """```

---

## Best Practices Applied

✅ **Auto-scaling enabled** - Clusters scale based on workload
✅ **Spot instances with fallback** - Cost optimization with reliability
✅ **Photon runtime** - Enhanced performance for Spark operations
✅ **Retry logic** - Automatic retries on failure
✅ **Adaptive query execution** - Optimized Spark query plans
✅ **Delta Lake optimizations** - Enhanced Delta table operations
✅ **Email notifications** - Alerts for job status changes

---

## Configuration File

The complete JSON configuration has been saved to the accompanying `-config.json` file.

To create this job in Databricks:

```bash
databricks jobs create --json-file job-config.json
```

---

**Generated by:** AI-SDLC Databricks Job Design Agent
"""

        return doc
