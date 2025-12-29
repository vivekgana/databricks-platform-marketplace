# Contributing to Databricks Platform Marketplace

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and professional in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/databricks-platform-marketplace.git
   cd databricks-platform-marketplace
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/yourcompany/databricks-platform-marketplace.git
   ```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Git
- Databricks workspace (for integration tests)

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install Node dependencies
npm install

# Install pre-commit hooks
pre-commit install
```

### Configuration

1. Copy the example configuration:
   ```bash
   cp .databricks-plugin-config.example.yaml .databricks-plugin-config.yaml
   ```

2. Set environment variables:
   ```bash
   export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
   export DATABRICKS_TOKEN="your-token"
   ```

## How to Contribute

### Reporting Bugs

- Check if the bug has already been reported in [Issues](https://github.com/yourcompany/databricks-platform-marketplace/issues)
- Use the bug report template
- Include:
  - Clear description
  - Steps to reproduce
  - Expected vs actual behavior
  - Environment details
  - Logs/screenshots if applicable

### Suggesting Features

- Check if the feature has already been suggested
- Use the feature request template
- Explain:
  - The problem it solves
  - Proposed solution
  - Alternative approaches
  - Example use cases

### Contributing Code

1. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Write tests** for new functionality

4. **Update documentation** as needed

5. **Commit your changes** with clear messages:
   ```bash
   git commit -m "feat: add customer segmentation to pipeline"
   ```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(commands): add deploy-bundle command for multi-env deployment
fix(agents): correct PySpark optimizer shuffle detection
docs(readme): update installation instructions
test(integration): add Delta Sharing test cases
```

## Pull Request Process

1. **Update your branch** with latest upstream:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests locally**:
   ```bash
   npm test
   pytest tests/ -v
   ```

3. **Run linting**:
   ```bash
   npm run lint
   black plugins/ tests/ examples/
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request** on GitHub:
   - Use the PR template
   - Link related issues
   - Provide clear description
   - Add screenshots/examples if applicable

6. **Address review feedback**:
   - Make requested changes
   - Push updates to your branch
   - Respond to comments

### PR Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts
- [ ] Branch is up-to-date with main

## Coding Standards

### Python

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Maximum line length: 100 characters
- Use type hints where appropriate
- Write docstrings for all public functions/classes

**Example:**
```python
def process_customer_data(
    customer_df: DataFrame,
    start_date: str,
    end_date: str
) -> DataFrame:
    """
    Process customer data for specified date range.
    
    Args:
        customer_df: Input customer DataFrame
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        Processed customer DataFrame with aggregations
    
    Raises:
        ValueError: If date range is invalid
    """
    # Implementation
    pass
```

### Markdown

- Use clear headings hierarchy
- Include code examples where relevant
- Keep line length reasonable
- Use tables for structured data

### JSON

- Validate with `jq`
- Use 2-space indentation
- Follow marketplace schema

## Testing Guidelines

### Unit Tests

- Located in `tests/unit/`
- Test individual functions/classes
- Mock external dependencies
- Aim for >80% code coverage

```python
def test_plan_pipeline_basic(sample_pipeline_spec):
    """Test basic pipeline planning."""
    result = plan_pipeline.create_plan(sample_pipeline_spec)
    
    assert result is not None
    assert "bronze" in result["layers"]
```

### Integration Tests

- Located in `tests/integration/`
- Test against real Databricks workspace
- Use test catalog/schema
- Clean up resources after test

```python
@pytest.mark.integration
def test_full_pipeline_workflow(workspace_client, test_catalog):
    """Test complete pipeline lifecycle."""
    # Test implementation
    pass
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=plugins --cov-report=html

# Specific test file
pytest tests/unit/test_commands.py -v
```

## Documentation

### Plugin Documentation

When adding commands/agents/skills:

1. Update plugin.json
2. Create corresponding .md file
3. Update README.md
4. Add examples in docs/

### Code Comments

- Explain **why**, not **what**
- Keep comments up-to-date
- Use docstrings for public APIs

### Documentation Structure

```
docs/
├── getting-started.md
├── configuration.md
├── commands-reference.md
├── agents-reference.md
├── skills-reference.md
└── examples/
```

## Need Help?

- 💬 [Slack Community](https://yourcompany.slack.com/data-platform)
- 📧 [Email](mailto:data-platform@yourcompany.com)
- 🐛 [GitHub Issues](https://github.com/yourcompany/databricks-platform-marketplace/issues)

## Recognition

Contributors are recognized in:
- CHANGELOG.md for each release
- GitHub contributors page
- Annual contributor spotlight

Thank you for contributing! 🎉
