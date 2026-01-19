# setup-jira-integration

Configure the DevOps integrations plugin to use Atlassian JIRA for work management.

## Usage

```
claude /devops:setup-jira --project PROJ --email you@company.com --token $JIRA_API_TOKEN --url https://your-company.atlassian.net
```

## Prerequisites
- JIRA URL, user email, and API token (see ../docs/setup/JIRA_TOKEN_SETUP.md)
- Project key (e.g., `PROJ`)

## Steps
1) Export env vars: `JIRA_URL`, `JIRA_API_TOKEN`, `JIRA_EMAIL`, `JIRA_PROJECT`.
2) Run the command; the plugin writes config to `.databricks-devops-config.yaml`.
3) Validate connectivity by creating a test work item (see examples/investment-asset-plan).

## Outputs
- Creates/updates the JIRA section in the plugin config.
- Returns a connection check status and the project key in use.
