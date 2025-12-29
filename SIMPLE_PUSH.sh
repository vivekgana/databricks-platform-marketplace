#!/bin/bash

# Simple Git Push to GitHub
# No API calls, no GitHub CLI - Pure Git only!
# Your token is embedded below

set -e

# Your GitHub token
TOKEN="11ABBPU2I0fUeTiiafGmfH_oq44HhOy1LGWFGcgc088aIXv0FKIYEl1dXBHWDjmysbHJRYV7UUjYDhS5JB"

echo "╔════════════════════════════════════════════════════════╗"
echo "║   Push to GitHub - Pure Git Method                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Get username
read -p "Enter your GitHub username: " USERNAME
if [ -z "$USERNAME" ]; then
    echo "Error: Username required"
    exit 1
fi

# Set repository name
REPO="databricks-platform-marketplace"

echo ""
echo "Configuration:"
echo "  User: $USERNAME"
echo "  Repo: $REPO"
echo ""
read -p "Continue? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    exit 0
fi

echo ""
echo "Step 1: Initialize Git..."
if [ ! -d ".git" ]; then
    git init
    git config user.name "$USERNAME"
    git config user.email "$USERNAME@users.noreply.github.com"
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

echo ""
echo "Step 2: Create initial commit..."
git add .
git commit -m "Initial commit: Databricks Platform Marketplace v1.0.0

Features:
- 15 commands for data engineering workflows
- 18 specialized agents for code review
- 8 reusable skills and templates
- Complete test suite with pytest
- CI/CD with GitHub Actions
- Delta Sharing and data products
- Cost optimization tools
- Comprehensive documentation" 2>/dev/null || echo "✅ Already committed"

echo ""
echo "Step 3: Set main branch..."
git branch -M main
echo "✅ Main branch set"

echo ""
echo "Step 4: Add remote with authentication..."
REMOTE_URL="https://${TOKEN}@github.com/${USERNAME}/${REPO}.git"
if git remote get-url origin &>/dev/null; then
    git remote set-url origin "$REMOTE_URL"
else
    git remote add origin "$REMOTE_URL"
fi
echo "✅ Remote configured"

echo ""
echo "============================================"
echo "⚠️  IMPORTANT: Create Repository First! ⚠️"
echo "============================================"
echo ""
echo "Before pushing, you MUST create the repository on GitHub:"
echo ""
echo "1. Go to: https://github.com/new"
echo "2. Repository name: $REPO"
echo "3. Description: Enterprise Databricks data platform plugins for Claude Code"
echo "4. Visibility: Public (recommended for marketplace)"
echo "5. DO NOT check 'Initialize with README'"
echo "6. Click 'Create repository'"
echo ""
read -p "Have you created the repository? (y/n): " CREATED
if [ "$CREATED" != "y" ]; then
    echo ""
    echo "Please create the repository first, then run this script again."
    exit 0
fi

echo ""
echo "Step 5: Pushing to GitHub..."
echo "This may take a minute..."

if git push -u origin main; then
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║   ✅ SUCCESS! Repository pushed to GitHub!            ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "📍 Your repository: https://github.com/$USERNAME/$REPO"
    echo ""
    echo "🎯 Next Steps:"
    echo ""
    echo "1. Install the plugin:"
    echo "   claude /plugin marketplace add https://github.com/$USERNAME/$REPO"
    echo "   claude /plugin install databricks-engineering"
    echo ""
    echo "2. Test it:"
    echo "   claude /databricks:plan-pipeline 'test pipeline'"
    echo ""
    echo "3. Configure GitHub secrets (optional, for CI/CD):"
    echo "   https://github.com/$USERNAME/$REPO/settings/secrets/actions"
    echo ""
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo ""
    echo "1. Repository doesn't exist - create it at https://github.com/new"
    echo "2. Token lacks permissions - needs 'repo' scope"
    echo "3. Repository already has content - try: git push -u origin main --force"
    echo ""
    read -p "Try force push? (y/n): " FORCE
    if [ "$FORCE" = "y" ]; then
        git push -u origin main --force && echo "✅ Force push succeeded!"
    fi
fi

echo ""
echo "Cleaning up credentials..."
git remote set-url origin "https://github.com/$USERNAME/$REPO.git"
echo "✅ Token removed from git config"
echo ""
echo "Done! 🎉"
