"""
Unit tests for ConfigLoader.
"""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from ai_sdlc.core.config_loader import (
    AISDLCConfig,
    CodegenPolicyConfig,
    ConfigLoader,
    LLMConfig,
    PRPolicyConfig,
    ProjectConfig,
    RepoConfig,
    RoutingRule,
)


@pytest.fixture
def sample_config_dict():
    """Sample configuration dictionary."""
    return {
        "project": {
            "name": "Test Project",
            "default_branch": "develop",
            "release_branch": "main",
        },
        "repos": [
            {
                "id": "test-repo",
                "url": "https://github.com/test/repo.git",
                "default_branch": "develop",
                "release_branch": "main",
                "scopes": ["src/", "tests/"],
                "signals": {"bundling": "databricks_asset_bundles"},
                "ci": {"provider": "github_actions"},
                "deploy": {"method": "dab", "targets": ["dev", "prod"]},
            }
        ],
        "codegen": {
            "policy": {
                "max_prs_per_run": 3,
                "require_plan_review": True,
                "require_tests": True,
                "allowed_change_zones": ["src/", "tests/"],
            },
            "pr_policy": {
                "default_base_branch": "develop",
                "allow_main_direct_pr": False,
                "hotfix_label_allows_main": "hotfix",
            },
        },
        "routing": {
            "rules": [
                {
                    "if_contains": ["databricks", "bundle"],
                    "prefer_repos": ["test-repo"],
                }
            ]
        },
        "pr_linking": {
            "base_branch": "develop",
            "branch_prefix": "ai/",
            "commit_prefix": "[AI-SDLC]",
            "issue_labels": ["ai-sdlc:req"],
        },
        "ai_sdlc_config": {
            "llm": {
                "provider": "anthropic",
                "model": "claude-sonnet-4-5",
                "temperature": 0.2,
                "max_tokens": 8000,
            },
            "evidence": {
                "enabled": True,
                "base_path": "/dbfs/tmp/demo/",
                "required_formats": ["png", "html", "md"],
            },
        },
    }


