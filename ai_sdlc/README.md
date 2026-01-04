# AI-SDLC - AI-Driven Software Development Life Cycle

**Version**: 0.1.0 (Phase 1 - Foundation)
**Status**: In Development
**Last Updated**: 2026-01-03

---

## Overview

AI-SDLC is a comprehensive system for automating software development workflows for Databricks platforms using AI-powered code generation, multi-repo awareness, and develop-first branching workflows.

### Key Features

- ✅ **Product Owner-Friendly**: REQ-*.md templates for structured requirements with Given/When/Then acceptance criteria
- ✅ **Multi-Repo Aware**: Intelligent routing across multiple repositories based on content analysis
- ✅ **LLM Integration**: Support for Anthropic Claude, OpenAI GPT-4, Azure OpenAI, and Databricks Foundation Models
- ✅ **Databricks-Native**: Deep understanding of bundles, notebooks, DLT, and Unity Catalog
- ✅ **Develop-First Branching**: PRs to develop branch with gated promotion to main
- 🚧 **Evidence Automation**: PNG/HTML/MD evidence generation (Coming in Phase 2)
- 🚧 **Code Generation**: AI-powered code generation (Coming in Phase 3)

---

## Quick Start

### Installation

```bash
# Clone repository
cd databricks-platform-marketplace/ai_sdlc

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Configuration

Create or update `ai_sdlc/project.yml`:

```yaml
project:
  name: "My Project"
  default_branch: "develop"
  release_branch: "main"

repos:
  - id: "main-repo"
    url: "https://github.com/org/repo.git"
    default_branch: "develop"
    scopes: ["src/", "tests/"]

routing:
  rules:
    - if_contains: ["databricks", "bundle"]
      prefer_repos: ["main-repo"]
```

### Environment Variables

```bash
# LLM Provider (choose one)
export ANTHROPIC_API_KEY="sk-ant-api03-..."  # Recommended
# OR
export OPENAI_API_KEY="sk-..."
# OR
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://..."

# Optional: Custom config path
export AI_SDLC_PROJECT_CONFIG="./ai_sdlc/project.yml"
```

---

## CLI Usage

### Parse Requirements

Parse and validate a REQ-*.md file:

```bash
ai-sdlc parse requirements/REQ-101.md

# With verbose output
ai-sdlc parse requirements/REQ-101.md -v

# Skip validation
ai-sdlc parse requirements/REQ-101.md --no-validate
```

### Route Requirements

Route a requirement to target repositories:

```bash
ai-sdlc route requirements/REQ-101.md

# With custom config
ai-sdlc route requirements/REQ-101.md -c ./custom-project.yml

# With verbose output and suggestions
ai-sdlc route requirements/REQ-101.md -v
```

### Validate Configuration

Validate your project.yml configuration:

```bash
ai-sdlc validate-config

# With verbose output
ai-sdlc validate-config -v
```

### System Information

Display AI-SDLC system information:

```bash
ai-sdlc info
```

---

## Python API Usage

### Load Configuration

```python
from ai_sdlc.core.config_loader import ConfigLoader

loader = ConfigLoader("./ai_sdlc/project.yml")
config = loader.load()

print(f"Project: {config.name}")
print(f"Repos: {[repo.id for repo in config.repos]}")
```

### Parse Requirements

```python
from ai_sdlc.parsers.requirement_parser import RequirementParser

parser = RequirementParser()
requirement = parser.parse_file("requirements/REQ-101.md")

print(f"Requirement: {requirement.req_id}")
print(f"Title: {requirement.title}")
print(f"ACs: {len(requirement.acceptance_criteria)}")

# Validate
errors = parser.validate(requirement)
if errors:
    print(f"Validation errors: {errors}")
```

### Route Requirements

```python
from ai_sdlc.core.config_loader import ConfigLoader
from ai_sdlc.parsers.repo_router import RepoRouter
from ai_sdlc.parsers.requirement_parser import RequirementParser

# Load config
config = ConfigLoader().load()

# Parse requirement
parser = RequirementParser()
requirement = parser.parse_file("requirements/REQ-101.md")

# Route to repos
router = RepoRouter(config)
result = router.route(requirement)

print(f"Target repos: {[repo.id for repo in result.target_repos]}")
print(f"Confidence: {result.confidence:.2%}")
print(f"Reason: {result.routing_reason}")
```

### Use LLM Client

```python
from ai_sdlc.core.llm_client import LLMClient

# Initialize Claude client
client = LLMClient(
    provider="anthropic",
    model="claude-sonnet-4-5",
    temperature=0.2,
    max_tokens=8000
)

# Generate code
response = client.generate(
    prompt="Generate a Python function that validates email addresses",
    system_prompt="You are an expert Python developer"
)

