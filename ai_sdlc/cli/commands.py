"""
AI-SDLC CLI Commands

Provides command-line interface for AI-SDLC operations including:
- parse: Parse and validate REQ-*.md files
- route: Route requirements to repositories
- validate: Validate project configuration
"""

import sys
from pathlib import Path
from typing import Optional

import click

from ..core.config_loader import ConfigLoader
from ..parsers.repo_router import RepoRouter
from ..parsers.requirement_parser import RequirementParser


@click.group()
@click.version_option(version="0.1.0", prog_name="ai-sdlc")
def cli():
    """
    AI-SDLC CLI - AI-Driven Software Development Life Cycle for Databricks

    This tool helps automate the software development lifecycle for Databricks
    platforms using AI-powered code generation, requirement parsing, and
    multi-repo workflows.
    """
    pass


@cli.command()
@click.argument("requirement_file", type=click.Path(exists=True))
@click.option(
    "--validate/--no-validate",
    default=True,
    help="Validate requirement completeness",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def parse(requirement_file: str, validate: bool, verbose: bool):
    """
    Parse and display a REQ-*.md requirement file.

    REQUIREMENT_FILE: Path to REQ-*.md file

    Examples:
        ai-sdlc parse requirements/REQ-101.md
        ai-sdlc parse requirements/REQ-101.md --no-validate
        ai-sdlc parse requirements/REQ-101.md -v
    """
    try:
        parser = RequirementParser()
        click.echo(f"Parsing {requirement_file}...")

        # Parse requirement
        requirement = parser.parse_file(requirement_file)

        # Display summary
        click.echo(f"\n{'=' * 60}")
        click.echo(f"Requirement: {requirement.req_id}")
        click.echo(f"Title: {requirement.title}")
        click.echo(f"Owner: {requirement.owner}")
        click.echo(f"Team: {requirement.team}")
        click.echo(f"Priority: {requirement.priority.value}")
        click.echo(f"Status: {requirement.status.value}")
        click.echo(f"Target Release: {requirement.target_release}")
        click.echo(f"{'=' * 60}\n")

        # Display repos
        if requirement.repos:
            click.echo(f"Target Repositories ({len(requirement.repos)}):")
            for repo_spec in requirement.repos:
                click.echo(f"  - {repo_spec.repo} (base: {repo_spec.base_branch})")
        else:
            click.echo("Target Repositories: None specified (will use routing rules)")

        # Display acceptance criteria
        click.echo(f"\nAcceptance Criteria ({len(requirement.acceptance_criteria)}):")
        for ac in requirement.acceptance_criteria:
            click.echo(f"\n  {ac.id}:")
            if verbose:
                click.echo(f"    Given: {ac.given[:80]}...")
                click.echo(f"    When: {ac.when[:80]}...")
                click.echo(f"    Then: {ac.then[:80]}...")
            if ac.verification:
                click.echo(
                    f"    Verification: {ac.verification.method.value} - "
                    f"{ac.verification.details[:60]}..."
                )
            if ac.demo_evidence:
                click.echo(f"    Demo Evidence: {', '.join(ac.demo_evidence)}")

        # Display demo spec
        if requirement.demo:
            click.echo(f"\nDemo Evidence:")
            click.echo(f"  Path: {requirement.demo.evidence_path}")
            click.echo(
                f"  Required Assets: {', '.join(requirement.demo.required_assets)}"
            )

        # Validate if requested
        if validate:
            click.echo(f"\n{'=' * 60}")
            click.echo("Validation Results:")
            errors = parser.validate(requirement)
            if errors:
                click.echo(click.style("✗ Validation failed:", fg="red", bold=True))
                for error in errors:
                    click.echo(click.style(f"  - {error}", fg="red"))
                sys.exit(1)
            else:
                click.echo(click.style("✓ Validation passed", fg="green", bold=True))

        click.echo(f"\n{'=' * 60}")
        click.echo(click.style("✓ Parsing successful", fg="green", bold=True))

    except Exception as e:
        click.echo(click.style(f"✗ Error: {str(e)}", fg="red", bold=True))
        sys.exit(1)


@cli.command()
@click.argument("requirement_file", type=click.Path(exists=True))
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to project.yml config file",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def route(requirement_file: str, config: Optional[str], verbose: bool):
    """
    Route a requirement to target repositories.

    REQUIREMENT_FILE: Path to REQ-*.md file

    Examples:
        ai-sdlc route requirements/REQ-101.md
        ai-sdlc route requirements/REQ-101.md -c ./ai_sdlc/project.yml
        ai-sdlc route requirements/REQ-101.md -v
    """
    try:
        # Load configuration
        click.echo("Loading project configuration...")
        config_loader = ConfigLoader(config)
        project_config = config_loader.load()
        click.echo(f"✓ Loaded configuration for: {project_config.name}\n")

        # Parse requirement
        click.echo(f"Parsing {requirement_file}...")
        parser = RequirementParser()
        requirement = parser.parse_file(requirement_file)
        click.echo(f"✓ Parsed requirement: {requirement.req_id}\n")

        # Route requirement
        click.echo("Routing requirement to repositories...")
        router = RepoRouter(project_config)
        routing_result = router.route(requirement)

        # Display routing result
        click.echo(f"\n{'=' * 60}")
        click.echo("Routing Result:")
        click.echo(f"{'=' * 60}\n")

        click.echo(f"Requirement: {routing_result.requirement_id}")
        click.echo(f"Confidence: {routing_result.confidence:.2%}")
        click.echo(f"Reason: {routing_result.routing_reason}\n")

        click.echo(f"Target Repositories ({len(routing_result.target_repos)}):")
        for repo in routing_result.target_repos:
            click.echo(f"\n  {repo.id}:")
            click.echo(f"    URL: {repo.url}")
            click.echo(f"    Base Branch: {repo.default_branch}")
            click.echo(f"    Release Branch: {repo.release_branch}")
            if verbose and repo.scopes:
                click.echo(f"    Path Scopes: {', '.join(repo.scopes)}")
            if verbose and repo.signals:
                click.echo(f"    Signals: {repo.signals}")

        # Validate routing
        warnings = router.validate_routing(routing_result)
        if warnings:
            click.echo(f"\n{'=' * 60}")
            click.echo(click.style("Routing Warnings:", fg="yellow", bold=True))
            for warning in warnings:
                click.echo(click.style(f"  ⚠ {warning}", fg="yellow"))

        # Get suggestions
        if verbose:
            suggestions = router.get_routing_suggestions(requirement)
            if suggestions:
                click.echo(f"\n{'=' * 60}")
                click.echo("Routing Suggestions:")
                for suggestion in suggestions:
                    click.echo(f"  💡 {suggestion}")

        click.echo(f"\n{'=' * 60}")
        click.echo(click.style("✓ Routing complete", fg="green", bold=True))

    except Exception as e:
        click.echo(click.style(f"✗ Error: {str(e)}", fg="red", bold=True))
        if verbose:
            import traceback

            click.echo(traceback.format_exc())
        sys.exit(1)


@cli.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to project.yml config file",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def validate_config(config: Optional[str], verbose: bool):
    """
    Validate project configuration (project.yml).

    Examples:
        ai-sdlc validate-config
        ai-sdlc validate-config -c ./ai_sdlc/project.yml
        ai-sdlc validate-config -v
    """
    try:
        click.echo("Validating project configuration...")

        # Load and validate configuration
        config_loader = ConfigLoader(config)
        project_config = config_loader.load()

        # Display configuration summary
        click.echo(f"\n{'=' * 60}")
        click.echo(f"Project: {project_config.name}")
        click.echo(f"Default Branch: {project_config.default_branch}")
        click.echo(f"Release Branch: {project_config.release_branch}")
        click.echo(f"{'=' * 60}\n")

        # Display repositories
        click.echo(f"Repositories ({len(project_config.repos)}):")
        for repo in project_config.repos:
            click.echo(f"\n  {repo.id}:")
            click.echo(f"    URL: {repo.url}")
            click.echo(f"    Default Branch: {repo.default_branch}")
            click.echo(f"    Release Branch: {repo.release_branch}")
            if verbose:
                if repo.scopes:
                    click.echo(f"    Scopes: {', '.join(repo.scopes)}")
                if repo.signals:
                    click.echo(f"    Signals: {repo.signals}")
                if repo.ci:
                    click.echo(f"    CI: {repo.ci}")

        # Display routing rules
        click.echo(f"\nRouting Rules ({len(project_config.routing_rules)}):")
        for i, rule in enumerate(project_config.routing_rules, 1):
            click.echo(f"  Rule {i}:")
            click.echo(f"    Keywords: {', '.join(rule.if_contains)}")
            click.echo(f"    Target Repos: {', '.join(rule.prefer_repos)}")

        # Display PR policy
        click.echo(f"\nPR Policy:")
        click.echo(f"  Base Branch: {project_config.pr_policy.default_base_branch}")
        click.echo(
            f"  Allow Main Direct PR: {project_config.pr_policy.allow_main_direct_pr}"
        )
        click.echo(
            f"  Hotfix Label: {project_config.pr_policy.hotfix_label_allows_main}"
        )

        # Display AI-SDLC configuration
        if verbose:
            click.echo(f"\nAI-SDLC Configuration:")
            llm = project_config.ai_sdlc_config.llm
            click.echo(f"  LLM Provider: {llm.provider}")
            click.echo(f"  LLM Model: {llm.model}")
            click.echo(f"  Temperature: {llm.temperature}")
            click.echo(f"  Max Tokens: {llm.max_tokens}")

            evidence = project_config.ai_sdlc_config.evidence
            click.echo(f"\n  Evidence Generation: {evidence.enabled}")
            click.echo(f"  Evidence Path: {evidence.base_path}")
            click.echo(f"  Required Formats: {', '.join(evidence.required_formats)}")

        click.echo(f"\n{'=' * 60}")
        click.echo(click.style("✓ Configuration is valid", fg="green", bold=True))

    except Exception as e:
        click.echo(click.style(f"✗ Validation failed: {str(e)}", fg="red", bold=True))
        if verbose:
            import traceback

            click.echo(traceback.format_exc())
        sys.exit(1)


@cli.command()
def info():
    """
    Display AI-SDLC system information and status.
    """
    click.echo(f"\n{'=' * 60}")
    click.echo("AI-SDLC System Information")
    click.echo(f"{'=' * 60}\n")

    click.echo("Version: 0.1.0 (Phase 1 - Foundation)")
    click.echo("Status: In Development\n")

    click.echo("Implemented Features:")
    click.echo("  ✓ Configuration loading (project.yml)")
    click.echo("  ✓ Requirement parsing (REQ-*.md)")
    click.echo("  ✓ Multi-repo routing")
    click.echo("  ✓ LLM client (Claude, OpenAI, Azure, Databricks)")
    click.echo("  ✓ CLI commands (parse, route, validate-config)\n")

    click.echo("Pending Features:")
    click.echo("  ⬜ Codebase analysis")
    click.echo("  ⬜ Code generation")
    click.echo("  ⬜ Demo evidence automation")
    click.echo("  ⬜ PR workflow management")
    click.echo("  ⬜ DevOps integration\n")

    click.echo("Documentation:")
    click.echo("  - README: docs/AI_SDLC_DESIGN.md")
    click.echo("  - Implementation Plan: AI_SDLC_IMPLEMENTATION_PLAN.md")
    click.echo("  - Requirements Template: requirements/REQ-TEMPLATE.md\n")

    click.echo(f"{'=' * 60}\n")


if __name__ == "__main__":
    cli()
