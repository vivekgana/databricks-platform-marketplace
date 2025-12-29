#!/bin/bash

# Interactive GitHub Connection Helper
# Helps you choose the best method to connect to GitHub

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

clear
echo "${CYAN}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║   GitHub Connection Helper                             ║"
echo "║   Databricks Platform Marketplace                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo "${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check available methods
echo "🔍 Checking available GitHub connection methods..."
echo ""

HAS_GH=false
HAS_GIT=false
HAS_DESKTOP=false

if command_exists gh; then
    echo "✅ GitHub CLI (gh) - AVAILABLE"
    HAS_GH=true
else
    echo "❌ GitHub CLI (gh) - NOT INSTALLED"
fi

if command_exists git; then
    echo "✅ Git - AVAILABLE"
    HAS_GIT=true
else
    echo "❌ Git - NOT INSTALLED"
fi

if [ -d "/Applications/GitHub Desktop.app" ] || command_exists github; then
    echo "✅ GitHub Desktop - AVAILABLE"
    HAS_DESKTOP=true
else
    echo "❌ GitHub Desktop - NOT INSTALLED"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Recommend best method
echo "${CYAN}📋 Recommended Setup Method:${NC}"
echo ""

if [ "$HAS_GH" = true ]; then
    echo "${GREEN}→ Use GitHub CLI (RECOMMENDED)${NC}"
    echo "  Fast, automated, and easy to use"
    echo ""
    echo "  Run: ./github-setup.sh"
    echo ""
    
    read -p "Do you want to run GitHub CLI setup now? (y/n): " RUN_GH
    if [ "$RUN_GH" = "y" ]; then
        ./github-setup.sh
        exit 0
    fi
    
elif [ "$HAS_GIT" = true ]; then
    echo "${YELLOW}→ Use Git Command Line${NC}"
    echo "  Manual but reliable"
    echo ""
    echo "  Follow: GITHUB_SETUP_MANUAL.md"
    echo ""
    
    read -p "Do you want to see the manual setup steps? (y/n): " SHOW_MANUAL
    if [ "$SHOW_MANUAL" = "y" ]; then
        cat GITHUB_SETUP_MANUAL.md | less
    fi
    
elif [ "$HAS_DESKTOP" = true ]; then
    echo "${YELLOW}→ Use GitHub Desktop${NC}"
    echo "  GUI-based, beginner friendly"
    echo ""
    echo "  1. Open GitHub Desktop"
    echo "  2. File → Add Local Repository"
    echo "  3. Select this folder"
    echo "  4. Click 'Publish repository'"
    echo ""
    
else
    echo "${RED}❌ No GitHub tools found${NC}"
    echo ""
    echo "Please install one of the following:"
    echo ""
    echo "1. GitHub CLI (Recommended):"
    echo "   macOS:   brew install gh"
    echo "   Linux:   See https://cli.github.com/"
    echo "   Windows: winget install --id GitHub.cli"
    echo ""
    echo "2. Git:"
    echo "   macOS:   brew install git"
    echo "   Linux:   sudo apt-get install git"
    echo "   Windows: https://git-scm.com/download/win"
    echo ""
    echo "3. GitHub Desktop:"
    echo "   Download: https://desktop.github.com/"
    echo ""
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "${CYAN}📚 Available Guides:${NC}"
echo ""
echo "1. github-setup.sh              - Automated GitHub CLI setup"
echo "2. GITHUB_SETUP_MANUAL.md       - Manual setup instructions"
echo "3. DEPLOYMENT.md                - Complete deployment guide"
echo ""

read -p "Do you want to open the deployment guide? (y/n): " OPEN_GUIDE
if [ "$OPEN_GUIDE" = "y" ]; then
    if command_exists code; then
        code DEPLOYMENT.md
    elif command_exists nano; then
        nano DEPLOYMENT.md
    else
        cat DEPLOYMENT.md | less
    fi
fi

echo ""
echo "${GREEN}✨ Alternative: Use GitHub Web Interface${NC}"
echo ""
echo "If you prefer a web-based setup:"
echo "1. Go to: https://github.com/new"
echo "2. Create repository: databricks-platform-marketplace"
echo "3. Follow instructions in GITHUB_SETUP_MANUAL.md"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "${CYAN}🤝 Need Help?${NC}"
echo ""
echo "- GitHub Docs: https://docs.github.com"
echo "- Git Tutorial: https://git-scm.com/docs/gittutorial"
echo "- GitHub CLI Docs: https://cli.github.com/manual/"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "Press Enter to exit..."
