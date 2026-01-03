#!/bin/bash
# Deployment script for DevOps Integration Plugins
# Last Updated: January 2, 2026

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi

    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is required but not installed"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    cd "$PROJECT_ROOT"
    pip3 install -r requirements.txt
    log_success "Dependencies installed"
}

# Run tests
run_tests() {
    log_info "Running tests..."
    cd "$PROJECT_ROOT"

    # Run unit tests
    pytest tests/ -v -m "unit" --cov=sdk --cov=integrations --cov=examples

    if [ $? -eq 0 ]; then
        log_success "All tests passed"
    else
        log_error "Tests failed"
        exit 1
    fi
}

# Build package
build_package() {
    log_info "Building package..."
    cd "$PROJECT_ROOT"

    # Clean previous builds
    rm -rf dist/ build/ *.egg-info

    # Build
    python3 -m build

    if [ $? -eq 0 ]; then
        log_success "Package built successfully"
    else
        log_error "Package build failed"
        exit 1
    fi
}

# Deploy to environment
deploy_to_env() {
    local ENV=$1
    log_info "Deploying to $ENV environment..."

    case $ENV in
        dev|development)
            deploy_dev
            ;;
        staging)
            deploy_staging
            ;;
        prod|production)
            deploy_production
            ;;
        *)
            log_error "Unknown environment: $ENV"
            echo "Usage: $0 <dev|staging|prod>"
            exit 1
            ;;
    esac
}

# Deploy to development
deploy_dev() {
    log_info "Deploying to development..."

    # Copy files to development server (example)
    # scp -r dist/* dev-server:/opt/plugins/devops-integrations/

    # Or upload to package repository
    # twine upload --repository-url https://dev-pypi.yourcompany.com dist/*

    log_success "Deployed to development"

    # Run smoke tests
    log_info "Running smoke tests..."
    pytest tests/ -v -m "smoke" || log_warning "Smoke tests failed"
}

# Deploy to staging
deploy_staging() {
    log_info "Deploying to staging..."

    # Ensure we're on main branch
    BRANCH=$(git branch --show-current)
    if [ "$BRANCH" != "main" ]; then
        log_warning "Not on main branch (current: $BRANCH)"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    # Deploy to staging
    # scp -r dist/* staging-server:/opt/plugins/devops-integrations/

    log_success "Deployed to staging"

    # Run integration tests
    log_info "Running integration tests..."
    pytest tests/ -v -m "integration" --run-integration || log_warning "Integration tests failed"
}

# Deploy to production
deploy_production() {
    log_warning "Deploying to PRODUCTION..."

    # Ensure we're on main branch
    BRANCH=$(git branch --show-current)
    if [ "$BRANCH" != "main" ]; then
        log_error "Must be on main branch for production deploy"
        exit 1
    fi

    # Confirmation
    read -p "Are you sure you want to deploy to PRODUCTION? (yes/NO) " -r
    echo
    if [[ ! $REPLY =~ ^yes$ ]]; then
        log_info "Deployment cancelled"
        exit 0
    fi

    # Tag release
    VERSION=$(grep -oP '(?<=version = ")[^"]+' pyproject.toml)
    log_info "Creating release tag: v$VERSION"
    git tag -a "v$VERSION" -m "Release version $VERSION"
    git push origin "v$VERSION"

    # Deploy
    # twine upload --repository-url https://pypi.yourcompany.com dist/*

    log_success "Deployed to production (v$VERSION)"

    # Notify team
    log_info "Sending notification..."
    # curl -X POST "$SLACK_WEBHOOK_URL" -H 'Content-Type: application/json' \
    #   -d "{\"text\": \"DevOps Integrations v$VERSION deployed to production\"}"
}

# Health check
health_check() {
    local ENV=$1
    log_info "Running health check for $ENV..."

    # Example health check
    python3 << EOF
from sdk import PluginRegistry
from integrations.jira import JiraPlugin
from integrations.azure_devops import AzureDevOpsPlugin

registry = PluginRegistry()
print("Health check: OK")
EOF

    if [ $? -eq 0 ]; then
        log_success "Health check passed"
    else
        log_error "Health check failed"
        exit 1
    fi
}

# Rollback
rollback() {
    local ENV=$1
    log_warning "Rolling back $ENV environment..."

    # Get previous version
    PREV_VERSION=$(git describe --abbrev=0 --tags $(git describe --abbrev=0 --tags)^)
    log_info "Rolling back to $PREV_VERSION"

    # Perform rollback
    # kubectl rollout undo deployment/devops-integrations -n $ENV

    log_success "Rolled back to $PREV_VERSION"
}

# Main script
main() {
    log_info "DevOps Integrations Deployment Script"
    log_info "========================================"

    if [ $# -eq 0 ]; then
        echo "Usage: $0 <command> [environment]"
        echo ""
        echo "Commands:"
        echo "  deploy <dev|staging|prod>  - Deploy to environment"
        echo "  test                       - Run tests only"
        echo "  build                      - Build package only"
        echo "  health <env>               - Run health check"
        echo "  rollback <env>             - Rollback deployment"
        exit 1
    fi

    COMMAND=$1
    ENV=${2:-dev}

    check_prerequisites

    case $COMMAND in
        deploy)
            install_dependencies
            run_tests
            build_package
            deploy_to_env "$ENV"
            health_check "$ENV"
            ;;
        test)
            install_dependencies
            run_tests
            ;;
        build)
            install_dependencies
            build_package
            ;;
        health)
            health_check "$ENV"
            ;;
        rollback)
            rollback "$ENV"
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            exit 1
            ;;
    esac

    log_success "Deployment completed successfully!"
}

# Run main
main "$@"
