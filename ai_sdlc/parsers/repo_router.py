"""
Repository Router for AI-SDLC

Routes requirements to appropriate repositories based on content analysis,
routing rules, and explicit frontmatter targeting.
"""

from dataclasses import dataclass, field
from typing import List, Set

from ..core.config_loader import ProjectConfig, RepoConfig
from .requirement_parser import Requirement


@dataclass
class RoutingResult:
    """Result of routing a requirement to repositories."""

    requirement_id: str
    target_repos: List[RepoConfig]
    routing_reason: str  # Explanation of why these repos were chosen
    confidence: float  # 0.0-1.0 confidence score
    metadata: dict = field(default_factory=dict)

    def __str__(self) -> str:
        """Format routing result."""
        repo_names = [repo.id for repo in self.target_repos]
        return (
            f"Routing {self.requirement_id} to {', '.join(repo_names)}\n"
            f"Reason: {self.routing_reason}\n"
            f"Confidence: {self.confidence:.2f}"
        )


class RepoRouter:
    """
    Routes requirements to appropriate repositories.

    Routing priority:
    1. Explicit repo targeting in requirement frontmatter
    2. Content-based routing rules from project.yml
    3. Fallback to all repos if no match
    """

    def __init__(self, project_config: ProjectConfig):
        """
        Initialize RepoRouter.

        Args:
            project_config: Project configuration with repos and routing rules
        """
        self.project_config = project_config

    def route(self, requirement: Requirement) -> RoutingResult:
        """
        Route requirement to target repositories.

        Args:
            requirement: Parsed requirement

        Returns:
            RoutingResult with target repos and reasoning
        """
        # Priority 1: Explicit repo targeting in frontmatter
        if requirement.repos:
            return self._route_explicit(requirement)

        # Priority 2: Content-based routing using rules
        routing_result = self._route_by_content(requirement)
        if routing_result.target_repos:
            return routing_result

        # Priority 3: Fallback to all repos
        return self._route_fallback(requirement)

    def _route_explicit(self, requirement: Requirement) -> RoutingResult:
        """Route based on explicit repo specifications in frontmatter."""
        target_repos = []

        for repo_spec in requirement.repos:
            repo_config = self.project_config.get_repo_by_id(
                self._extract_repo_id(repo_spec.repo)
            )
            if repo_config:
                target_repos.append(repo_config)

        if not target_repos:
            # Repo IDs in frontmatter don't match any configured repos
            return self._route_fallback(requirement)

        return RoutingResult(
            requirement_id=requirement.req_id,
            target_repos=target_repos,
            routing_reason="Explicit repo targeting in requirement frontmatter",
            confidence=1.0,
            metadata={"method": "explicit", "repo_specs": requirement.repos},
        )

    def _route_by_content(self, requirement: Requirement) -> RoutingResult:
        """Route based on content analysis and routing rules."""
        # Build content string from requirement
        content = self._build_content_string(requirement)

        # Apply routing rules
        matched_repo_ids: Set[str] = set()
        matched_rules = []

        for rule in self.project_config.routing_rules:
            if rule.matches(content):
                matched_repo_ids.update(rule.prefer_repos)
                matched_rules.append(rule)

        if not matched_repo_ids:
            return RoutingResult(
                requirement_id=requirement.req_id,
                target_repos=[],
                routing_reason="No routing rules matched",
                confidence=0.0,
                metadata={"method": "content", "matched_rules": []},
            )

        # Get RepoConfig objects
        target_repos = []
        for repo_id in matched_repo_ids:
            repo_config = self.project_config.get_repo_by_id(repo_id)
            if repo_config:
                target_repos.append(repo_config)

        # Calculate confidence based on number of rules matched
        confidence = min(0.7 + (len(matched_rules) * 0.1), 1.0)

        rule_descriptions = [
            f"matches {', '.join(rule.if_contains)}" for rule in matched_rules
        ]
        reason = (
            f"Content-based routing: {len(matched_rules)} rules matched "
            f"({'; '.join(rule_descriptions)})"
        )

        return RoutingResult(
            requirement_id=requirement.req_id,
            target_repos=target_repos,
            routing_reason=reason,
            confidence=confidence,
            metadata={
                "method": "content",
                "matched_rules": [
                    {"keywords": rule.if_contains, "repos": rule.prefer_repos}
                    for rule in matched_rules
                ],
            },
        )

    def _route_fallback(self, requirement: Requirement) -> RoutingResult:
        """Fallback routing to all configured repositories."""
        return RoutingResult(
            requirement_id=requirement.req_id,
            target_repos=self.project_config.repos,
            routing_reason="Fallback: No specific routing matched, targeting all repos",
            confidence=0.3,
            metadata={"method": "fallback"},
        )

    def _build_content_string(self, requirement: Requirement) -> str:
        """
        Build searchable content string from requirement.

        Includes: title, problem statement, functional requirements,
        acceptance criteria, and Databricks objects.
        """
        parts = [
            requirement.title,
            requirement.problem_statement,
            " ".join(requirement.functional_requirements),
            " ".join(
                [
                    f"{ac.given} {ac.when} {ac.then}"
                    for ac in requirement.acceptance_criteria
                ]
            ),
        ]

        # Add Databricks objects if present
        if requirement.databricks_objects:
            parts.append(str(requirement.databricks_objects))

        return " ".join(parts)

    def _extract_repo_id(self, repo_url: str) -> str:
        """
        Extract repository ID from URL or name.

        Args:
            repo_url: Full GitHub URL or repo ID

        Returns:
            Repository ID matching project.yml

        Examples:
            "https://github.com/vivekgana/databricks-platform-marketplace.git" -> "marketplace"
            "marketplace" -> "marketplace"
        """
        # If it's already just an ID, return it
        if "/" not in repo_url:
            return repo_url

        # Try to match against configured repos
        for repo_config in self.project_config.repos:
            if repo_url in repo_config.url or repo_config.url in repo_url:
                return repo_config.id

        # Extract from URL format: owner/repo or owner/repo.git
        if "github.com" in repo_url:
            parts = repo_url.split("/")
            if len(parts) >= 2:
                repo_name = parts[-1].replace(".git", "")
                return repo_name

        # Default: use last part of URL
        return repo_url.split("/")[-1].replace(".git", "")

    def validate_routing(self, routing_result: RoutingResult) -> List[str]:
        """
        Validate routing result.

        Args:
            routing_result: RoutingResult to validate

        Returns:
            List of validation warnings (empty if valid)
        """
        warnings = []

        # Check if any repos were selected
        if not routing_result.target_repos:
            warnings.append("No target repositories selected")

        # Warn on low confidence
        if routing_result.confidence < 0.5:
            warnings.append(
                f"Low routing confidence ({routing_result.confidence:.2f}). "
                "Consider adding explicit repo targeting in requirement frontmatter."
            )

        # Check if all repos have required configuration
        for repo in routing_result.target_repos:
            if not repo.default_branch:
                warnings.append(f"Repo {repo.id} missing default_branch configuration")
            if not repo.scopes:
                warnings.append(
                    f"Repo {repo.id} has no path scopes defined. "
                    "AI may modify unintended files."
                )

        return warnings

    def get_routing_suggestions(self, requirement: Requirement) -> List[str]:
        """
        Get suggestions for improving routing confidence.

        Args:
            requirement: Requirement to analyze

        Returns:
            List of suggestions for improving routing
        """
        suggestions = []

        # Suggest adding explicit repos if none specified
        if not requirement.repos:
            suggestions.append(
                "Add explicit `repos:` section to requirement frontmatter "
                "for deterministic routing"
            )

        # Analyze content and suggest keywords
        content = self._build_content_string(requirement).lower()

        databricks_keywords = [
            "databricks",
            "bundle",
            "notebook",
            "dlt",
            "delta live tables",
            "unity catalog",
        ]
        if any(kw in content for kw in databricks_keywords):
            suggestions.append(
                "Requirement mentions Databricks concepts. "
                "Consider adding more specific Databricks keywords for better routing."
            )

        # Suggest adding Databricks objects section if missing
        if not requirement.databricks_objects and any(
            kw in content for kw in databricks_keywords
        ):
            suggestions.append(
                "Add '## 6. Data & Databricks objects' section "
                "to specify catalogs, schemas, tables, and jobs"
            )

        return suggestions
