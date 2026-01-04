"""
Unit tests for RepoRouter.
"""

import pytest

from ai_sdlc.core.config_loader import ProjectConfig, RepoConfig, RoutingRule
from ai_sdlc.parsers.repo_router import RepoRouter
from ai_sdlc.parsers.requirement_parser import (
    Requirement,
    RequirementPriority,
    RequirementStatus,
    RepoSpec,
)


@pytest.fixture
def project_config():
    """Create sample project configuration."""
    repo1 = RepoConfig(
        id="marketplace",
        url="https://github.com/vivekgana/databricks-platform-marketplace.git",
        default_branch="develop",
        release_branch="main",
        scopes=["src/", "notebooks/", "tests/"],
    )

    repo2 = RepoConfig(
        id="analytics",
        url="https://github.com/vivekgana/analytics.git",
        default_branch="develop",
        release_branch="main",
        scopes=["pipelines/", "queries/"],
    )

    rule1 = RoutingRule(
        if_contains=["databricks", "bundle", "notebook"],
        prefer_repos=["marketplace"],
    )

    rule2 = RoutingRule(
        if_contains=["sql", "query", "analytics"], prefer_repos=["analytics"]
    )

    return ProjectConfig(
        name="Test Project",
        default_branch="develop",
        release_branch="main",
        repos=[repo1, repo2],
        routing_rules=[rule1, rule2],
    )


@pytest.fixture
def sample_requirement():
    """Create sample requirement."""
    return Requirement(
        req_id="REQ-001",
        title="Test Databricks Bundle Feature",
        owner="Product Owner",
        product="Platform",
        team="Platform Team",
        priority=RequirementPriority.P1,
        status=RequirementStatus.DRAFT,
        target_release="v1.0",
        created="2026-01-01",
        updated="2026-01-03",
        problem_statement="Need to add Databricks bundle support",
        functional_requirements=["Add bundle configuration", "Create notebooks"],
    )


