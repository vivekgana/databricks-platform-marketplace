"""
Configuration Loader for AI-SDLC

Loads and validates project.yml configuration for multi-repo AI-SDLC workflows.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class RepoConfig:
    """Configuration for a single repository."""

    id: str
    url: str
    default_branch: str
    release_branch: str
    scopes: List[str] = field(default_factory=list)
    signals: Dict[str, str] = field(default_factory=dict)
    ci: Dict[str, Any] = field(default_factory=dict)
    deploy: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepoConfig":
        """Create RepoConfig from dictionary."""
        return cls(
            id=data["id"],
            url=data["url"],
            default_branch=data.get("default_branch", "develop"),
            release_branch=data.get("release_branch", "main"),
            scopes=data.get("scopes", []),
            signals=data.get("signals", {}),
            ci=data.get("ci", {}),
            deploy=data.get("deploy", {}),
        )

    def matches_scope(self, file_path: str) -> bool:
        """Check if a file path matches this repo's scopes."""
        if not self.scopes:
            return True
        return any(file_path.startswith(scope) for scope in self.scopes)


@dataclass
class CodegenPolicyConfig:
    """Code generation policy configuration."""

    max_prs_per_run: int = 3
    require_plan_review: bool = True
    require_tests: bool = True
    allowed_change_zones: List[str] = field(default_factory=list)


@dataclass
class PRPolicyConfig:
    """Pull request policy configuration."""

    default_base_branch: str = "develop"
    allow_main_direct_pr: bool = False
    hotfix_label_allows_main: str = "ai-sdlc:hotfix"


@dataclass
class LLMConfig:
    """LLM provider configuration."""

    provider: str = "anthropic"
    model: str = "claude-sonnet-4-5"
    temperature: float = 0.2
    max_tokens: int = 8000
    timeout_seconds: int = 120


@dataclass
class EvidenceConfig:
    """Evidence generation configuration."""

    enabled: bool = True
    base_path: str = "/dbfs/tmp/demo/"
    timeout_seconds: int = 3600
    required_formats: List[str] = field(default_factory=lambda: ["png", "html", "md"])


@dataclass
class GatesConfig:
    """Approval gates configuration."""

    require_plan_review: bool = True
    require_pr_review: bool = True
    require_demo_evidence: bool = True
    min_reviewers: int = 1


@dataclass
class GenerationConfig:
    """Code generation configuration."""

    max_files_per_pr: int = 50
    enable_test_generation: bool = True
    enable_databricks_generation: bool = True
    follow_existing_patterns: bool = True


@dataclass
class NotificationsConfig:
    """Notifications configuration."""

    slack_enabled: bool = False
    slack_webhook_url: Optional[str] = None
    slack_notify_on: List[str] = field(default_factory=list)
    email_enabled: bool = False


