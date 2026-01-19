# deploy-marketplace

Deploy the Databricks DevOps Integrations plugin from the Claude Marketplace.

## Usage

```
# Add marketplace then install
claude /plugin marketplace add https://github.com/vivekgana/databricks-platform-marketplace
claude /plugin install databricks-devops-integrations
```

## Steps
1) Ensure Claude CLI is installed (`claude --version`).
2) Add the marketplace and install the plugin.
3) Follow verification steps in docs/deployment/MARKETPLACE_DEPLOYMENT.md.

## Outputs
- Plugin installed under `~/.claude/plugins/databricks-devops-integrations`.
- Confirmation of install and available integrations (JIRA, Azure DevOps).
