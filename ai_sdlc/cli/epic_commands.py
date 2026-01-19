"""
CLI Commands for Epic/Feature/Enabler Processing

Process ADO Epics, Features, and Enablers to find or generate child PBIs.
Supports importing from wiki design documents.

Usage:
    python -m ai_sdlc.cli.epic_commands process-work-item <ADO_URL>
    python -m ai_sdlc.cli.epic_commands process-wiki <WIKI_URL>
    python -m ai_sdlc.cli.epic_commands generate-from-epic <EPIC_ID>
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_sdlc.generators.epic_feature_generator import EpicFeatureGenerator, WikiReference
from ai_sdlc.generators.pbi_generator import PBIGenerator
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


def cmd_process_work_item(args):
    """Process ADO work item URL and find/generate child PBIs."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_ado_config()

        # Initialize components
        ado_plugin = AzureDevOpsPlugin()
        ado_plugin.authenticate(config)

        pbi_generator = PBIGenerator(ado_plugin, config)
        epic_generator = EpicFeatureGenerator(ado_plugin, config, pbi_generator)

        # Process work item
        print(f"\n🔍 Processing ADO work item...\n")
        print(f"URL: {args.work_item_url}\n")

        result = epic_generator.process_work_item_url(
            args.work_item_url, auto_generate=not args.no_generate
        )

        if result.success:
            print(f"✅ Processed {result.parent_type.value}:")
            print(f"   ID: {result.parent_id}")
            print(f"   Title: {result.parent_title}")
            print(f"   Total Children: {result.total_children}")
            print(f"   Existing: {len(result.existing_children)}")
            print(f"   Generated: {len(result.generated_children)}\n")

            # Display existing children
            if result.existing_children:
                print(f"📋 Existing Child PBIs:")
                for child_id in result.existing_children:
                    child_url = f"https://dev.azure.com/{config.organization}/{config.project}/_workitems/edit/{child_id}"
                    print(f"   - {child_id}: {child_url}")
                print("")

            # Display generated children
            if result.generated_children:
                print(f"🆕 Generated Child PBIs:")
                for child_id in result.generated_children:
                    child_url = f"https://dev.azure.com/{config.organization}/{config.project}/_workitems/edit/{child_id}"
                    print(f"   - {child_id}: {child_url}")
                print("")

            # Summary
            if result.generated_children:
                print(f"✨ Generated {len(result.generated_children)} new child PBIs")
            else:
                print(f"ℹ️  No new PBIs generated (all children exist)")

        else:
            print(f"❌ Failed to process work item:")
            print(f"   Error: {result.error_message}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_process_wiki(args):
    """Process wiki URL and find/generate PBIs for all referenced work items."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_ado_config()

        # Initialize components
        ado_plugin = AzureDevOpsPlugin()
        ado_plugin.authenticate(config)

        pbi_generator = PBIGenerator(ado_plugin, config)
        epic_generator = EpicFeatureGenerator(ado_plugin, config, pbi_generator)

        # Parse wiki URL
        wiki_ref = WikiReference.parse_url(args.wiki_url)
        if not wiki_ref:
            print(f"❌ Invalid wiki URL: {args.wiki_url}")
            sys.exit(1)

        # Process wiki
        print(f"\n📖 Processing Wiki Page...\n")
        print(f"Project: {wiki_ref.project}")
        print(f"Page: {wiki_ref.page_title}")
        print(f"URL: {args.wiki_url}\n")

        results = epic_generator.process_wiki_url(
            args.wiki_url, auto_generate=not args.no_generate
        )

        if not results:
            print(f"ℹ️  No ADO work items found in wiki page")
            sys.exit(0)

        print(f"🔍 Found {len(results)} work items in wiki\n")

        # Display results for each work item
        total_existing = 0
        total_generated = 0

        for i, result in enumerate(results, 1):
            if result.success:
                print(f"{i}. {result.parent_type.value} {result.parent_id}: {result.parent_title}")
                print(f"   Existing children: {len(result.existing_children)}")
                print(f"   Generated children: {len(result.generated_children)}")

                if result.generated_children:
                    for child_id in result.generated_children:
                        child_url = f"https://dev.azure.com/{config.organization}/{config.project}/_workitems/edit/{child_id}"
                        print(f"      - Created {child_id}: {child_url}")

                total_existing += len(result.existing_children)
                total_generated += len(result.generated_children)
                print("")
            else:
                print(f"{i}. ❌ Failed: {result.error_message}\n")

        # Summary
        print(f"📊 Summary:")
        print(f"   Total work items: {len(results)}")
        print(f"   Existing child PBIs: {total_existing}")
        print(f"   Generated child PBIs: {total_generated}")
        print(f"   Total child PBIs: {total_existing + total_generated}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_generate_from_epic(args):
    """Generate child PBIs from Epic work item."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_ado_config()

        # Initialize components
        ado_plugin = AzureDevOpsPlugin()
        ado_plugin.authenticate(config)

        pbi_generator = PBIGenerator(ado_plugin, config)
        epic_generator = EpicFeatureGenerator(ado_plugin, config, pbi_generator)

        # Generate PBIs from Epic
        print(f"\n🔧 Generating child PBIs from Epic {args.epic_id}...\n")

        pbi_ids = epic_generator.generate_pbis_from_epic(args.epic_id)

        if pbi_ids:
            print(f"✅ Generated {len(pbi_ids)} child PBIs:\n")
            for pbi_id in pbi_ids:
                pbi_url = f"https://dev.azure.com/{config.organization}/{config.project}/_workitems/edit/{pbi_id}"
                print(f"   - PBI {pbi_id}: {pbi_url}")
        else:
            print(f"ℹ️  No PBIs generated")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def cmd_list_children(args):
    """List all child work items of a parent."""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = load_ado_config()

        # Initialize components
        ado_plugin = AzureDevOpsPlugin()
        ado_plugin.authenticate(config)

        pbi_generator = PBIGenerator(ado_plugin, config)
        epic_generator = EpicFeatureGenerator(ado_plugin, config, pbi_generator)

        # Find children
        print(f"\n🔍 Finding child work items for {args.parent_id}...\n")

        child_ids = epic_generator._find_child_work_items(args.parent_id)

        if child_ids:
            print(f"✅ Found {len(child_ids)} child work items:\n")

            for child_id in child_ids:
                # Get child details
                child = ado_plugin.get_work_item(child_id, config)
                child_url = f"https://dev.azure.com/{config.organization}/{config.project}/_workitems/edit/{child_id}"
                print(f"   - {child_id}: {child.title}")
                print(f"     URL: {child_url}")
                print(f"     Status: {child.status.value}")
                print("")
        else:
            print(f"ℹ️  No child work items found")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Epic/Feature/Enabler Processing CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Process work item command
    process_wi_parser = subparsers.add_parser(
        "process-work-item", help="Process ADO work item and find/generate child PBIs"
    )
    process_wi_parser.add_argument(
        "work_item_url", help="ADO work item URL (Epic, Feature, or Enabler)"
    )
    process_wi_parser.add_argument(
        "--no-generate",
        action="store_true",
        help="Only find existing children, don't generate new ones",
    )
    process_wi_parser.set_defaults(func=cmd_process_work_item)

    # Process wiki command
    process_wiki_parser = subparsers.add_parser(
        "process-wiki",
        help="Process wiki page and find/generate PBIs for all referenced work items",
    )
    process_wiki_parser.add_argument("wiki_url", help="ADO wiki page URL")
    process_wiki_parser.add_argument(
        "--no-generate",
        action="store_true",
        help="Only find existing children, don't generate new ones",
    )
    process_wiki_parser.set_defaults(func=cmd_process_wiki)

    # Generate from Epic command
    gen_epic_parser = subparsers.add_parser(
        "generate-from-epic", help="Generate child PBIs from Epic work item"
    )
    gen_epic_parser.add_argument("epic_id", help="Epic work item ID")
    gen_epic_parser.set_defaults(func=cmd_generate_from_epic)

    # List children command
    list_parser = subparsers.add_parser(
        "list-children", help="List all child work items of a parent"
    )
    list_parser.add_argument("parent_id", help="Parent work item ID")
    list_parser.set_defaults(func=cmd_list_children)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
