#!/bin/bash

# GitHub Setup Script using Git with Token Authentication
# No GitHub CLI required!

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

clear
echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║   GitHub Setup - Token Authentication                 ║"
echo "║   Databricks Platform Marketplace                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Git found${NC}"
echo ""

# Get GitHub credentials
echo -e "${CYAN}📝 GitHub Repository Details${NC}"
echo ""

read -p "Enter your GitHub username: " GITHUB_USER
if [ -z "$GITHUB_USER" ]; then
    echo -e "${RED}Error: Username required${NC}"
    exit 1
fi

read -p "Enter your GitHub token (input hidden): " -s GITHUB_TOKEN
echo ""
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}Error: Token required${NC}"
    exit 1
fi

read -p "Enter repository name (default: databricks-platform-marketplace): " REPO_NAME
REPO_NAME=${REPO_NAME:-databricks-platform-marketplace}

read -p "Repository visibility - public or private (default: public): " VISIBILITY
VISIBILITY=${VISIBILITY:-public}

echo ""
echo -e "${CYAN}📦 Repository Configuration${NC}"
echo "  Username:   $GITHUB_USER"
echo "  Repository: $REPO_NAME"
echo "  Visibility: $VISIBILITY"
echo "  Token:      $(echo $GITHUB_TOKEN | head -c 10)..."
echo ""

read -p "Continue? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo -e "${CYAN}🚀 Setting up repository...${NC}"
echo ""

# Initialize git if not already done
if [ ! -d ".git" ]; then
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
    echo -e "${GREEN}✅ Git repository initialized${NC}"
else
    echo -e "${GREEN}✅ Git repository already initialized${NC}"
fi

# Configure git user if needed
if [ -z "$(git config user.name)" ]; then
    git config user.name "$GITHUB_USER"
    git config user.email "$GITHUB_USER@users.noreply.github.com"
    echo -e "${GREEN}✅ Git user configured${NC}"
fi

# Set main branch
git branch -M main
echo -e "${GREEN}✅ Main branch set${NC}"

# Create repository on GitHub using API
echo ""
echo "🌐 Creating repository on GitHub..."

CREATE_RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "{
    \"name\": \"$REPO_NAME\",
    \"description\": \"Enterprise Databricks data platform plugins for Claude Code\",
    \"private\": $([ "$VISIBILITY" = "private" ] && echo "true" || echo "false"),
    \"has_issues\": true,
    \"has_projects\": false,
    \"has_wiki\": false,
    \"auto_init\": false
  }")

# Check if repository was created successfully
if echo "$CREATE_RESPONSE" | grep -q "\"full_name\""; then
    echo -e "${GREEN}✅ Repository created on GitHub${NC}"
    REPO_URL=$(echo "$CREATE_RESPONSE" | grep -o '"html_url": *"[^"]*"' | sed 's/"html_url": *"//' | sed 's/"//')
    echo "   URL: $REPO_URL"
elif echo "$CREATE_RESPONSE" | grep -q "\"name already exists\""; then
    echo -e "${YELLOW}⚠️  Repository already exists on GitHub${NC}"
    REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME"
else
    echo -e "${RED}❌ Failed to create repository${NC}"
    echo "Response: $CREATE_RESPONSE"
    exit 1
fi

# Add remote with token authentication
echo ""
echo "🔗 Configuring remote..."

REMOTE_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${REPO_NAME}.git"

if git remote get-url origin &> /dev/null; then
    git remote set-url origin "$REMOTE_URL"
    echo -e "${GREEN}✅ Remote updated${NC}"
else
    git remote add origin "$REMOTE_URL"
    echo -e "${GREEN}✅ Remote added${NC}"
fi

# Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."

if git push -u origin main; then
    echo -e "${GREEN}✅ Code pushed to GitHub${NC}"
else
    echo -e "${YELLOW}⚠️  Push may have failed, trying force push...${NC}"
    git push -u origin main --force
fi

