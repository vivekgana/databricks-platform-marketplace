# Project Structure

This document provides an overview of the Databricks Platform Marketplace repository structure.

## Repository Overview

```
databricks-platform-marketplace/
├── .claude-plugin/              # Marketplace configuration
│   └── marketplace.json         # Marketplace manifest
│
├── .github/                     # GitHub configuration
│   └── workflows/
│       └── ci-cd.yml           # CI/CD pipeline
│
├── plugins/                     # Plugin implementations
│   ├── databricks-engineering/ # Core data engineering plugin
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json     # Plugin configuration
│   │   ├── commands/           # Slash commands (15)
│   │   ├── agents/             # Review agents (18)
│   │   ├── skills/             # Reusable patterns (8)
│   │   ├── mcp-servers/        # MCP integrations (3)
│   │   └── templates/          # Project templates
│   │
│   ├── databricks-mlops/       # MLOps extension (optional)
│   └── databricks-governance/  # Governance plugin (optional)
│
├── docs/                        # Documentation
│   ├── getting-started.md      # Quick start guide
│   ├── configuration.md        # Configuration reference
│   ├── commands-reference.md   # Command documentation
│   ├── agents-reference.md     # Agent documentation
│   └── skills-reference.md     # Skills documentation
│
├── examples/                    # Example projects
│   ├── customer-360-pipeline/  # Complete customer 360 example
│   ├── real-time-analytics/    # Streaming analytics
│   └── ml-feature-platform/    # Feature store example
│
├── tests/                       # Test suite
│   ├── unit/                   # Unit tests
│   │   └── test_commands.py
│   ├── integration/            # Integration tests
│   │   └── test_workflows.py
│   └── fixtures/               # Test fixtures
│
├── scripts/                     # Utility scripts
│   └── validate-plugins.js     # Plugin validation
│
├── package.json                 # NPM package configuration
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Dev dependencies
├── pyproject.toml              # Pytest configuration
├── setup.sh                     # Setup script
├── .gitignore                  # Git ignore rules
├── LICENSE                      # MIT License
├── README.md                    # Main README
├── CHANGELOG.md                # Version history
├── CONTRIBUTING.md             # Contribution guide
└── .databricks-plugin-config.example.yaml  # Config template
```

## Key Directories

### `.claude-plugin/`
Contains the marketplace manifest that defines:
- Marketplace metadata
- Plugin listings
- Installation methods
- Requirements

### `plugins/databricks-engineering/`
Core plugin with complete data engineering toolset:

**Commands** (`commands/`):
- Pipeline planning and execution
- Data product management
- Delta Sharing configuration
- Deployment automation
- Cost optimization
- Quality testing

**Agents** (`agents/`):
- Code review specialists
- Performance optimizers
- Security validators
- Governance experts

**Skills** (`skills/`):
- Medallion architecture patterns
- Delta Live Tables templates
- Data quality frameworks
- Testing strategies
- CI/CD workflows

**MCP Servers** (`mcp-servers/`):
- Databricks Workspace API integration
- Unity Catalog metadata access
- Spark query profiling

### `examples/`
Complete, production-ready example projects:
- Full source code
- Tests
- Configuration
- Documentation

### `tests/`
Comprehensive test suite:
- **Unit tests**: Fast, isolated tests
- **Integration tests**: Full workflow tests
- **Fixtures**: Reusable test data

### `docs/`
Complete documentation:
- User guides
- API reference
- Best practices
- Troubleshooting

## File Descriptions

### Root Files

| File | Purpose |
|------|---------|
| `package.json` | NPM package metadata and scripts |
| `requirements.txt` | Python production dependencies |
| `requirements-dev.txt` | Python development dependencies |
| `pyproject.toml` | Python project configuration |
| `setup.sh` | Automated setup script |
| `README.md` | Main documentation |
| `CHANGELOG.md` | Version history |
| `CONTRIBUTING.md` | Contribution guidelines |
| `LICENSE` | MIT license |
| `.gitignore` | Git ignore patterns |

### Configuration Files

| File | Purpose |
|------|---------|
| `.databricks-plugin-config.example.yaml` | Configuration template |
| `.databricks-plugin-config.yaml` | User configuration (gitignored) |

