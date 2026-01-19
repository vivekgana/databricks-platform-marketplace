"""
CLI commands for Databricks job design.

Usage:
    python -m ai_sdlc.cli.databricks_job_commands design --job-name "My ETL Job" --tasks tasks.json
    python -m ai_sdlc.cli.databricks_job_commands validate --config job-config.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from ai_sdlc.agents.databricks_job_design_agent import DatabricksJobDesignAgent


def design_job(
    job_name: str,
    job_description: str,
    tasks_file: str,
    cluster_size: str = "medium",
    schedule_cron: Optional[str] = None,
    schedule_timezone: str = "UTC",
    notification_emails: Optional[List[str]] = None,
    max_concurrent_runs: int = 1,
    timeout_seconds: int = 0,
    work_item_id: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> int:
    """
    Design a Databricks job from task specifications.

    Args:
        job_name: Name of the job
        job_description: Description of the job
        tasks_file: Path to JSON file with task definitions
        cluster_size: Cluster preset (small, medium, large, xlarge)
        schedule_cron: Optional cron expression for scheduling
        schedule_timezone: Timezone for schedule (default: UTC)
        notification_emails: Optional list of emails for notifications
        max_concurrent_runs: Maximum concurrent runs (default: 1)
        timeout_seconds: Job timeout in seconds (default: 0 = no timeout)
        work_item_id: Optional work item ID
        output_dir: Output directory for job configuration

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    # Load tasks from file
    try:
        with open(tasks_file, "r") as f:
            tasks = json.load(f)
    except FileNotFoundError:
        print(f"❌ Tasks file not found: {tasks_file}")
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in tasks file: {e}")
        return 1

    # Validate tasks format
    if not isinstance(tasks, list):
        print("❌ Tasks file must contain a JSON array of task definitions")
        return 1

    # Initialize agent
    agent = DatabricksJobDesignAgent(
        work_item_id=work_item_id or "local",
        evidence_base_path=output_dir or "./databricks-job-designs",
    )

    # Build schedule configuration if provided
    schedule = None
    if schedule_cron:
        schedule = {
            "quartz_cron_expression": schedule_cron,
            "timezone_id": schedule_timezone,
            "pause_status": "UNPAUSED",
        }

    # Design job
    print(f"🔧 Designing Databricks job: {job_name}")
    print(f"   Cluster size: {cluster_size}")
    print(f"   Task count: {len(tasks)}")
    print(f"   Max concurrent runs: {max_concurrent_runs}")
    if schedule:
        print(f"   Schedule: {schedule_cron} ({schedule_timezone})")
    print()

    result = agent.execute(
        {
            "job_name": job_name,
            "job_description": job_description,
            "tasks": tasks,
            "cluster_size": cluster_size,
            "schedule": schedule,
            "notification_emails": notification_emails or [],
            "max_concurrent_runs": max_concurrent_runs,
            "timeout_seconds": timeout_seconds,
        }
    )

    if not result["success"]:
        print(f"❌ Job design failed: {result.get('error_message')}")
        return 1

    data = result["data"]

    # Print summary
    print("=" * 70)
    print(f"📊 Job Design Summary")
    print("=" * 70)
    print()
    print(f"Job name:           {data['job_name']}")
    print(f"Task count:         {data['task_count']}")
    print(f"Cluster size:       {data['cluster_size']}")
    print(f"Has schedule:       {'Yes' if data['has_schedule'] else 'No'}")
    print(f"Max concurrent:     {data['max_concurrent_runs']}")
    print()

    # Print validation results
    validation = data["validation"]
    if validation["valid"]:
        print("✅ Configuration validation: PASSED")
    else:
        print("❌ Configuration validation: FAILED")
        print("\nErrors:")
        for error in validation["errors"]:
            print(f"  • {error}")

    if validation["warnings"]:
        print("\n⚠️  Warnings:")
        for warning in validation["warnings"]:
            print(f"  • {warning}")

    print()

    # Print output files
    print(f"📄 Configuration file: {data['config_file']}")
    print(f"📄 Documentation file: {data['doc_file']}")
    print()

    # Print next steps
    print("Next steps:")
    print("1. Review the generated job configuration")
    print("2. Customize cluster settings if needed")
    print("3. Create the job in Databricks:")
    print(f"   databricks jobs create --json-file {data['config_file']}")
    print()

    return 0 if validation["valid"] else 1


def validate_job_config(config_file: str) -> int:
    """
    Validate an existing Databricks job configuration.

    Args:
        config_file: Path to job configuration JSON file

    Returns:
        Exit code (0 = valid, 1 = invalid)
    """
    # Load configuration
    try:
        with open(config_file, "r") as f:
            job_config = json.load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_file}")
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        return 1

    print(f"🔍 Validating job configuration: {config_file}")
    print()

    # Create agent and validate
    agent = DatabricksJobDesignAgent(work_item_id="validation")
    validation_result = agent._validate_job_config(job_config)

    # Print results
    if validation_result["valid"]:
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration validation failed")
        print("\nErrors:")
        for error in validation_result["errors"]:
            print(f"  • {error}")

    if validation_result["warnings"]:
        print("\n⚠️  Warnings:")
        for warning in validation_result["warnings"]:
            print(f"  • {warning}")

    print()
    return 0 if validation_result["valid"] else 1


