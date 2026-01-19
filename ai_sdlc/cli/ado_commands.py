"""
CLI Commands for Azure DevOps <-> Requirement Integration

Usage:
    python -m ai_sdlc.cli.ado_commands link-requirement REQ-101.md
    python -m ai_sdlc.cli.ado_commands sync-to-ado REQ-101.md
    python -m ai_sdlc.cli.ado_commands sync-from-ado REQ-101.md
    python -m ai_sdlc.cli.ado_commands validate-link REQ-101.md
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_sdlc.integrations.ado_requirement_sync import ADORequirementSync, ADOWorkItemReference
from ai_sdlc.parsers.requirement_parser import RequirementParser
from plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import AzureDevOpsPlugin
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
    # URL format: https://dev.azure.com/your-organization
    org = ado_org_url.split("/")[-1]

    return PluginConfig(
        api_endpoint=ado_org_url,
        api_key=ado_pat,
        organization=org,
        project=ado_project,
    )


def cmd_link_requirement(args):
    """Link requirement file to Azure DevOps work item."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_ado_config()

        # Initialize components
        ado_plugin = AzureDevOpsPlugin()
        ado_plugin.authenticate(config)

        req_parser = RequirementParser()
        sync = ADORequirementSync(ado_plugin, config, req_parser)

        # Parse requirement
        requirement = req_parser.parse_file(args.requirement_file)
        logger.info(f"Parsed requirement: {requirement.req_id}")

        # Link to ADO
        ado_url = sync.link_requirement_to_ado(
            requirement, create_if_missing=args.create
        )

        if ado_url:
            print(f"✅ Requirement {requirement.req_id} linked to ADO:")
            print(f"   {ado_url}")

            # Suggest updating requirement file
            if not requirement.ado_link:
                print(f"\n💡 Add this to your requirement frontmatter:")
                print(f"   ado: {ado_url}")
        else:
            print(f"❌ Failed to link requirement {requirement.req_id}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_sync_to_ado(args):
    """Sync requirement changes to Azure DevOps work item."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_ado_config()

        # Initialize components
        ado_plugin = AzureDevOpsPlugin()
        ado_plugin.authenticate(config)

        req_parser = RequirementParser()
        sync = ADORequirementSync(ado_plugin, config, req_parser)

        # Parse requirement
        requirement = req_parser.parse_file(args.requirement_file)
        logger.info(f"Parsed requirement: {requirement.req_id}")

        # Check for ADO link
        if not requirement.ado_link:
            print(f"❌ Requirement {requirement.req_id} has no ADO link")
            print(f"   Run 'link-requirement' command first")
            sys.exit(1)

        # Sync to ADO
        success = sync.sync_requirement_to_ado(requirement, requirement.ado_link)

        if success:
            print(f"✅ Synced requirement {requirement.req_id} to ADO")
            print(f"   {requirement.ado_link}")
        else:
            print(f"❌ Failed to sync requirement {requirement.req_id}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_sync_from_ado(args):
    """Sync Azure DevOps work item changes back to requirement."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_ado_config()

        # Initialize components
        ado_plugin = AzureDevOpsPlugin()
        ado_plugin.authenticate(config)

        req_parser = RequirementParser()
        sync = ADORequirementSync(ado_plugin, config, req_parser)

        # Parse requirement
        requirement = req_parser.parse_file(args.requirement_file)
        logger.info(f"Parsed requirement: {requirement.req_id}")

        # Check for ADO link
        if not requirement.ado_link:
            print(f"❌ Requirement {requirement.req_id} has no ADO link")
            sys.exit(1)

        # Sync from ADO
        changes = sync.sync_ado_to_requirement(
            requirement.ado_link, Path(args.requirement_file)
        )

        if changes:
            print(f"📥 Changes detected from ADO:")
            for field, change in changes.items():
                print(f"   {field}: {change['old']} → {change['new']}")

            if args.apply:
                print(f"\n⚠️  Auto-apply not yet implemented")
                print(f"   Please manually update {args.requirement_file}")
            else:
                print(f"\n💡 To apply changes, add --apply flag")
        else:
            print(f"✅ No changes detected from ADO")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_validate_link(args):
    """Validate ADO link in requirement file."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_ado_config()

        # Initialize components
        ado_plugin = AzureDevOpsPlugin()
        ado_plugin.authenticate(config)

        req_parser = RequirementParser()
        sync = ADORequirementSync(ado_plugin, config, req_parser)

        # Parse requirement
        requirement = req_parser.parse_file(args.requirement_file)
        logger.info(f"Parsed requirement: {requirement.req_id}")

        # Check for ADO link
        if not requirement.ado_link:
            print(f"❌ Requirement {requirement.req_id} has no ADO link")
            sys.exit(1)

        # Validate link
        is_valid, error_message = sync.validate_ado_link(requirement.ado_link)

        if is_valid:
            print(f"✅ ADO link is valid:")
            print(f"   {requirement.ado_link}")

            # Parse and show details
            ado_ref = ADOWorkItemReference.parse_url(requirement.ado_link)
            if ado_ref:
                print(f"\n📋 Work Item Details:")
                print(f"   Organization: {ado_ref.organization}")
                print(f"   Project: {ado_ref.project}")
                print(f"   Work Item ID: {ado_ref.work_item_id}")

                # Get work item details
                work_item = ado_plugin.get_work_item(ado_ref.work_item_id, config)
                print(f"   Title: {work_item.title}")
                print(f"   Status: {work_item.status.value}")
                print(f"   Assignee: {work_item.assignee or 'Unassigned'}")
        else:
            print(f"❌ ADO link is invalid:")
            print(f"   {error_message}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_search_by_requirement(args):
    """Search for ADO work item by requirement ID."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_ado_config()

        # Initialize components
        ado_plugin = AzureDevOpsPlugin()
        ado_plugin.authenticate(config)

        sync = ADORequirementSync(ado_plugin, config)

        # Search for work item
        work_item = sync.search_ado_by_requirement_id(args.requirement_id)

        if work_item:
            print(f"✅ Found ADO work item for {args.requirement_id}:")
            print(f"   ID: {work_item.id}")
            print(f"   Title: {work_item.title}")
            print(f"   Status: {work_item.status.value}")
            print(f"   Assignee: {work_item.assignee or 'Unassigned'}")
            print(f"   URL: {work_item.url}")
        else:
            print(f"❌ No ADO work item found for {args.requirement_id}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Azure DevOps <-> Requirement Integration CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Link requirement command
    link_parser = subparsers.add_parser(
        "link-requirement", help="Link requirement file to ADO work item"
    )
    link_parser.add_argument("requirement_file", help="Path to REQ-*.md file")
    link_parser.add_argument(
        "--create",
        action="store_true",
        help="Create ADO work item if ado_link is missing",
    )
    link_parser.set_defaults(func=cmd_link_requirement)

    # Sync to ADO command
    sync_to_parser = subparsers.add_parser(
        "sync-to-ado", help="Sync requirement changes to ADO"
    )
    sync_to_parser.add_argument("requirement_file", help="Path to REQ-*.md file")
    sync_to_parser.set_defaults(func=cmd_sync_to_ado)

    # Sync from ADO command
    sync_from_parser = subparsers.add_parser(
        "sync-from-ado", help="Sync ADO changes back to requirement"
    )
    sync_from_parser.add_argument("requirement_file", help="Path to REQ-*.md file")
    sync_from_parser.add_argument(
        "--apply", action="store_true", help="Apply changes to requirement file"
    )
    sync_from_parser.set_defaults(func=cmd_sync_from_ado)

    # Validate link command
    validate_parser = subparsers.add_parser(
        "validate-link", help="Validate ADO link in requirement"
    )
    validate_parser.add_argument("requirement_file", help="Path to REQ-*.md file")
    validate_parser.set_defaults(func=cmd_validate_link)

    # Search by requirement ID command
    search_parser = subparsers.add_parser(
        "search", help="Search for ADO work item by requirement ID"
    )
    search_parser.add_argument("requirement_id", help="Requirement ID (e.g., REQ-101)")
    search_parser.set_defaults(func=cmd_search_by_requirement)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
