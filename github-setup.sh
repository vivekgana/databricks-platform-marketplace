#!/bin/bash

# GitHub Setup Script for Databricks Platform Marketplace
# This script uses GitHub CLI (gh) to create and push the repository

set -e

echo "🚀 Setting up GitHub repository..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "${RED}❌ GitHub CLI (gh) is not installed.${NC}"
    echo ""
    echo "Install it with:"
    echo "  macOS:   brew install gh"
    echo "  Linux:   curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
    echo "  Windows: winget install --id GitHub.cli"
    echo ""
    echo "Or visit: https://cli.github.com/"
    exit 1
fi

echo "✅ GitHub CLI found"

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "${YELLOW}⚠️  Not authenticated with GitHub${NC}"
    echo "Authenticating..."
    gh auth login
fi

echo "✅ Authenticated with GitHub"
echo ""

# Get repository details
read -p "Enter repository name (default: databricks-platform-marketplace): " REPO_NAME
REPO_NAME=${REPO_NAME:-databricks-platform-marketplace}

read -p "Enter repository description (default: Enterprise Databricks data platform plugins for Claude Code): " REPO_DESC
REPO_DESC=${REPO_DESC:-"Enterprise Databricks data platform plugins for Claude Code"}

read -p "Make repository public? (y/n, default: y): " IS_PUBLIC
IS_PUBLIC=${IS_PUBLIC:-y}

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo ""
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: Databricks Platform Marketplace v1.0.0

- Added Databricks Engineering Plugin with 15 commands
- Added 18 specialized agents for code review
- Added 8 reusable skills and templates
- Added comprehensive test suite
- Added CI/CD workflows
- Added documentation and examples"
    echo "✅ Git repository initialized"
fi

# Create GitHub repository
echo ""
echo "🌐 Creating GitHub repository..."

if [ "$IS_PUBLIC" = "y" ]; then
    gh repo create "$REPO_NAME" \
        --description "$REPO_DESC" \
        --public \
        --source=. \
        --remote=origin \
        --push
else
    gh repo create "$REPO_NAME" \
        --description "$REPO_DESC" \
        --private \
        --source=. \
        --remote=origin \
        --push
fi

echo ""
echo "${GREEN}✅ Repository created and pushed!${NC}"
echo ""

# Get repository URL
REPO_URL=$(gh repo view --json url -q .url)
echo "📍 Repository URL: $REPO_URL"
echo ""

# Set up GitHub Pages for documentation
echo "📚 Setting up GitHub Pages..."
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/$(gh repo view --json owner,name -q '.owner.login + "/" + .name')/pages" \
  -f source[branch]=main \
  -f source[path]=/docs \
  2>/dev/null || echo "${YELLOW}⚠️  GitHub Pages setup requires manual configuration${NC}"

# Create labels for issues
echo ""
echo "🏷️  Creating issue labels..."
gh label create "bug" --color "d73a4a" --description "Something isn't working" --force
gh label create "enhancement" --color "a2eeef" --description "New feature or request" --force
gh label create "documentation" --color "0075ca" --description "Documentation improvements" --force
gh label create "good first issue" --color "7057ff" --description "Good for newcomers" --force
gh label create "help wanted" --color "008672" --description "Extra attention needed" --force

echo "✅ Labels created"

# Set repository topics
echo ""
echo "🏷️  Adding repository topics..."
gh repo edit --add-topic databricks,data-engineering,claude,ai,mlops,delta-lake,pyspark

echo ""
echo "${GREEN}✅ GitHub setup complete!${NC}"
echo ""
echo "📋 Next steps:"
echo "  1. Configure GitHub secrets for CI/CD:"
echo "     gh secret set NPM_TOKEN"
echo "     gh secret set DATABRICKS_HOST"
echo "     gh secret set DATABRICKS_TOKEN"
echo ""
echo "  2. View your repository:"
echo "     gh repo view --web"
echo ""
echo "  3. Install the plugin:"
echo "     claude /plugin marketplace add $REPO_URL"
echo "     claude /plugin install databricks-engineering"
echo ""
echo "  4. (Optional) Publish to NPM:"
echo "     npm login"
echo "     npm publish --access public"
echo ""
echo "Happy coding! 🎉"