print(response.content)
print(f"Tokens: {response.tokens_used}, Cost: ${response.cost_usd:.4f}")
```

---

## Architecture

### Package Structure

```
ai_sdlc/
├── core/                   # Core engine and configuration
│   ├── config_loader.py    # Load and validate project.yml
│   ├── llm_client.py       # LLM provider abstraction
│   └── context_manager.py  # (Phase 2)
│
├── parsers/                # Requirement and routing parsers
│   ├── requirement_parser.py  # Parse REQ-*.md files
│   └── repo_router.py         # Multi-repo routing logic
│
├── analyzers/              # (Phase 2) Codebase analysis
├── generators/             # (Phase 3) Code generation
├── evidence/               # (Phase 4) Evidence automation
├── workflows/              # (Phase 5) PR workflows
├── integrations/           # (Phase 6) DevOps integration
│
├── cli/                    # Command-line interface
│   └── commands.py
│
└── tests/                  # Unit and integration tests
    ├── unit/
    └── integration/
```

### Phase 1 Components (Implemented)

1. **ConfigLoader** (`core/config_loader.py`)
   - Loads project.yml configuration
   - Validates repos, routing rules, and policies
   - Manages AI-SDLC settings

2. **LLMClient** (`core/llm_client.py`)
   - Abstraction for multiple LLM providers
   - Supports Claude, GPT-4, Azure OpenAI, Databricks
   - Token tracking and cost estimation

3. **RequirementParser** (`parsers/requirement_parser.py`)
   - Parses REQ-*.md files with YAML frontmatter
   - Extracts Given/When/Then acceptance criteria
   - Validates requirement completeness

4. **RepoRouter** (`parsers/repo_router.py`)
   - Routes requirements to target repositories
   - Content-based routing with heuristics
   - Confidence scoring and validation

5. **CLI** (`cli/commands.py`)
   - Commands: parse, route, validate-config, info
   - User-friendly output with colors
   - Verbose mode for debugging

---

## Testing

### Run All Tests

```bash
# Run unit tests
pytest ai_sdlc/tests/unit/ -v

# Run with coverage
pytest ai_sdlc/tests/unit/ --cov=ai_sdlc --cov-report=html

# Run specific test file
pytest ai_sdlc/tests/unit/test_config_loader.py -v
```

### Test Coverage

Current test coverage for Phase 1 components:

- `config_loader.py`: 90%+ coverage
- `requirement_parser.py`: 95%+ coverage
- `repo_router.py`: 90%+ coverage
- `llm_client.py`: 85%+ coverage (limited by API mocking)

---

## Development

### Code Formatting

```bash
# Format code with Black
black ai_sdlc/

# Check with Pylint
pylint ai_sdlc/ --disable=C0111,R0913

# Type checking with MyPy
mypy ai_sdlc/ --ignore-missing-imports
```

### Adding New Features

1. Create feature branch: `git checkout -b feature/your-feature`
2. Implement feature with tests
3. Format code: `black ai_sdlc/`
4. Run tests: `pytest -v`
5. Create PR to `develop` branch

---

## Roadmap

### Phase 1: Foundation (Weeks 1-2) ✅ COMPLETE

- ✅ Configuration loading
- ✅ Requirement parsing
- ✅ Multi-repo routing
- ✅ LLM client
- ✅ Basic CLI
- ✅ Unit tests

### Phase 2: Analysis (Weeks 3-4) 🚧 NEXT

- ⬜ Codebase analyzer
- ⬜ Databricks scanner
- ⬜ Pattern detector
- ⬜ Context manager

### Phase 3: Generation (Weeks 5-6)

- ⬜ Code generator
- ⬜ Databricks generator
- ⬜ Test generator
- ⬜ Template manager

### Phase 4: Evidence (Weeks 7-8)

- ⬜ Evidence orchestrator
- ⬜ Notebook generator
- ⬜ Job configurator
- ⬜ Artifact collector

### Phase 5: PR Workflow (Weeks 9-10)

- ⬜ Branch manager
- ⬜ PR manager
- ⬜ CI validator
- ⬜ Approval workflow

### Phase 6: DevOps Integration (Weeks 11-12)

- ⬜ DevOps bridge
- ⬜ JIRA integration
- ⬜ Azure DevOps integration
- ⬜ Velocity tracking

---

## Documentation

- [Implementation Plan](../AI_SDLC_IMPLEMENTATION_PLAN.md) - Complete 16-week plan
- [Design Document](../docs/AI_SDLC_DESIGN.md) - Design philosophy
- [Requirements Template](../requirements/REQ-TEMPLATE.md) - REQ-*.md format
- [Project Configuration](./project.yml) - Multi-repo config

---

## Support

For issues, questions, or contributions:

- **GitHub Issues**: [databricks-platform-marketplace/issues](https://github.com/vivekgana/databricks-platform-marketplace/issues)
- **Documentation**: See `docs/` directory
- **Examples**: See `requirements/` directory for sample REQ-*.md files

---

## License

[Your License Here]

---

**Prepared by**: Databricks Platform Team
**Date**: 2026-01-03
