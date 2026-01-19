"""
CLI Commands for Workflow Orchestration

User-friendly commands to run AI-SDLC workflows.

Usage:
    python -m ai_sdlc.cli.workflow_commands run-workflow <work_item_id>
    python -m ai_sdlc.cli.workflow_commands run-stage <work_item_id> <stage>
    python -m ai_sdlc.cli.workflow_commands validate-stage <work_item_id> <stage>
    python -m ai_sdlc.cli.workflow_commands resume-workflow <work_item_id>
    python -m ai_sdlc.cli.workflow_commands list-work-items
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_sdlc.orchestration import (
    WorkflowOrchestrator,
    StateReader,
    WorkflowStage,
)
from ai_sdlc.evidence import (
    AzureBlobEvidenceStorage,
    LocalFileEvidenceStorage,
    EvidenceFormatter,
)
from plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import (
    AzureDevOpsPlugin,
)
from plugins.databricks_devops_integrations.sdk.base_plugin import PluginConfig


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def load_ado_config() -> PluginConfig:
    """Load Azure DevOps configuration from environment variables."""
    ado_org_url = os.getenv("AZURE_DEVOPS_ORG_URL")
    ado_pat = os.getenv("AZURE_DEVOPS_PAT")
    ado_project = os.getenv("AZURE_DEVOPS_PROJECT")

    if not all([ado_org_url, ado_pat, ado_project]):
        raise ValueError(
            "Missing Azure DevOps configuration. Set AZURE_DEVOPS_ORG_URL, "
            "AZURE_DEVOPS_PAT, and AZURE_DEVOPS_PROJECT environment variables."
        )

    # Extract organization from URL
    org = ado_org_url.split("/")[-1]

    return PluginConfig(
        api_endpoint=ado_org_url,
        api_key=ado_pat,
        organization=org,
        project=ado_project,
    )


def get_evidence_storage(use_azure: bool = True):
    """
    Get evidence storage backend.

    Args:
        use_azure: Use Azure Blob Storage (default) or local filesystem

    Returns:
        Evidence storage instance
    """
    if use_azure:
        return AzureBlobEvidenceStorage(
            container_name=os.getenv("EVIDENCE_CONTAINER", "audit-cortex-evidence")
        )
    else:
        base_path = os.getenv("EVIDENCE_PATH", "./evidence")
        return LocalFileEvidenceStorage(base_path)


def cmd_run_workflow(args):
    """Run complete workflow for a work item."""
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_ado_config()

        # Initialize components
        ado_plugin = AzureDevOpsPlugin()
        ado_plugin.authenticate(config)

        # Determine evidence path
        if args.evidence_path:
            evidence_base_path = args.evidence_path
        elif args.use_local_storage:
            evidence_base_path = "./evidence"
        else:
            evidence_base_path = "azure-blob://audit-cortex-evidence"

        # Initialize orchestrator
        orchestrator = WorkflowOrchestrator(
            ado_plugin=ado_plugin,
            config=config,
            evidence_base_path=evidence_base_path,
            checkpoint_dir=args.checkpoint_dir,
        )

        # Register agents (would be done in production)
        logger.info("Note: Agent implementations need to be registered with orchestrator")

        # Run workflow
        print(f"\n{'=' * 60}")
        print(f"🚀 Starting AI-SDLC Workflow")
        print(f"{'=' * 60}\n")
        print(f"Work Item ID: {args.work_item_id}")
        print(f"Evidence Path: {evidence_base_path}")
        print(f"Stop on Failure: {not args.continue_on_failure}")
        print()

        result = orchestrator.run_workflow(
            work_item_id=args.work_item_id,
            stop_on_failure=not args.continue_on_failure,
        )

        # Display results
        print(f"\n{'=' * 60}")
        print(f"✅ Workflow Complete" if result.all_stages_passed else "⚠️ Workflow Completed with Issues")
        print(f"{'=' * 60}\n")

        print(f"Duration: {result.duration_seconds:.1f}s")
        print(f"Stages Completed: {len(result.stage_results)}")
        print(f"Successful Stages: {len(result.get_successful_stages())}")
        print(f"Failed Stages: {len(result.get_failed_stages())}")
        print()

        if result.error_message:
            print(f"❌ Error: {result.error_message}\n")

        # Show stage results
        print("Stage Results:")
        for stage, stage_result in result.stage_results.items():
            status_icon = "✅" if stage_result.is_success() else "❌"
            print(
                f"  {status_icon} {stage.value}: "
                f"Eval Score: {stage_result.eval_score:.2f}, "
                f"Duration: {stage_result.agent_result.duration_seconds:.1f}s"
            )

        sys.exit(0 if result.all_stages_passed else 1)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_run_stage(args):
    """Run a specific workflow stage."""
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    print(f"Running single stage: {args.stage}")
    print("Note: This command is not yet fully implemented.")
    print("Use run-workflow to execute complete workflow.")


def cmd_validate_stage(args):
    """Validate a workflow stage with evaluations."""
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    print(f"Validating stage: {args.stage}")
    print("Note: This command is not yet fully implemented.")


def cmd_resume_workflow(args):
    """Resume an interrupted workflow."""
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_ado_config()

        # Initialize components
        ado_plugin = AzureDevOpsPlugin()
        ado_plugin.authenticate(config)

        evidence_base_path = args.evidence_path or "azure-blob://audit-cortex-evidence"

        # Initialize orchestrator
        orchestrator = WorkflowOrchestrator(
            ado_plugin=ado_plugin,
            config=config,
            evidence_base_path=evidence_base_path,
            checkpoint_dir=args.checkpoint_dir,
        )

        # Resume workflow
        print(f"\n{'=' * 60}")
        print(f"🔄 Resuming AI-SDLC Workflow")
        print(f"{'=' * 60}\n")
        print(f"Work Item ID: {args.work_item_id}")
        print()

        result = orchestrator.resume_workflow(work_item_id=args.work_item_id)

        if result:
            print(f"\n✅ Workflow resumed and completed")
            sys.exit(0 if result.all_stages_passed else 1)
        else:
            print(f"\n⚠️ No checkpoint found or workflow already complete")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_list_work_items(args):
    """List work items ready for workflow."""
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_ado_config()

        # Initialize components
        ado_plugin = AzureDevOpsPlugin()
        ado_plugin.authenticate(config)

        state_reader = StateReader(ado_plugin, config)

        # Find work items
        print(f"\n{'=' * 60}")
        print(f"📋 Work Items Ready for Workflow")
        print(f"{'=' * 60}\n")

        work_items = state_reader.find_work_items_ready_for_workflow(
            work_item_type=args.type
        )

        if not work_items:
            print("No work items found in ready state.")
            return

        for i, state_info in enumerate(work_items, 1):
            print(f"{i}. {state_info.work_item_type} {state_info.work_item_id}")
            print(f"   Title: {state_info.title}")
            print(f"   State: {state_info.current_ado_state.value}")
            print(f"   Suggested Stage: {state_info.suggested_workflow_stage.value if state_info.suggested_workflow_stage else 'N/A'}")
            print()

        print(f"Total: {len(work_items)} work items\n")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_collect_evidence(args):
    """Collect and upload evidence for a work item."""
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    print(f"Collecting evidence for work item: {args.work_item_id}")
    print("Note: This command is not yet fully implemented.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI-SDLC Workflow Orchestration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global options
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # run-workflow command
    run_workflow_parser = subparsers.add_parser(
        "run-workflow",
        help="Run complete workflow for a work item",
    )
    run_workflow_parser.add_argument(
        "work_item_id",
        help="Work item ID (e.g., 6340168)",
    )
    run_workflow_parser.add_argument(
        "--evidence-path",
        help="Evidence storage path (default: Azure Blob)",
    )
    run_workflow_parser.add_argument(
        "--use-local-storage",
        action="store_true",
        help="Use local filesystem instead of Azure Blob",
    )
    run_workflow_parser.add_argument(
        "--checkpoint-dir",
        default="./.workflow_checkpoints",
        help="Directory for workflow checkpoints",
    )
    run_workflow_parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        help="Continue workflow even if a stage fails",
    )
    run_workflow_parser.set_defaults(func=cmd_run_workflow)

    # run-stage command
    run_stage_parser = subparsers.add_parser(
        "run-stage",
        help="Run a specific workflow stage",
    )
    run_stage_parser.add_argument("work_item_id", help="Work item ID")
    run_stage_parser.add_argument(
        "stage",
        choices=[s.value for s in WorkflowStage],
        help="Stage to run",
    )
    run_stage_parser.add_argument(
        "--evidence-path",
        help="Evidence storage path",
    )
    run_stage_parser.set_defaults(func=cmd_run_stage)

    # validate-stage command
    validate_parser = subparsers.add_parser(
        "validate-stage",
        help="Validate a workflow stage with evaluations",
    )
    validate_parser.add_argument("work_item_id", help="Work item ID")
    validate_parser.add_argument(
        "stage",
        choices=[s.value for s in WorkflowStage],
        help="Stage to validate",
    )
    validate_parser.set_defaults(func=cmd_validate_stage)

    # resume-workflow command
    resume_parser = subparsers.add_parser(
        "resume-workflow",
        help="Resume an interrupted workflow from checkpoint",
    )
    resume_parser.add_argument("work_item_id", help="Work item ID")
    resume_parser.add_argument(
        "--evidence-path",
        help="Evidence storage path",
    )
    resume_parser.add_argument(
        "--checkpoint-dir",
        default="./.workflow_checkpoints",
        help="Directory for workflow checkpoints",
    )
    resume_parser.set_defaults(func=cmd_resume_workflow)

    # list-work-items command
    list_parser = subparsers.add_parser(
        "list-work-items",
        help="List work items ready for workflow",
    )
    list_parser.add_argument(
        "--type",
        choices=["Epic", "Feature", "Enabler", "Product Backlog Item"],
        help="Filter by work item type",
    )
    list_parser.set_defaults(func=cmd_list_work_items)

    # collect-evidence command
    collect_parser = subparsers.add_parser(
        "collect-evidence",
        help="Collect and upload evidence for a work item",
    )
    collect_parser.add_argument("work_item_id", help="Work item ID")
    collect_parser.add_argument(
        "--upload-to-ado",
        action="store_true",
        help="Upload evidence to ADO as attachments",
    )
    collect_parser.set_defaults(func=cmd_collect_evidence)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