@pytest.fixture
def config_file(sample_config_dict):
    """Create temporary config file."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yml", delete=False, encoding="utf-8"
    ) as f:
        yaml.dump(sample_config_dict, f)
        config_path = f.name

    yield config_path

    # Cleanup
    if os.path.exists(config_path):
        os.remove(config_path)


class TestRepoConfig:
    """Tests for RepoConfig."""

    def test_from_dict(self):
        """Test creating RepoConfig from dictionary."""
        data = {
            "id": "test",
            "url": "https://github.com/test/repo.git",
            "default_branch": "develop",
            "release_branch": "main",
            "scopes": ["src/"],
        }
        repo = RepoConfig.from_dict(data)

        assert repo.id == "test"
        assert repo.url == "https://github.com/test/repo.git"
        assert repo.default_branch == "develop"
        assert repo.scopes == ["src/"]

    def test_matches_scope(self):
        """Test scope matching."""
        repo = RepoConfig(
            id="test",
            url="https://github.com/test/repo.git",
            default_branch="develop",
            release_branch="main",
            scopes=["src/", "tests/"],
        )

        assert repo.matches_scope("src/main.py")
        assert repo.matches_scope("tests/test_main.py")
        assert not repo.matches_scope("docs/README.md")

    def test_matches_scope_no_scopes(self):
        """Test scope matching with no scopes (matches all)."""
        repo = RepoConfig(
            id="test",
            url="https://github.com/test/repo.git",
            default_branch="develop",
            release_branch="main",
        )

        assert repo.matches_scope("anything.py")


class TestRoutingRule:
    """Tests for RoutingRule."""

    def test_from_dict(self):
        """Test creating RoutingRule from dictionary."""
        data = {"if_contains": ["databricks", "bundle"], "prefer_repos": ["repo1"]}
        rule = RoutingRule.from_dict(data)

        assert rule.if_contains == ["databricks", "bundle"]
        assert rule.prefer_repos == ["repo1"]

    def test_matches(self):
        """Test content matching."""
        rule = RoutingRule(if_contains=["databricks", "bundle"], prefer_repos=["repo1"])

        assert rule.matches("This is about Databricks bundles")
        assert rule.matches("DATABRICKS workflow")
        assert not rule.matches("This is about something else")


class TestProjectConfig:
    """Tests for ProjectConfig."""

    def test_get_repo_by_id(self):
        """Test getting repository by ID."""
        repo1 = RepoConfig(
            id="repo1",
            url="https://github.com/test/repo1.git",
            default_branch="develop",
            release_branch="main",
        )
        repo2 = RepoConfig(
            id="repo2",
            url="https://github.com/test/repo2.git",
            default_branch="develop",
            release_branch="main",
        )

        config = ProjectConfig(
            name="Test", default_branch="develop", repos=[repo1, repo2]
        )

        assert config.get_repo_by_id("repo1") == repo1
        assert config.get_repo_by_id("repo2") == repo2
        assert config.get_repo_by_id("nonexistent") is None

    def test_route_requirement(self):
        """Test requirement routing."""
        repo1 = RepoConfig(
            id="repo1",
            url="https://github.com/test/repo1.git",
            default_branch="develop",
            release_branch="main",
        )
        repo2 = RepoConfig(
            id="repo2",
            url="https://github.com/test/repo2.git",
            default_branch="develop",
            release_branch="main",
        )

        rule = RoutingRule(if_contains=["databricks"], prefer_repos=["repo1"])

        config = ProjectConfig(
            name="Test",
            default_branch="develop",
            repos=[repo1, repo2],
            routing_rules=[rule],
        )

        # Should match rule and route to repo1
        result = config.route_requirement("This is about Databricks")
        assert result == ["repo1"]

        # Should not match and return all repos
        result = config.route_requirement("This is about something else")
        assert set(result) == {"repo1", "repo2"}


class TestConfigLoader:
    """Tests for ConfigLoader."""

    def test_load_valid_config(self, config_file):
        """Test loading a valid configuration file."""
        loader = ConfigLoader(config_file)
        config = loader.load()

        assert config.name == "Test Project"
        assert config.default_branch == "develop"
        assert len(config.repos) == 1
        assert config.repos[0].id == "test-repo"

    def test_load_missing_file(self):
        """Test loading a non-existent file."""
        loader = ConfigLoader("/nonexistent/path.yml")

        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_load_invalid_yaml(self):
        """Test loading invalid YAML."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False, encoding="utf-8"
        ) as f:
            f.write("invalid: yaml: content:")
            config_path = f.name

        try:
            loader = ConfigLoader(config_path)
            with pytest.raises(Exception):  # YAML parsing error
                loader.load()
        finally:
            os.remove(config_path)

    def test_validate_missing_name(self, sample_config_dict):
        """Test validation with missing project name."""
        del sample_config_dict["project"]["name"]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False, encoding="utf-8"
        ) as f:
            yaml.dump(sample_config_dict, f)
            config_path = f.name

        try:
            loader = ConfigLoader(config_path)
            with pytest.raises(ValueError, match="Project name is required"):
                loader.load()
        finally:
            os.remove(config_path)

    def test_validate_no_repos(self, sample_config_dict):
        """Test validation with no repositories."""
        sample_config_dict["repos"] = []

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False, encoding="utf-8"
        ) as f:
            yaml.dump(sample_config_dict, f)
            config_path = f.name

        try:
            loader = ConfigLoader(config_path)
            with pytest.raises(ValueError, match="At least one repository"):
                loader.load()
        finally:
            os.remove(config_path)

    def test_validate_duplicate_repo_ids(self, sample_config_dict):
        """Test validation with duplicate repo IDs."""
        sample_config_dict["repos"].append(sample_config_dict["repos"][0].copy())

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False, encoding="utf-8"
        ) as f:
            yaml.dump(sample_config_dict, f)
            config_path = f.name

        try:
            loader = ConfigLoader(config_path)
            with pytest.raises(ValueError, match="Repository IDs must be unique"):
                loader.load()
        finally:
            os.remove(config_path)

    def test_validate_invalid_llm_provider(self, sample_config_dict):
        """Test validation with invalid LLM provider."""
        sample_config_dict["ai_sdlc_config"]["llm"]["provider"] = "invalid_provider"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False, encoding="utf-8"
        ) as f:
            yaml.dump(sample_config_dict, f)
            config_path = f.name

        try:
            loader = ConfigLoader(config_path)
            with pytest.raises(ValueError, match="Invalid LLM provider"):
                loader.load()
        finally:
            os.remove(config_path)

    def test_reload(self, config_file):
        """Test reloading configuration."""
        loader = ConfigLoader(config_file)
        config1 = loader.load()
        config2 = loader.reload()

        assert config1.name == config2.name
        assert config1.repos[0].id == config2.repos[0].id