@dataclass
class AISDLCConfig:
    """AI-SDLC system configuration."""

    llm: LLMConfig = field(default_factory=LLMConfig)
    evidence: EvidenceConfig = field(default_factory=EvidenceConfig)
    gates: GatesConfig = field(default_factory=GatesConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    notifications: NotificationsConfig = field(default_factory=NotificationsConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AISDLCConfig":
        """Create AISDLCConfig from dictionary."""
        return cls(
            llm=LLMConfig(**data.get("llm", {})) if data.get("llm") else LLMConfig(),
            evidence=(
                EvidenceConfig(**data.get("evidence", {}))
                if data.get("evidence")
                else EvidenceConfig()
            ),
            gates=(
                GatesConfig(**data.get("gates", {}))
                if data.get("gates")
                else GatesConfig()
            ),
            generation=(
                GenerationConfig(**data.get("generation", {}))
                if data.get("generation")
                else GenerationConfig()
            ),
            notifications=(
                NotificationsConfig(**data.get("notifications", {}).get("slack", {}))
                if data.get("notifications")
                else NotificationsConfig()
            ),
        )


@dataclass
class RoutingRule:
    """Routing rule for multi-repo targeting."""

    if_contains: List[str] = field(default_factory=list)
    prefer_repos: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoutingRule":
        """Create RoutingRule from dictionary."""
        return cls(
            if_contains=data.get("if_contains", []),
            prefer_repos=data.get("prefer_repos", []),
        )

    def matches(self, content: str) -> bool:
        """Check if content matches this routing rule."""
        if not self.if_contains:
            return False
        content_lower = content.lower()
        return any(keyword.lower() in content_lower for keyword in self.if_contains)


@dataclass
class PRLinkingConfig:
    """PR linking configuration."""

    base_branch: str = "develop"
    branch_prefix: str = "ai/"
    commit_prefix: str = "[AI-SDLC]"
    issue_labels: List[str] = field(default_factory=list)


@dataclass
class ProjectConfig:
    """Main project configuration."""

    name: str
    default_branch: str = "develop"
    release_branch: str = "main"
    repos: List[RepoConfig] = field(default_factory=list)
    codegen_policy: CodegenPolicyConfig = field(default_factory=CodegenPolicyConfig)
    pr_policy: PRPolicyConfig = field(default_factory=PRPolicyConfig)
    routing_rules: List[RoutingRule] = field(default_factory=list)
    pr_linking: PRLinkingConfig = field(default_factory=PRLinkingConfig)
    ai_sdlc_config: AISDLCConfig = field(default_factory=AISDLCConfig)

    def get_repo_by_id(self, repo_id: str) -> Optional[RepoConfig]:
        """Get repository configuration by ID."""
        for repo in self.repos:
            if repo.id == repo_id:
                return repo
        return None

    def route_requirement(self, content: str) -> List[str]:
        """
        Route requirement content to appropriate repositories.

        Args:
            content: Requirement content to analyze

        Returns:
            List of repository IDs that should handle this requirement
        """
        matched_repos = set()

        # Apply routing rules
        for rule in self.routing_rules:
            if rule.matches(content):
                matched_repos.update(rule.prefer_repos)

        # If no rules matched, return all repos
        if not matched_repos:
            return [repo.id for repo in self.repos]

        return list(matched_repos)


class ConfigLoader:
    """Loads and validates AI-SDLC project configuration."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ConfigLoader.

        Args:
            config_path: Path to project.yml config file.
                        If None, uses AI_SDLC_PROJECT_CONFIG env var or default.
        """
        if config_path is None:
            config_path = os.getenv("AI_SDLC_PROJECT_CONFIG", "./ai_sdlc/project.yml")

        self.config_path = Path(config_path)
        self._config: Optional[ProjectConfig] = None

    def load(self) -> ProjectConfig:
        """
        Load and parse project configuration.

        Returns:
            ProjectConfig object

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)

        if not raw_config:
            raise ValueError(f"Empty config file: {self.config_path}")

        self._config = self._parse_config(raw_config)
        self._validate_config(self._config)

        return self._config

    def _parse_config(self, raw_config: Dict[str, Any]) -> ProjectConfig:
        """Parse raw YAML config into ProjectConfig."""
        project_data = raw_config.get("project", {})

        # Parse repos
        repos = [
            RepoConfig.from_dict(repo_data) for repo_data in raw_config.get("repos", [])
        ]

        # Parse codegen policy
        codegen_data = raw_config.get("codegen", {}).get("policy", {})
        codegen_policy = CodegenPolicyConfig(
            max_prs_per_run=codegen_data.get("max_prs_per_run", 3),
            require_plan_review=codegen_data.get("require_plan_review", True),
            require_tests=codegen_data.get("require_tests", True),
            allowed_change_zones=codegen_data.get("allowed_change_zones", []),
        )

        # Parse PR policy
        pr_policy_data = raw_config.get("codegen", {}).get("pr_policy", {})
        pr_policy = PRPolicyConfig(
            default_base_branch=pr_policy_data.get("default_base_branch", "develop"),
            allow_main_direct_pr=pr_policy_data.get("allow_main_direct_pr", False),
            hotfix_label_allows_main=pr_policy_data.get(
                "hotfix_label_allows_main", "ai-sdlc:hotfix"
            ),
        )

        # Parse routing rules
        routing_data = raw_config.get("routing", {}).get("rules", [])
        routing_rules = [RoutingRule.from_dict(rule) for rule in routing_data]

        # Parse PR linking
        pr_linking_data = raw_config.get("pr_linking", {})
        pr_linking = PRLinkingConfig(
            base_branch=pr_linking_data.get("base_branch", "develop"),
            branch_prefix=pr_linking_data.get("branch_prefix", "ai/"),
            commit_prefix=pr_linking_data.get("commit_prefix", "[AI-SDLC]"),
            issue_labels=pr_linking_data.get("issue_labels", []),
        )

        # Parse AI-SDLC config
        ai_sdlc_data = raw_config.get("ai_sdlc_config", {})
        ai_sdlc_config = AISDLCConfig.from_dict(ai_sdlc_data)

        return ProjectConfig(
            name=project_data.get("name", "Unknown Project"),
            default_branch=project_data.get("default_branch", "develop"),
            release_branch=project_data.get("release_branch", "main"),
            repos=repos,
            codegen_policy=codegen_policy,
            pr_policy=pr_policy,
            routing_rules=routing_rules,
            pr_linking=pr_linking,
            ai_sdlc_config=ai_sdlc_config,
        )

    def _validate_config(self, config: ProjectConfig) -> None:
        """
        Validate project configuration.

        Args:
            config: ProjectConfig to validate

        Raises:
            ValueError: If config is invalid
        """
        # Validate project name
        if not config.name:
            raise ValueError("Project name is required")

        # Validate repos
        if not config.repos:
            raise ValueError("At least one repository must be configured")

        # Validate repo IDs are unique
        repo_ids = [repo.id for repo in config.repos]
        if len(repo_ids) != len(set(repo_ids)):
            raise ValueError("Repository IDs must be unique")

        # Validate branches
        for repo in config.repos:
            if not repo.default_branch:
                raise ValueError(f"Repository {repo.id} must have a default_branch")
            if not repo.release_branch:
                raise ValueError(f"Repository {repo.id} must have a release_branch")

        # Validate routing rules reference valid repos
        for rule in config.routing_rules:
            for repo_id in rule.prefer_repos:
                if not config.get_repo_by_id(repo_id):
                    raise ValueError(f"Routing rule references unknown repo: {repo_id}")

        # Validate LLM config
        valid_providers = ["anthropic", "openai", "azure_openai", "databricks"]
        if config.ai_sdlc_config.llm.provider not in valid_providers:
            raise ValueError(
                f"Invalid LLM provider: {config.ai_sdlc_config.llm.provider}. "
                f"Must be one of: {valid_providers}"
            )

    @property
    def config(self) -> Optional[ProjectConfig]:
        """Get loaded configuration."""
        return self._config

    def reload(self) -> ProjectConfig:
        """Reload configuration from file."""
        return self.load()
