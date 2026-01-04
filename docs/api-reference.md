# API Reference

**Document Version:** 1.0
**Last Updated:** 2026-01-04 00:33:20
**Prepared by:** Databricks Platform Team

---

## Overview

This reference documents the Python APIs for the Databricks Platform Marketplace, including AI-SDLC components, DevOps integrations, and plugin interfaces.

## AI-SDLC Python API

### Configuration Loader

Load and validate AI-SDLC project configuration.

#### ConfigLoader

**Location:** `ai_sdlc.core.config_loader`

```python
from ai_sdlc.core.config_loader import ConfigLoader, ProjectConfig

# Load configuration
loader = ConfigLoader("./ai_sdlc/project.yml")
config = loader.load()

# Access configuration
print(config.project.name)
print(config.project.default_branch)
print(config.repos[0].id)
```

**Class: ConfigLoader**

```python
class ConfigLoader:
    """Load and validate AI-SDLC configuration."""

    def __init__(self, config_path: str):
        """Initialize with path to project.yml"""
        pass

    def load(self) -> ProjectConfig:
        """Load and validate configuration"""
        pass

    def validate(self) -> List[str]:
        """Validate configuration, return errors"""
        pass
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `config_path: str` | None | Initialize loader with config file path |
| `load` | None | `ProjectConfig` | Load and parse configuration |
| `validate` | None | `List[str]` | Validate config, return error messages |

**Exceptions:**
- `FileNotFoundError` - Configuration file not found
- `yaml.YAMLError` - Invalid YAML syntax
- `ValidationError` - Configuration validation failed

#### ProjectConfig

```python
@dataclass
class ProjectConfig:
    """Complete project configuration."""

    project: ProjectSettings
    repos: List[RepoConfig]
    routing: RoutingConfig
    pr_linking: PRLinkingConfig
    codegen: CodegenConfig
    ai_sdlc_config: Optional[AISDLCConfig] = None
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `project` | `ProjectSettings` | Project metadata (name, branches) |
| `repos` | `List[RepoConfig]` | Repository configurations |
| `routing` | `RoutingConfig` | Routing rules for requirements |
| `pr_linking` | `PRLinkingConfig` | PR creation settings |
| `codegen` | `CodegenConfig` | Code generation policies |
| `ai_sdlc_config` | `AISDLCConfig` | AI-SDLC specific settings |

#### RepoConfig

```python
@dataclass
class RepoConfig:
    """Configuration for a single repository."""

    id: str
    url: str
    default_branch: str
    release_branch: str
    scopes: List[str]
    signals: Dict[str, str]
    ci: Dict[str, Any]
    deploy: Dict[str, Any]

    def matches_scope(self, file_path: str) -> bool:
        """Check if file path matches repo scopes."""
        pass
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `matches_scope` | `file_path: str` | `bool` | Check if file matches repo scope |
| `from_dict` | `data: Dict` | `RepoConfig` | Create from dictionary |

---

### LLM Client

Universal client for multiple LLM providers.

#### LLMClient

**Location:** `ai_sdlc.core.llm_client`

```python
from ai_sdlc.core.llm_client import LLMClient, LLMResponse

# Initialize client
client = LLMClient(
    provider="anthropic",
    model="claude-sonnet-4-5",
    temperature=0.2,
    max_tokens=8000
)

# Generate response
response = client.generate(
    prompt="Generate Python code for email validation",
    system_prompt="You are an expert Python developer"
)