class TestRepoRouter:
    """Tests for RepoRouter."""

    def test_route_explicit(self, project_config, sample_requirement):
        """Test routing with explicit repo specification."""
        # Add explicit repo targeting
        sample_requirement.repos = [RepoSpec(repo="marketplace", base_branch="develop")]

        router = RepoRouter(project_config)
        result = router.route(sample_requirement)

        assert len(result.target_repos) == 1
        assert result.target_repos[0].id == "marketplace"
        assert result.confidence == 1.0
        assert "Explicit" in result.routing_reason

    def test_route_by_content_databricks(self, project_config, sample_requirement):
        """Test content-based routing for Databricks keywords."""
        # No explicit repos - should use content routing
        sample_requirement.repos = []

        router = RepoRouter(project_config)
        result = router.route(sample_requirement)

        assert len(result.target_repos) == 1
        assert result.target_repos[0].id == "marketplace"
        assert result.confidence > 0.5
        assert "Content-based" in result.routing_reason

    def test_route_by_content_analytics(self, project_config):
        """Test content-based routing for analytics keywords."""
        requirement = Requirement(
            req_id="REQ-002",
            title="SQL Query Optimization",
            owner="Product Owner",
            product="Analytics",
            team="Data Team",
            priority=RequirementPriority.P2,
            status=RequirementStatus.DRAFT,
            target_release="v1.0",
            created="2026-01-01",
            updated="2026-01-03",
            problem_statement="Need to optimize SQL queries for analytics",
            functional_requirements=["Add query caching", "Optimize joins"],
        )

        router = RepoRouter(project_config)
        result = router.route(requirement)

        assert len(result.target_repos) == 1
        assert result.target_repos[0].id == "analytics"
        assert result.confidence > 0.5

    def test_route_fallback(self, project_config):
        """Test fallback routing to all repos."""
        requirement = Requirement(
            req_id="REQ-003",
            title="Generic Feature",
            owner="Product Owner",
            product="Platform",
            team="Team",
            priority=RequirementPriority.P3,
            status=RequirementStatus.DRAFT,
            target_release="v1.0",
            created="2026-01-01",
            updated="2026-01-03",
            problem_statement="Generic feature with no specific keywords",
            functional_requirements=["Do something"],
        )

        router = RepoRouter(project_config)
        result = router.route(requirement)

        # Should route to all repos when no match
        assert len(result.target_repos) == 2
        assert result.confidence == 0.3
        assert "Fallback" in result.routing_reason

    def test_route_multiple_rules_match(self, project_config):
        """Test routing when multiple rules match."""
        requirement = Requirement(
            req_id="REQ-004",
            title="Databricks SQL Analytics",
            owner="Product Owner",
            product="Platform",
            team="Team",
            priority=RequirementPriority.P1,
            status=RequirementStatus.DRAFT,
            target_release="v1.0",
            created="2026-01-01",
            updated="2026-01-03",
            problem_statement="SQL analytics on Databricks platform",
            functional_requirements=["SQL queries", "Databricks notebooks"],
        )

        router = RepoRouter(project_config)
        result = router.route(requirement)

        # Both rules should match
        assert len(result.target_repos) == 2
        repo_ids = {repo.id for repo in result.target_repos}
        assert "marketplace" in repo_ids
        assert "analytics" in repo_ids

    def test_extract_repo_id_from_url(self, project_config):
        """Test extracting repo ID from various URL formats."""
        router = RepoRouter(project_config)

        # Full GitHub URL
        assert (
            router._extract_repo_id(
                "https://github.com/vivekgana/databricks-platform-marketplace.git"
            )
            == "marketplace"
        )

        # Just repo ID
        assert router._extract_repo_id("marketplace") == "marketplace"

        # Unknown URL
        result = router._extract_repo_id("https://github.com/user/unknown-repo.git")
        assert result == "unknown-repo"

    def test_build_content_string(self, project_config, sample_requirement):
        """Test building searchable content string."""
        router = RepoRouter(project_config)
        content = router._build_content_string(sample_requirement)

        assert "Test Databricks Bundle Feature" in content
        assert "Need to add Databricks bundle support" in content
        assert "Add bundle configuration" in content

    def test_validate_routing_success(self, project_config, sample_requirement):
        """Test validating successful routing."""
        sample_requirement.repos = [RepoSpec(repo="marketplace", base_branch="develop")]

        router = RepoRouter(project_config)
        result = router.route(sample_requirement)

        warnings = router.validate_routing(result)
        assert len(warnings) == 0

    def test_validate_routing_no_repos(self, project_config):
        """Test validating routing with no target repos."""
        from ai_sdlc.parsers.repo_router import RoutingResult

        result = RoutingResult(
            requirement_id="REQ-001",
            target_repos=[],
            routing_reason="Test",
            confidence=0.0,
        )

        router = RepoRouter(project_config)
        warnings = router.validate_routing(result)

        assert len(warnings) > 0
        assert any("No target repositories" in w for w in warnings)

    def test_validate_routing_low_confidence(self, project_config):
        """Test validating routing with low confidence."""
        from ai_sdlc.parsers.repo_router import RoutingResult

        result = RoutingResult(
            requirement_id="REQ-001",
            target_repos=project_config.repos,
            routing_reason="Fallback",
            confidence=0.3,
        )

        router = RepoRouter(project_config)
        warnings = router.validate_routing(result)

        assert any("Low routing confidence" in w for w in warnings)

    def test_get_routing_suggestions_no_explicit_repos(
        self, project_config, sample_requirement
    ):
        """Test getting suggestions when no explicit repos specified."""
        sample_requirement.repos = []

        router = RepoRouter(project_config)
        suggestions = router.get_routing_suggestions(sample_requirement)

        assert any("explicit" in s.lower() for s in suggestions)

    def test_get_routing_suggestions_databricks_content(
        self, project_config, sample_requirement
    ):
        """Test suggestions for Databricks content."""
        router = RepoRouter(project_config)
        suggestions = router.get_routing_suggestions(sample_requirement)

        assert any("databricks" in s.lower() for s in suggestions)

    def test_routing_metadata(self, project_config, sample_requirement):
        """Test routing result includes metadata."""
        sample_requirement.repos = []

        router = RepoRouter(project_config)
        result = router.route(sample_requirement)

        assert "method" in result.metadata
        assert result.metadata["method"] in ["explicit", "content", "fallback"]