def generate_sample_tasks(output_file: str, task_count: int = 3) -> int:
    """
    Generate a sample tasks JSON file.

    Args:
        output_file: Path to output JSON file
        task_count: Number of sample tasks to generate

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    sample_tasks = []

    for i in range(task_count):
        task = {
            "task_name": f"task_{i + 1}",
            "task_type": "notebook",
            "description": f"Sample task {i + 1}",
            "notebook_path": f"/Workspace/notebooks/task_{i + 1}",
            "parameters": {"param1": "value1", "param2": "value2"},
            "max_retries": 2,
            "timeout_seconds": 3600,
        }

        # Add dependency for tasks after the first one
        if i > 0:
            task["depends_on"] = [f"task_{i}"]

        sample_tasks.append(task)

    try:
        with open(output_file, "w") as f:
            json.dump(sample_tasks, f, indent=2)
        print(f"✅ Sample tasks file created: {output_file}")
        print(f"   Task count: {task_count}")
        print()
        print("Edit this file to customize tasks, then use:")
        print(
            f'  python -m ai_sdlc.cli.databricks_job_commands design --job-name "My Job" --tasks {output_file}'
        )
        print()
        return 0
    except Exception as e:
        print(f"❌ Failed to create sample file: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Databricks Job Design CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate sample tasks file
  python -m ai_sdlc.cli.databricks_job_commands generate-sample --output tasks.json

  # Design a simple job
  python -m ai_sdlc.cli.databricks_job_commands design \\
    --job-name "ETL Pipeline" \\
    --description "Daily ETL job" \\
    --tasks tasks.json \\
    --cluster-size medium

  # Design a scheduled job with notifications
  python -m ai_sdlc.cli.databricks_job_commands design \\
    --job-name "Daily Report" \\
    --description "Generate daily reports" \\
    --tasks tasks.json \\
    --cluster-size small \\
    --schedule "0 0 2 * * ?" \\
    --timezone "America/New_York" \\
    --emails user1@example.com user2@example.com

  # Validate job configuration
  python -m ai_sdlc.cli.databricks_job_commands validate --config job-config.json

  # Design job with work item ID
  python -m ai_sdlc.cli.databricks_job_commands design \\
    --job-name "Feature Pipeline" \\
    --tasks tasks.json \\
    --work-item-id 6340168
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Design command
    design_parser = subparsers.add_parser("design", help="Design a Databricks job")
    design_parser.add_argument(
        "--job-name",
        required=True,
        help="Name of the job",
    )
    design_parser.add_argument(
        "--description",
        default="",
        help="Description of the job",
    )
    design_parser.add_argument(
        "--tasks",
        required=True,
        help="Path to JSON file with task definitions",
    )
    design_parser.add_argument(
        "--cluster-size",
        choices=["small", "medium", "large", "xlarge"],
        default="medium",
        help="Cluster size preset (default: medium)",
    )
    design_parser.add_argument(
        "--schedule",
        help="Quartz cron expression for scheduling (e.g., '0 0 2 * * ?')",
    )
    design_parser.add_argument(
        "--timezone",
        default="UTC",
        help="Timezone for schedule (default: UTC)",
    )
    design_parser.add_argument(
        "--emails",
        nargs="+",
        help="Email addresses for notifications",
    )
    design_parser.add_argument(
        "--max-concurrent",
        type=int,
        default=1,
        help="Maximum concurrent runs (default: 1)",
    )
    design_parser.add_argument(
        "--timeout",
        type=int,
        default=0,
        help="Job timeout in seconds (default: 0 = no timeout)",
    )
    design_parser.add_argument(
        "--work-item-id",
        help="Work item ID (optional)",
    )
    design_parser.add_argument(
        "--output-dir",
        help="Output directory for job configuration (default: ./databricks-job-designs)",
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate job configuration"
    )
    validate_parser.add_argument(
        "--config",
        required=True,
        help="Path to job configuration JSON file",
    )

    # Generate sample command
    sample_parser = subparsers.add_parser(
        "generate-sample", help="Generate sample tasks file"
    )
    sample_parser.add_argument(
        "--output",
        default="sample-tasks.json",
        help="Output file path (default: sample-tasks.json)",
    )
    sample_parser.add_argument(
        "--count",
        type=int,
        default=3,
        help="Number of sample tasks (default: 3)",
    )

    args = parser.parse_args()

    if args.command == "design":
        exit_code = design_job(
            job_name=args.job_name,
            job_description=args.description,
            tasks_file=args.tasks,
            cluster_size=args.cluster_size,
            schedule_cron=args.schedule,
            schedule_timezone=args.timezone,
            notification_emails=args.emails,
            max_concurrent_runs=args.max_concurrent,
            timeout_seconds=args.timeout,
            work_item_id=args.work_item_id,
            output_dir=args.output_dir,
        )
    elif args.command == "validate":
        exit_code = validate_job_config(config_file=args.config)
    elif args.command == "generate-sample":
        exit_code = generate_sample_tasks(
            output_file=args.output, task_count=args.count
        )
    else:
        parser.print_help()
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
