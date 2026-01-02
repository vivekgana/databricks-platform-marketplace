#!/bin/bash
# Test Runner Script

set -e

echo "Running unit tests..."
pytest tests/unit/ -v --cov=src --cov-report=html

echo "Running integration tests..."
pytest tests/integration/ -v

echo "Generating coverage report..."
coverage report
coverage html

echo "All tests passed!"