## Plugin Structure

Each plugin follows this structure:

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json             # Plugin metadata
├── commands/                   # Slash commands
│   └── command-name.md
├── agents/                     # Review agents
│   └── agent-name.md
├── skills/                     # Reusable patterns
│   └── skill-name/
│       ├── SKILL.md           # Skill documentation
│       ├── templates/         # Code templates
│       └── examples/          # Usage examples
├── mcp-servers/               # MCP integrations
│   └── server-config.json
├── templates/                 # Project templates
└── README.md                  # Plugin documentation
```

## Command Structure

Commands are defined as markdown files:

```markdown
# Command Name

## Description
Brief description of what the command does

## Usage
```bash
claude /plugin:command-name <args>
```

## Examples
Working examples with explanation

## Related Commands
Links to related commands
```

## Agent Structure

Agents are defined as markdown files with review instructions:

```markdown
# Agent Name

## Role
Description of the agent's expertise

## What to Review
Detailed review criteria

## Common Issues to Flag
Specific patterns to identify

## Example Review Output
Template for review results
```

## Skill Structure

Skills contain reusable patterns:

```
skill-name/
├── SKILL.md                    # Documentation with frontmatter
├── templates/                  # Code templates
│   ├── bronze_layer.py
│   ├── silver_layer.py
│   └── gold_layer.py
├── examples/                   # Complete examples
│   └── example_pipeline.py
└── scripts/                    # Helper scripts (optional)
```

## Testing Structure

Tests are organized by type:

```
tests/
├── unit/                       # Fast, isolated tests
│   ├── test_commands.py
│   ├── test_agents.py
│   └── test_utils.py
├── integration/                # Full workflow tests
│   ├── test_workflows.py
│   └── test_deployment.py
└── fixtures/                   # Shared test data
    ├── conftest.py
    └── sample_data.py
```

## Example Project Structure

Each example follows this pattern:

```
examples/<example-name>/
├── src/                        # Source code
│   ├── __init__.py
│   ├── pipeline.py
│   └── transformations.py
├── tests/                      # Tests
│   ├── __init__.py
│   ├── test_pipeline.py
│   └── test_transformations.py
├── databricks.yml              # Databricks Asset Bundle
├── requirements.txt            # Dependencies
└── README.md                   # Example documentation
```

## Development Workflow

1. **Setup**: Run `./setup.sh`
2. **Develop**: Edit plugins, commands, agents, or skills
3. **Test**: Run `npm test`
4. **Validate**: Run `npm run validate`
5. **Commit**: Follow conventional commits
6. **Push**: CI/CD runs automatically

## Adding New Components

### Adding a Command

1. Create `plugins/<plugin>/commands/new-command.md`
2. Update `plugins/<plugin>/.claude-plugin/plugin.json`
3. Add tests in `tests/unit/`
4. Update documentation in `docs/commands-reference.md`

### Adding an Agent

1. Create `plugins/<plugin>/agents/new-agent.md`
2. Update `plugins/<plugin>/.claude-plugin/plugin.json`
3. Add tests in `tests/unit/`
4. Update documentation in `docs/agents-reference.md`

### Adding a Skill

1. Create directory `plugins/<plugin>/skills/new-skill/`
2. Add `SKILL.md` with frontmatter
3. Add templates and examples
4. Update `plugins/<plugin>/.claude-plugin/plugin.json`
5. Update documentation in `docs/skills-reference.md`

## Maintenance

### Regular Tasks

- Update dependencies: `npm update` and `pip list --outdated`
- Run tests: `npm test`
- Validate plugins: `npm run validate`
- Update documentation
- Review and merge PRs

### Release Process

1. Update `CHANGELOG.md`
2. Bump version in `package.json` and plugin.json files
3. Tag release: `git tag v1.x.x`
4. Push tag: `git push origin v1.x.x`
5. GitHub Actions publishes to NPM

## Resources

- [Claude Code Plugin Spec](https://docs.claude.com/plugins)
- [Databricks Documentation](https://docs.databricks.com)
- [Delta Lake Guide](https://docs.delta.io)

---

Last updated: 2024-01-15
