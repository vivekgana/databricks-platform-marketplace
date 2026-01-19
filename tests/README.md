# AI-SDLC Test Suite

This directory contains the test suite for the AI-SDLC workflow orchestration system.

## Test Structure

```
tests/
├── conftest.py                          # Shared fixtures and configuration
├── pytest.ini                           # Pytest configuration
├── unit/                                # Unit tests (fast, isolated)
│   ├── agents/                          # Agent tests
│   │   └── test_base_agent.py
│   ├── evals/                           # Evaluator tests
│   │   └── test_base_eval.py
│   ├── evidence/                        # Evidence management tests
│   │   ├── test_evidence_collector.py
│   │   └── test_evidence_formatter.py
│   ├── orchestration/                   # Orchestration tests
│   └── test_azure_devops_evidence.py    # ADO integration tests
└── integration/                         # Integration tests
    └── test_evidence_workflow.py        # End-to-end workflow tests
```

## Running Tests

### All Tests

```bash
pytest
```

### Unit Tests Only

```bash
pytest -m unit
```

### Integration Tests Only

```bash
pytest -m integration
```

### Specific Test File

```bash
pytest tests/unit/evidence/test_evidence_collector.py
```

### Specific Test Class

```bash
pytest tests/unit/evidence/test_evidence_collector.py::TestEvidenceCollector
```

### Specific Test Method

```bash
pytest tests/unit/evidence/test_evidence_collector.py::TestEvidenceCollector::test_add_evidence
```

### With Coverage Report

```bash
pytest --cov=ai_sdlc --cov=plugins --cov-report=html --cov-report=term
```

View coverage report: `open htmlcov/index.html`

### Verbose Output

```bash
pytest -v
```

### Show Print Statements

```bash
pytest -s
```

### Run Tests in Parallel

```bash
pytest -n auto  # Requires pytest-xdist
```

## Test Markers

Tests are organized using markers:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Integration tests (may require external services)
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.requires_azure` - Tests requiring Azure credentials
- `@pytest.mark.requires_llm` - Tests requiring LLM API access

### Running Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run all except slow tests
pytest -m "not slow"

# Run integration tests that don't require Azure
pytest -m "integration and not requires_azure"
```

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `temp_dir` - Temporary directory for test files
- `work_item_id` - Standard test work item ID
- `mock_config` - Mock configuration
- `mock_ado_plugin` - Mock Azure DevOps plugin
- `sample_agent_result_success` - Sample successful agent result
- `sample_agent_result_failure` - Sample failed agent result
- `sample_work_item_data` - Sample work item data
- `sample_evidence_items` - Sample evidence files
- `mock_storage` - Mock evidence storage
- `sample_stage_results` - Sample workflow stage results

## Writing Tests

### Unit Test Example

```python
import pytest
from my_module import MyClass

@pytest.mark.unit
class TestMyClass:
    @pytest.fixture
    def instance(self):
        return MyClass()

    def test_method(self, instance):
        result = instance.method()
        assert result == expected_value
```

### Integration Test Example

```python
import pytest

@pytest.mark.integration
class TestWorkflow:
    def test_complete_workflow(self):
        # Test end-to-end workflow
        pass
```

### Using Fixtures

```python
def test_with_temp_dir(temp_dir):
    # temp_dir is automatically created and cleaned up
    file_path = Path(temp_dir) / "test.txt"
    file_path.write_text("content")
    assert file_path.exists()
```

## Test Coverage

Current test coverage for key components:

| Component | Coverage | Tests |
|-----------|----------|-------|
| Evidence Collector | ✅ 90%+ | test_evidence_collector.py |
| Evidence Formatter | ✅ 85%+ | test_evidence_formatter.py |
| Base Agent | ✅ 85%+ | test_base_agent.py |
| Base Eval | ✅ 90%+ | test_base_eval.py |
| ADO Evidence Methods | ✅ 80%+ | test_azure_devops_evidence.py |

## Continuous Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Nightly builds

CI configuration:
- Fast unit tests run on every PR
- Integration tests run on main branch commits
- Azure-dependent tests run nightly with credentials

## Troubleshooting

### Tests Fail with Import Errors

Ensure AI-SDLC packages are in PYTHONPATH:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Tests Fail with Missing Dependencies

Install test dependencies:

```bash
pip install pytest pytest-cov pytest-mock pytest-asyncio
```

### Integration Tests Skipped

Integration tests requiring external services are skipped by default. To run them:

1. Set required environment variables:
   ```bash
   export AZURE_STORAGE_CONNECTION_STRING="..."
   export AZURE_DEVOPS_PAT="..."
   ```

2. Run with integration marker:
   ```bash
   pytest -m integration
   ```

### Slow Test Execution

Use pytest-xdist for parallel execution:

```bash
pip install pytest-xdist
pytest -n auto
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Fast**: Unit tests should run in < 1 second
3. **Clear Names**: Test names should describe what they test
4. **Arrange-Act-Assert**: Structure tests clearly
5. **Fixtures**: Use fixtures for common setup
6. **Mocking**: Mock external dependencies
7. **Coverage**: Aim for 80%+ coverage
8. **Documentation**: Add docstrings to test classes

## Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure tests pass: `pytest`
3. Check coverage: `pytest --cov`
4. Add integration tests if needed
5. Update this README if adding new test categories

## Contact

For test-related questions:
- Slack: #ai-sdlc-support
- Email: ai-sdlc-support@yourcompany.com