# Update repository settings via API
echo ""
echo "⚙️  Configuring repository settings..."

# Add topics
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME/topics" \
  -d '{"names":["databricks","data-engineering","claude","ai","mlops","delta-lake","pyspark"]}' > /dev/null

echo -e "${GREEN}✅ Topics added${NC}"

# Enable GitHub Pages
echo ""
echo "📚 Enabling GitHub Pages..."

PAGES_RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME/pages" \
  -d '{
    "source": {
      "branch": "main",
      "path": "/docs"
    }
  }')

if echo "$PAGES_RESPONSE" | grep -q "\"html_url\""; then
    PAGES_URL=$(echo "$PAGES_RESPONSE" | grep -o '"html_url": *"[^"]*"' | sed 's/"html_url": *"//' | sed 's/"//')
    echo -e "${GREEN}✅ GitHub Pages enabled${NC}"
    echo "   Docs will be available at: $PAGES_URL"
else
    echo -e "${YELLOW}⚠️  GitHub Pages setup requires manual configuration${NC}"
fi

# Create labels
echo ""
echo "🏷️  Creating issue labels..."

LABELS=(
    "bug:d73a4a:Something isn't working"
    "enhancement:a2eeef:New feature or request"
    "documentation:0075ca:Documentation improvements"
    "good first issue:7057ff:Good for newcomers"
    "help wanted:008672:Extra attention needed"
)

for label_info in "${LABELS[@]}"; do
    IFS=':' read -r name color description <<< "$label_info"
    curl -s -X POST \
      -H "Authorization: token $GITHUB_TOKEN" \
      -H "Accept: application/vnd.github.v3+json" \
      "https://api.github.com/repos/$GITHUB_USER/$REPO_NAME/labels" \
      -d "{\"name\":\"$name\",\"color\":\"$color\",\"description\":\"$description\"}" > /dev/null
done

echo -e "${GREEN}✅ Labels created${NC}"

# Clear token from git config for security
git remote set-url origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
echo -e "${GREEN}✅ Credentials secured${NC}"

# Success summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ GitHub Setup Complete!                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}📍 Repository Details:${NC}"
echo "   URL:      $REPO_URL"
echo "   Clone:    git clone https://github.com/$GITHUB_USER/$REPO_NAME.git"
echo "   API:      https://api.github.com/repos/$GITHUB_USER/$REPO_NAME"
echo ""

if [ -n "$PAGES_URL" ]; then
    echo -e "${CYAN}📚 Documentation:${NC}"
    echo "   Pages:    $PAGES_URL (will be live in a few minutes)"
    echo ""
fi

echo -e "${CYAN}🔧 Next Steps:${NC}"
echo ""
echo "1. Configure GitHub Secrets for CI/CD:"
echo "   Go to: $REPO_URL/settings/secrets/actions"
echo "   Add these secrets:"
echo "     - NPM_TOKEN (for NPM publishing)"
echo "     - DATABRICKS_HOST (for integration tests)"
echo "     - DATABRICKS_TOKEN (for integration tests)"
echo "     - SLACK_WEBHOOK (optional, for notifications)"
echo ""

echo "2. Install the plugin:"
echo "   claude /plugin marketplace add https://github.com/$GITHUB_USER/$REPO_NAME"
echo "   claude /plugin install databricks-engineering"
echo ""

echo "3. Test a command:"
echo "   claude /databricks:plan-pipeline 'test pipeline'"
echo ""

echo "4. View your repository:"
echo "   open $REPO_URL  # or visit in browser"
echo ""

echo -e "${GREEN}🎉 Happy coding!${NC}"
echo ""

# Offer to open in browser
read -p "Open repository in browser? (y/n): " OPEN_BROWSER
if [ "$OPEN_BROWSER" = "y" ]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open "$REPO_URL"
    elif command -v open &> /dev/null; then
        open "$REPO_URL"
    else
        echo "Please visit: $REPO_URL"
    fi
fi
