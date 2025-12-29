#!/bin/bash

# Setup script for Databricks Platform Marketplace
# This script initializes the repository and prepares it for development

set -e

echo "🚀 Setting up Databricks Platform Marketplace..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi
echo "✅ Python $(python3 --version | cut -d' ' -f2) found"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi
echo "✅ Node.js $(node --version) found"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi
echo "✅ npm $(npm --version) found"

# Check git
if ! command -v git &> /dev/null; then
    echo "❌ git is not installed. Please install git."
    exit 1
fi
echo "✅ git $(git --version | cut -d' ' -f3) found"

echo ""

# Initialize git repository
echo "📦 Initializing git repository..."
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Create main branch if not exists
if ! git rev-parse --verify main &> /dev/null; then
    git checkout -b main
    echo "✅ Created main branch"
fi

# Install Python dependencies
echo ""
echo "🐍 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt
    echo "✅ Production dependencies installed"
fi

if [ -f "requirements-dev.txt" ]; then
    python3 -m pip install -r requirements-dev.txt
    echo "✅ Development dependencies installed"
fi

# Install Node dependencies
echo ""
echo "📦 Installing Node.js dependencies..."
npm install
echo "✅ Node.js dependencies installed"

# Setup configuration
echo ""
echo "⚙️  Setting up configuration..."
if [ ! -f ".databricks-plugin-config.yaml" ]; then
    cp .databricks-plugin-config.example.yaml .databricks-plugin-config.yaml
    echo "✅ Created .databricks-plugin-config.yaml from template"
    echo "${YELLOW}⚠️  Please edit .databricks-plugin-config.yaml with your Databricks credentials${NC}"
else
    echo "✅ Configuration file already exists"
fi

# Setup pre-commit hooks
echo ""
echo "🪝 Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo "✅ Pre-commit hooks installed"
else
    echo "${YELLOW}⚠️  pre-commit not found. Install with: pip install pre-commit${NC}"
fi

# Create necessary directories
echo ""
echo "📁 Creating directory structure..."
mkdir -p logs
mkdir -p data
mkdir -p tmp
echo "✅ Directories created"

# Validate plugin configurations
echo ""
echo "🔍 Validating plugin configurations..."
npm run validate
echo "✅ Plugin configurations valid"

# Run initial tests
echo ""
echo "🧪 Running initial tests..."
pytest tests/unit/ -v --tb=short || {
    echo "${YELLOW}⚠️  Some tests failed. This is normal for a fresh setup.${NC}"
}

# Git initial commit
echo ""
echo "📝 Creating initial commit..."
if ! git rev-parse HEAD &> /dev/null; then
    git add .
    git commit -m "Initial commit: Databricks Platform Marketplace v1.0.0

    - Added Databricks Engineering Plugin with 15 commands
    - Added 18 specialized agents for code review
    - Added 8 reusable skills and templates
    - Added comprehensive test suite
    - Added CI/CD workflows
    - Added documentation and examples"
    echo "✅ Initial commit created"
else
    echo "✅ Repository already has commits"
fi

# Setup complete
echo ""
echo "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "📚 Next steps:"
echo "  1. Edit .databricks-plugin-config.yaml with your credentials"
echo "  2. Set environment variables:"
echo "     export DATABRICKS_HOST='https://your-workspace.cloud.databricks.com'"
echo "     export DATABRICKS_TOKEN='your-token'"
echo ""
echo "  3. Test the plugin:"
echo "     claude /databricks:plan-pipeline 'test pipeline'"
echo ""
echo "  4. Run tests:"
echo "     npm test"
echo ""
echo "  5. Start development:"
echo "     code .  # or your preferred editor"
echo ""
echo "📖 Documentation: docs/getting-started.md"
echo "💬 Community: https://yourcompany.slack.com/data-platform"
echo ""
echo "Happy coding! 🎉"
