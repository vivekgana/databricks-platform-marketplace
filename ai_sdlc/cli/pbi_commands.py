"""
CLI Commands for PBI Generation

Generate Azure DevOps Product Backlog Items (PBIs) from requirements.

Usage:
    python -m ai_sdlc.cli.pbi_commands generate-pbis REQ-101.md
    python -m ai_sdlc.cli.pbi_commands generate-pbis REQ-101.md --type enabler
    python -m ai_sdlc.cli.pbi_commands generate-pbis REQ-101.md --with-tasks
    python -m ai_sdlc.cli.pbi_commands batch-generate requirements/
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_sdlc.generators.pbi_generator import PBIGenerator, PBIType
from ai_sdlc.parsers.requirement_parser import RequirementParser
from plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import (
    AzureDevOpsPlugin,
)
from plugins.databricks_devops_integrations.sdk.base_plugin import PluginConfig


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def load_ado_config() -> PluginConfig:
    """Load Azure DevOps configuration from environment variables."""
    ado_org_url = os.getenv("AZURE_DEVOPS_ORG_URL")
    ado_pat = os.getenv("AZURE_DEVOPS_PAT")
    ado_project = os.getenv("AZURE_DEVOPS_PROJECT")

    if not all([ado_org_url, ado_pat, ado_project]):
        raise ValueError(
            "Missing Azure DevOps configuration. Set AZURE_DEVOPS_ORG_URL, AZURE_DEVOPS_PAT, and AZURE_DEVOPS_PROJECT environment variables."
        )

    # Extract organization from URL
    org = ado_org_url.split("/")[-1]

    return PluginConfig(
        api_endpoint=ado_org_url,
        api_key=ado_pat,
        organization=org,
        project=ado_project,
    )


def cmd_generate_pbis(args):
    """Generate PBIs from requirement file."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_ado_config()

        # Initialize components
        ado_plugin = AzureDevOpsPlugin()
        ado_plugin.authenticate(config)

        req_parser = RequirementParser()
        pbi_generator = PBIGenerator(ado_plugin, config)

        # Parse requirement
        requirement = req_parser.parse_file(args.requirement_file)
        logger.info(f"Parsed requirement: {requirement.req_id}")

        # Determine PBI type
        if args.type:
            pbi_type = PBIType.ENABLER if args.type == "enabler" else PBIType.FEATURE
            auto_detect = False
        else:
            pbi_type = PBIType.FEATURE
            auto_detect = True

        # Generate PBIs
        print(f"\n🔧 Generating PBIs for {requirement.req_id}...\n")
        results = pbi_generator.generate_from_requirement(
            requirement, pbi_type=pbi_type, auto_detect=auto_detect
        )

        # Display results
        for result in results:
            if result.success:
                print(f"✅ Created {result.pbi_type.value} PBI:")
                print(f"   ID: {result.work_item_id}")
                print(f"   Title: {result.title}")
                print(f"   URL: {result.work_item_url}")

                # Generate child tasks if requested
                if args.with_tasks:
                    print(f"\n   📋 Generating child tasks...")
                    task_ids = pbi_generator.generate_child_tasks(
                        result.work_item_id, requirement
                    )
                    print(f"   ✅ Created {len(task_ids)} tasks")
                    for task_id in task_ids:
                        task_url = f"https://dev.azure.com/{config.organization}/{config.project}/_workitems/edit/{task_id}"
                        print(f"      - Task {task_id}: {task_url}")

                print("")
            else:
                print(f"❌ Failed to create {result.pbi_type.value} PBI:")
                print(f"   Title: {result.title}")
                print(f"   Error: {result.error_message}")
                print("")

        # Summary
        success_count = sum(1 for r in results if r.success)
        print(f"\n📊 Summary: {success_count}/{len(results)} PBIs created successfully")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_batch_generate(args):
    """Generate PBIs from all requirements in a directory."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_ado_config()

        # Initialize components
        ado_plugin = AzureDevOpsPlugin()
        ado_plugin.authenticate(config)

        req_parser = RequirementParser()
        pbi_generator = PBIGenerator(ado_plugin, config)

        # Find all requirement files
        req_dir = Path(args.requirements_dir)
        req_files = list(req_dir.glob("REQ-*.md"))

        if not req_files:
            print(f"❌ No REQ-*.md files found in {req_dir}")
            sys.exit(1)

        print(f"\n🔧 Found {len(req_files)} requirement files\n")

        all_results = []

        # Process each requirement
        for req_file in req_files:
            try:
                # Parse requirement
                requirement = req_parser.parse_file(str(req_file))
                print(f"📄 Processing {requirement.req_id}: {requirement.title}")

                # Generate PBIs
                results = pbi_generator.generate_from_requirement(
                    requirement, auto_detect=True
                )

                for result in results:
                    all_results.append((requirement.req_id, result))

                    if result.success:
                        print(
                            f"   ✅ Created {result.pbi_type.value} PBI {result.work_item_id}"
                        )

                        # Generate child tasks if requested
                        if args.with_tasks:
                            task_ids = pbi_generator.generate_child_tasks(
                                result.work_item_id, requirement
                            )
                            print(f"      📋 Created {len(task_ids)} tasks")
                    else:
                        print(f"   ❌ Failed: {result.error_message}")

                print("")

            except Exception as e:
                logger.error(f"Failed to process {req_file}: {e}")
                print(f"   ❌ Error: {e}\n")

        # Summary
        success_count = sum(1 for _, r in all_results if r.success)
        print(f"\n📊 Summary: {success_count}/{len(all_results)} PBIs created")

        # Output report if requested
        if args.output:
            _write_report(args.output, all_results, config)
            print(f"📝 Report written to: {args.output}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_generate_enabler(args):
    """Generate Enabler PBI with custom specification."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_ado_config()

        # Initialize components
        ado_plugin = AzureDevOpsPlugin()
        ado_plugin.authenticate(config)

        pbi_generator = PBIGenerator(ado_plugin, config)

        # Create EnablerPBI from arguments
        from ai_sdlc.generators.pbi_generator import EnablerPBI
        from plugins.databricks_devops_integrations.sdk.base_plugin import (
            WorkItemPriority,
        )

        enabler = EnablerPBI(
            title=args.title,
            description=args.description or "",
            technical_details=args.technical_details or "",
            acceptance_criteria=(
                args.acceptance_criteria.split(";") if args.acceptance_criteria else []
            ),
            dependencies=args.dependencies.split(";") if args.dependencies else [],
            affected_components=(
                args.components.split(";") if args.components else []
            ),
            story_points=args.story_points or 5.0,
            priority=_parse_priority(args.priority),
            tags=args.tags.split(",") if args.tags else [],
        )

        # Generate PBI
        print(f"\n🔧 Creating Enabler PBI...\n")
        result = pbi_generator.generate_enabler_pbi(enabler)

        if result.success:
            print(f"✅ Created Enabler PBI:")
            print(f"   ID: {result.work_item_id}")
            print(f"   Title: {result.title}")
            print(f"   URL: {result.work_item_url}")
        else:
            print(f"❌ Failed to create Enabler PBI:")
            print(f"   Error: {result.error_message}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_generate_feature(args):
    """Generate Feature PBI with custom specification."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_ado_config()

        # Initialize components
        ado_plugin = AzureDevOpsPlugin()
        ado_plugin.authenticate(config)

        pbi_generator = PBIGenerator(ado_plugin, config)

        # Create FeaturePBI from arguments
        from ai_sdlc.generators.pbi_generator import FeaturePBI
        from plugins.databricks_devops_integrations.sdk.base_plugin import (
            WorkItemPriority,
        )

        feature = FeaturePBI(
            title=args.title,
            description=args.description or "",
            user_story=args.user_story or "",
            acceptance_criteria=(
                args.acceptance_criteria.split(";") if args.acceptance_criteria else []
            ),
            business_value=args.business_value or "",
            user_personas=args.personas.split(",") if args.personas else [],
            dependencies=args.dependencies.split(";") if args.dependencies else [],
            story_points=args.story_points or 5.0,
            priority=_parse_priority(args.priority),
            tags=args.tags.split(",") if args.tags else [],
        )

        # Generate PBI
        print(f"\n🔧 Creating Feature PBI...\n")
        result = pbi_generator.generate_feature_pbi(feature)

        if result.success:
            print(f"✅ Created Feature PBI:")
            print(f"   ID: {result.work_item_id}")
            print(f"   Title: {result.title}")
            print(f"   URL: {result.work_item_url}")
        else:
            print(f"❌ Failed to create Feature PBI:")
            print(f"   Error: {result.error_message}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def _parse_priority(priority_str: str):
    """Parse priority string to WorkItemPriority."""
    from plugins.databricks_devops_integrations.sdk.base_plugin import (
        WorkItemPriority,
    )

    mapping = {
        "critical": WorkItemPriority.CRITICAL,
        "high": WorkItemPriority.HIGH,
        "medium": WorkItemPriority.MEDIUM,
        "low": WorkItemPriority.LOW,
    }
    return mapping.get(priority_str.lower(), WorkItemPriority.MEDIUM)


def _write_report(output_path: str, results, config):
    """Write PBI generation report to file."""
    with open(output_path, "w") as f:
        f.write("# PBI Generation Report\n\n")
        f.write(f"**Project:** {config.project}\n")
        f.write(f"**Organization:** {config.organization}\n\n")
        f.write(f"**Total PBIs:** {len(results)}\n")
        f.write(
            f"**Successful:** {sum(1 for _, r in results if r.success)}\n"
        )
        f.write(
            f"**Failed:** {sum(1 for _, r in results if not r.success)}\n\n"
        )

        f.write("## Created PBIs\n\n")
        for req_id, result in results:
            if result.success:
                f.write(f"### {req_id} - {result.title}\n\n")
                f.write(f"- **Type:** {result.pbi_type.value}\n")
                f.write(f"- **Work Item ID:** {result.work_item_id}\n")
                f.write(f"- **URL:** [{result.work_item_id}]({result.work_item_url})\n\n")

        if any(not r.success for _, r in results):
            f.write("## Failed PBIs\n\n")
            for req_id, result in results:
                if not result.success:
                    f.write(f"### {req_id} - {result.title}\n\n")
                    f.write(f"- **Error:** {result.error_message}\n\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="PBI Generation CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Generate PBIs from requirement
    gen_parser = subparsers.add_parser(
        "generate-pbis", help="Generate PBIs from requirement file"
    )
    gen_parser.add_argument("requirement_file", help="Path to REQ-*.md file")
    gen_parser.add_argument(
        "--type",
        choices=["enabler", "feature"],
        help="Force specific PBI type (default: auto-detect)",
    )
    gen_parser.add_argument(
        "--with-tasks", action="store_true", help="Generate child tasks from ACs"
    )
    gen_parser.set_defaults(func=cmd_generate_pbis)

    # Batch generate
    batch_parser = subparsers.add_parser(
        "batch-generate", help="Generate PBIs from all requirements in directory"
    )
    batch_parser.add_argument("requirements_dir", help="Path to requirements directory")
    batch_parser.add_argument(
        "--with-tasks", action="store_true", help="Generate child tasks from ACs"
    )
    batch_parser.add_argument("--output", help="Output report file path")
    batch_parser.set_defaults(func=cmd_batch_generate)

    # Generate enabler
    enabler_parser = subparsers.add_parser(
        "generate-enabler", help="Generate Enabler PBI"
    )
    enabler_parser.add_argument("--title", required=True, help="Enabler title")
    enabler_parser.add_argument("--description", help="Enabler description")
    enabler_parser.add_argument("--technical-details", help="Technical details")
    enabler_parser.add_argument(
        "--acceptance-criteria", help="Acceptance criteria (semicolon-separated)"
    )
    enabler_parser.add_argument(
        "--dependencies", help="Dependencies (semicolon-separated)"
    )
    enabler_parser.add_argument("--components", help="Affected components (semicolon-separated)")
    enabler_parser.add_argument(
        "--story-points", type=float, help="Story points (default: 5.0)"
    )
    enabler_parser.add_argument(
        "--priority",
        choices=["critical", "high", "medium", "low"],
        default="medium",
        help="Priority",
    )
    enabler_parser.add_argument("--tags", help="Tags (comma-separated)")
    enabler_parser.set_defaults(func=cmd_generate_enabler)

    # Generate feature
    feature_parser = subparsers.add_parser(
        "generate-feature", help="Generate Feature PBI"
    )
    feature_parser.add_argument("--title", required=True, help="Feature title")
    feature_parser.add_argument("--description", help="Feature description")
    feature_parser.add_argument("--user-story", help="User story")
    feature_parser.add_argument(
        "--acceptance-criteria", help="Acceptance criteria (semicolon-separated)"
    )
    feature_parser.add_argument("--business-value", help="Business value")
    feature_parser.add_argument("--personas", help="User personas (comma-separated)")
    feature_parser.add_argument(
        "--dependencies", help="Dependencies (semicolon-separated)"
    )
    feature_parser.add_argument(
        "--story-points", type=float, help="Story points (default: 5.0)"
    )
    feature_parser.add_argument(
        "--priority",
        choices=["critical", "high", "medium", "low"],
        default="medium",
        help="Priority",
    )
    feature_parser.add_argument("--tags", help="Tags (comma-separated)")
    feature_parser.set_defaults(func=cmd_generate_feature)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