print(response.content)
print(f"Tokens: {response.tokens_used}")
print(f"Cost: ${response.cost_usd:.4f}")
```

**Class: LLMClient**

```python
class LLMClient:
    """Universal LLM client supporting multiple providers."""

    def __init__(
        self,
        provider: str = "anthropic",
        model: str = "claude-sonnet-4-5",
        temperature: float = 0.2,
        max_tokens: int = 8000,
        timeout_seconds: int = 120
    ):
        """Initialize LLM client."""
        pass

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate LLM response."""
        pass

    def estimate_cost(self, tokens: int) -> float:
        """Estimate cost for token count."""
        pass
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | See constructor | None | Initialize with provider config |
| `generate` | `prompt: str, system_prompt: str, max_tokens: int` | `LLMResponse` | Generate response |
| `estimate_cost` | `tokens: int` | `float` | Estimate cost in USD |

**Supported Providers:**

| Provider | Models | Environment Variable |
|----------|--------|---------------------|
| `anthropic` | claude-sonnet-4-5, claude-opus-4-5 | `ANTHROPIC_API_KEY` |
| `openai` | gpt-4-turbo, gpt-4, gpt-3.5-turbo | `OPENAI_API_KEY` |
| `azure_openai` | gpt-4-turbo | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` |
| `databricks` | databricks-meta-llama-* | `DATABRICKS_HOST`, `DATABRICKS_TOKEN` |

#### LLMResponse

```python
@dataclass
class LLMResponse:
    """LLM response with metadata."""

    content: str              # Generated content
    tokens_used: int          # Total tokens used
    cost_usd: float          # Estimated cost in USD
    model: str               # Model used
    provider: str            # Provider used
    duration_seconds: float  # Request duration
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `content` | `str` | Generated text content |
| `tokens_used` | `int` | Total tokens consumed |
| `cost_usd` | `float` | Estimated cost in USD |
| `model` | `str` | Model identifier |
| `provider` | `str` | Provider name |
| `duration_seconds` | `float` | Request duration |

**Exceptions:**
- `ValueError` - Invalid provider or model
- `EnvironmentError` - Missing API key
- `TimeoutError` - Request timeout exceeded
- `RateLimitError` - Rate limit exceeded

---

### Requirement Parser

Parse REQ-*.md requirements with YAML frontmatter.

#### RequirementParser

**Location:** `ai_sdlc.parsers.requirement_parser`

```python
from ai_sdlc.parsers.requirement_parser import RequirementParser, Requirement

# Parse requirement file
parser = RequirementParser()
requirement = parser.parse_file("requirements/REQ-101.md")

# Access requirement data
print(requirement.req_id)
print(requirement.title)
print(requirement.acceptance_criteria)
print(requirement.verification_methods)
```

**Class: RequirementParser**

```python
class RequirementParser:
    """Parse REQ-*.md files with YAML frontmatter."""

    def parse_file(self, file_path: str) -> Requirement:
        """Parse requirement from file."""
        pass

    def parse_content(self, content: str) -> Requirement:
        """Parse requirement from string content."""
        pass

    def validate(self, requirement: Requirement) -> List[str]:
        """Validate requirement, return errors."""
        pass
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `parse_file` | `file_path: str` | `Requirement` | Parse requirement file |
| `parse_content` | `content: str` | `Requirement` | Parse requirement string |
| `validate` | `requirement: Requirement` | `List[str]` | Validate requirement |

#### Requirement

```python
@dataclass
class Requirement:
    """Parsed requirement with metadata."""

    req_id: str                          # REQ-101
    title: str                           # Requirement title
    description: str                     # Full description
    acceptance_criteria: List[AcceptanceCriterion]
    verification_methods: List[VerificationMethod]
    target_repos: List[str]              # Explicit repo targets
    demo_evidence: Optional[DemoEvidence]
    metadata: Dict[str, Any]             # Additional frontmatter
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `req_id` | `str` | Requirement ID (REQ-###) |
| `title` | `str` | Requirement title |
| `description` | `str` | Full description text |
| `acceptance_criteria` | `List[AcceptanceCriterion]` | Given/When/Then criteria |
| `verification_methods` | `List[VerificationMethod]` | Test/job/query/manual |
| `target_repos` | `List[str]` | Explicit repository targets |
| `demo_evidence` | `DemoEvidence` | Demo evidence specification |
| `metadata` | `Dict` | Additional metadata |

#### AcceptanceCriterion

```python
@dataclass
class AcceptanceCriterion:
    """Given/When/Then acceptance criterion."""

    given: str    # Given condition
    when: str     # When action
    then: str     # Then expected result
```

#### VerificationMethod

```python
@dataclass
class VerificationMethod:
    """Verification method specification."""

    method_type: str  # test, job, query, manual
    description: str  # Method description
    details: Dict     # Method-specific details
```

**Exceptions:**
- `FileNotFoundError` - Requirement file not found
- `yaml.YAMLError` - Invalid YAML frontmatter
- `ValidationError` - Requirement validation failed

---

### Repository Router

Route requirements to repositories based on content.

#### RepoRouter

**Location:** `ai_sdlc.parsers.repo_router`

```python
from ai_sdlc.parsers.repo_router import RepoRouter, RoutingResult

# Initialize router
router = RepoRouter(config)

# Route requirement
result = router.route(requirement)

print(f"Target repos: {[r.id for r in result.target_repos]}")
print(f"Confidence: {result.confidence:.2%}")
print(f"Strategy: {result.strategy}")
```

**Class: RepoRouter**

```python
class RepoRouter:
    """Route requirements to repositories."""

    def __init__(self, config: ProjectConfig):
        """Initialize with project configuration."""
        pass

    def route(self, requirement: Requirement) -> RoutingResult:
        """Route requirement to repositories."""
        pass

    def validate_routing(self, result: RoutingResult) -> List[str]:
        """Validate routing result."""
        pass
```

**Methods:**

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `config: ProjectConfig` | None | Initialize router |
| `route` | `requirement: Requirement` | `RoutingResult` | Route to repos |
| `validate_routing` | `result: RoutingResult` | `List[str]` | Validate routing |

#### RoutingResult

```python
@dataclass
class RoutingResult:
    """Routing decision result."""

    target_repos: List[RepoConfig]  # Target repositories
    confidence: float                # 0.0-1.0 confidence score
    strategy: str                    # explicit, content_based, fallback
    matched_keywords: List[str]      # Keywords matched
    suggestions: List[str]           # Improvement suggestions
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `target_repos` | `List[RepoConfig]` | Target repositories |
| `confidence` | `float` | Routing confidence (0.0-1.0) |
| `strategy` | `str` | Routing strategy used |
| `matched_keywords` | `List[str]` | Matched routing keywords |
| `suggestions` | `List[str]` | Routing improvements |

**Routing Strategies:**

| Strategy | Confidence | Description |
|----------|-----------|-------------|
| `explicit` | 1.0 | Repos specified in requirement |
| `content_based` | 0.7-1.0 | Matched by content keywords |
| `fallback` | 0.3 | Routed to all repos |

---

## DevOps Integration API

### Plugin SDK Base

Base interface for DevOps plugins.

#### BasePlugin

**Location:** `plugins.databricks_devops_integrations.sdk.base_plugin`

```python
from plugins.databricks_devops_integrations.sdk.base_plugin import BasePlugin, WorkItem

class CustomPlugin(BasePlugin):
    """Custom DevOps plugin."""

    def create_work_item(self, **kwargs) -> WorkItem:
        """Create work item."""
        pass

    def get_work_item(self, item_id: str) -> WorkItem:
        """Get work item by ID."""
        pass

    def update_work_item(self, item_id: str, **kwargs) -> WorkItem:
        """Update work item."""
        pass
```

**Class: BasePlugin (Abstract)**

```python
class BasePlugin(ABC):
    """Base class for DevOps plugins."""

    @abstractmethod
    def create_work_item(self, **kwargs) -> WorkItem:
        """Create work item."""
        pass

    @abstractmethod
    def get_work_item(self, item_id: str) -> WorkItem:
        """Get work item."""
        pass

    @abstractmethod
    def update_work_item(self, item_id: str, **kwargs) -> WorkItem:
        """Update work item."""
        pass

    @abstractmethod
    def search_work_items(self, query: str) -> List[WorkItem]:
        """Search work items."""
        pass
```

**Abstract Methods:**

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `create_work_item` | `**kwargs` | `WorkItem` | Create new work item |
| `get_work_item` | `item_id: str` | `WorkItem` | Get work item by ID |
| `update_work_item` | `item_id: str, **kwargs` | `WorkItem` | Update work item |
| `search_work_items` | `query: str` | `List[WorkItem]` | Search work items |

#### WorkItem

```python
@dataclass
class WorkItem:
    """Universal work item model."""

    id: str                    # Work item ID
    title: str                 # Title
    description: str           # Description
    status: str               # Status (New, In Progress, Done)
    assigned_to: Optional[str] # Assignee
    created_date: str         # Creation date
    updated_date: str         # Last update date
    work_item_type: str       # Type (Bug, Task, Feature)
    priority: Optional[str]   # Priority
    tags: List[str]           # Tags
    custom_fields: Dict       # Custom fields
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Work item identifier |
| `title` | `str` | Work item title |
| `description` | `str` | Full description |
| `status` | `str` | Current status |
| `assigned_to` | `str` | Assignee username/email |
| `created_date` | `str` | Creation timestamp |
| `updated_date` | `str` | Last update timestamp |
| `work_item_type` | `str` | Type (Bug, Task, Feature) |
| `priority` | `str` | Priority level |
| `tags` | `List[str]` | Associated tags |
| `custom_fields` | `Dict` | Custom field values |

---

### JIRA Plugin

JIRA Cloud and Server integration.

#### JIRAPlugin

**Location:** `plugins.databricks_devops_integrations.integrations.jira.jira_plugin`

```python
from plugins.databricks_devops_integrations.integrations.jira.jira_plugin import JIRAPlugin

# Initialize plugin
plugin = JIRAPlugin(
    jira_url="https://company.atlassian.net",
    email="user@company.com",
    api_token="your-token",
    project_key="PROJ"
)

# Create issue
issue = plugin.create_work_item(
    title="New Feature Request",
    description="Implement user authentication",
    work_item_type="Story",
    priority="High"
)

# Search issues
issues = plugin.search_work_items("project = PROJ AND status = 'In Progress'")
```

**Class: JIRAPlugin**

```python
class JIRAPlugin(BasePlugin):
    """JIRA integration plugin."""

    def __init__(
        self,
        jira_url: str,
        email: str,
        api_token: str,
        project_key: str
    ):
        """Initialize JIRA plugin."""
        pass

    def create_work_item(self, **kwargs) -> WorkItem:
        """Create JIRA issue."""
        pass

    def get_work_item(self, item_id: str) -> WorkItem:
        """Get JIRA issue."""
        pass

    def search_work_items(self, jql: str) -> List[WorkItem]:
        """Search with JQL query."""
        pass

    def transition_issue(self, item_id: str, transition_name: str) -> WorkItem:
        """Transition issue status."""
        pass
```

**Additional Methods:**

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `transition_issue` | `item_id: str, transition_name: str` | `WorkItem` | Change issue status |
| `add_comment` | `item_id: str, comment: str` | None | Add comment to issue |
| `get_transitions` | `item_id: str` | `List[Dict]` | Get available transitions |

**Environment Variables:**
- `JIRA_URL` - JIRA instance URL
- `JIRA_EMAIL` - User email
- `JIRA_API_TOKEN` - API token
- `JIRA_PROJECT` - Project key

---

### Azure DevOps Plugin

Azure Boards integration.

#### AzureDevOpsPlugin

**Location:** `plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin`

```python
from plugins.databricks_devops_integrations.integrations.azure_devops.azure_devops_plugin import AzureDevOpsPlugin

# Initialize plugin
plugin = AzureDevOpsPlugin(
    organization_url="https://dev.azure.com/myorg",
    personal_access_token="your-pat",
    project="MyProject"
)

# Create work item
item = plugin.create_work_item(
    title="Implement API endpoint",
    description="Create REST API for user management",
    work_item_type="User Story",
    tags=["api", "backend"]
)

# Query work items
items = plugin.search_work_items(
    "SELECT [System.Id], [System.Title] FROM WorkItems WHERE [System.State] = 'Active'"
)
```

**Class: AzureDevOpsPlugin**

```python
class AzureDevOpsPlugin(BasePlugin):
    """Azure DevOps integration plugin."""

    def __init__(
        self,
        organization_url: str,
        personal_access_token: str,
        project: str
    ):
        """Initialize Azure DevOps plugin."""
        pass

    def create_work_item(self, **kwargs) -> WorkItem:
        """Create work item."""
        pass

    def get_work_item(self, item_id: str) -> WorkItem:
        """Get work item."""
        pass

    def search_work_items(self, wiql: str) -> List[WorkItem]:
        """Search with WIQL query."""
        pass

    def update_work_item_state(self, item_id: str, state: str) -> WorkItem:
        """Update work item state."""
        pass
```

**Additional Methods:**

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `update_work_item_state` | `item_id: str, state: str` | `WorkItem` | Change item state |
| `link_work_items` | `source_id: str, target_id: str, link_type: str` | None | Link work items |
| `get_work_item_updates` | `item_id: str` | `List[Dict]` | Get update history |

**Environment Variables:**
- `AZURE_DEVOPS_ORG_URL` - Organization URL
- `AZURE_DEVOPS_PAT` - Personal access token
- `AZURE_DEVOPS_PROJECT` - Project name

---

## Plugin Extension API

### Creating Custom Plugins

Extend the plugin system with custom integrations.

```python
from plugins.databricks_devops_integrations.sdk.base_plugin import BasePlugin, WorkItem

class GitHubPlugin(BasePlugin):
    """GitHub Issues integration."""

    def __init__(self, token: str, repo: str):
        self.token = token
        self.repo = repo
        self.client = github.Github(token)

    def create_work_item(self, **kwargs) -> WorkItem:
        """Create GitHub issue."""
        repo = self.client.get_repo(self.repo)
        issue = repo.create_issue(
            title=kwargs["title"],
            body=kwargs["description"],
            labels=kwargs.get("tags", [])
        )
        return self._to_work_item(issue)

    def get_work_item(self, item_id: str) -> WorkItem:
        """Get GitHub issue."""
        repo = self.client.get_repo(self.repo)
        issue = repo.get_issue(int(item_id))
        return self._to_work_item(issue)

    def _to_work_item(self, issue) -> WorkItem:
        """Convert GitHub issue to WorkItem."""
        return WorkItem(
            id=str(issue.number),
            title=issue.title,
            description=issue.body or "",
            status=issue.state,
            assigned_to=issue.assignee.login if issue.assignee else None,
            created_date=issue.created_at.isoformat(),
            updated_date=issue.updated_at.isoformat(),
            work_item_type="Issue",
            tags=[label.name for label in issue.labels],
            custom_fields={}
        )
```

---

## Related Documentation

- [Configuration Reference](configuration.md)
- [Commands Reference](commands-reference.md)
- [Agents Reference](agents-reference.md)
- [Skills Reference](skills-reference.md)
- [Getting Started Guide](getting-started.md)

---

**Prepared by:** Databricks Platform Team
**Contact:** data-platform@vivekgana.com
