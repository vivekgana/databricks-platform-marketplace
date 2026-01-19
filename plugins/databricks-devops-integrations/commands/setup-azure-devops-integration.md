# setup-azure-devops-integration

Configure the DevOps integrations plugin to use Azure DevOps Boards for work management.

## Usage

```
claude /devops:setup-azure --org-url https://dev.azure.com/your-org --project YourProject --pat $AZURE_DEVOPS_PAT
```

## Prerequisites
- Azure DevOps org URL, project name, and PAT (see ../docs/setup/AZURE_PAT_SETUP.md)

## Steps
1) Export env vars: `AZURE_DEVOPS_ORG_URL`, `AZURE_DEVOPS_PAT`, `AZURE_DEVOPS_PROJECT`.
2) Run the command to create/update `.databricks-devops-config.yaml`.
3) Validate by creating a test work item or syncing an existing one.

## Outputs
- Stores Azure DevOps settings in the plugin config.
- Returns a connection check result and project info.
