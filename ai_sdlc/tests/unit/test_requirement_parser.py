"""
Unit tests for RequirementParser.
"""

import tempfile
from pathlib import Path

import pytest

from ai_sdlc.parsers.requirement_parser import (
    AcceptanceCriteria,
    Requirement,
    RequirementParser,
    RequirementPriority,
    RequirementStatus,
    VerificationMethod,
    VerificationSpec,
)


@pytest.fixture
def sample_requirement_content():
    """Sample REQ-*.md content."""
    return """---
req_id: REQ-001
title: "Test Requirement"
owner: "Product Owner"
product: "Test Product"
team: "Platform Team"
priority: "P1"
status: "Draft"
target_release: "v1.0"
created: "2026-01-01"
updated: "2026-01-03"
links:
  jira: "https://jira.example.com/TEST-123"
  ado: ""
  pr: ""
  docs: ""

repos:
  - repo: "test-repo"
    base_branch: "develop"
    release_branch: "main"
    path_scopes:
      - "src/"
      - "tests/"

demo:
  evidence_path: "dbfs:/tmp/demo/REQ-001/"
  required_assets:
    - "AC-1.png"
    - "AC-2.html"
---

# REQ-001: Test Requirement

## 1. Problem statement
This is a test problem statement explaining what we're solving.

## 2. Personas and users
- Persona A: Data Engineers
- Persona B: Data Scientists

## 3. Scope
### In scope
- Feature 1
- Feature 2

### Out of scope / Non-goals
- Feature 3
- Feature 4

## 4. Functional requirements
- FR-1: First functional requirement
- FR-2: Second functional requirement

## 5. Acceptance criteria (AC)

### AC-1
**Given** user has valid data
**When** they run the pipeline
**Then** data is processed successfully

**Verify:**
- test: tests/integration/test_pipeline.py::test_success

**Demo Evidence:**
- AC-1.png
- AC-1.html

### AC-2
**Given** user provides invalid data
**When** they attempt to run the pipeline
**Then** validation error is raised

**Verify:**
- test: tests/unit/test_validation.py::test_error

**Demo Evidence:**
- AC-2.png

## 10. Demo script (mapped to AC IDs)
- Step 1 → AC-1 evidence
- Step 2 → AC-2 evidence
"""


@pytest.fixture
def requirement_file(sample_requirement_content):
    """Create temporary requirement file."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write(sample_requirement_content)
        req_path = f.name

    yield req_path

    # Cleanup
    import os

    if os.path.exists(req_path):
        os.remove(req_path)


class TestVerificationSpec:
    """Tests for VerificationSpec."""

    def test_parse_test(self):
        """Test parsing test verification."""
        spec = VerificationSpec.parse("test: tests/integration/test_x.py::test_y")

        assert spec is not None
        assert spec.method == VerificationMethod.TEST
        assert spec.details == "tests/integration/test_x.py::test_y"

    def test_parse_job(self):
        """Test parsing job verification."""
        spec = VerificationSpec.parse("job: bundle_run: smoke_job")

        assert spec is not None
        assert spec.method == VerificationMethod.JOB
        assert spec.details == "bundle_run: smoke_job"

    def test_parse_query(self):
        """Test parsing query verification."""
        spec = VerificationSpec.parse("query: sql: SELECT * FROM table")

        assert spec is not None
        assert spec.method == VerificationMethod.QUERY
        assert spec.details == "sql: SELECT * FROM table"

    def test_parse_manual(self):
        """Test parsing manual verification."""
        spec = VerificationSpec.parse("manual: screenshot")

        assert spec is not None
        assert spec.method == VerificationMethod.MANUAL
        assert spec.details == "screenshot"

    def test_parse_invalid(self):
        """Test parsing invalid verification."""
        spec = VerificationSpec.parse("invalid: something")
        assert spec is None

        spec = VerificationSpec.parse("")
        assert spec is None


class TestRequirementParser:
    """Tests for RequirementParser."""

    def test_parse_file_success(self, requirement_file):
        """Test parsing a valid requirement file."""
        parser = RequirementParser()
        req = parser.parse_file(requirement_file)

        assert req.req_id == "REQ-001"
        assert req.title == "Test Requirement"
        assert req.owner == "Product Owner"
        assert req.team == "Platform Team"
        assert req.priority == RequirementPriority.P1
        assert req.status == RequirementStatus.DRAFT

    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        parser = RequirementParser()

        with pytest.raises(FileNotFoundError):
            parser.parse_file("/nonexistent/file.md")

    def test_parse_frontmatter(self, sample_requirement_content):
        """Test parsing YAML frontmatter."""
        parser = RequirementParser()
        req = parser.parse_content(sample_requirement_content)

        assert req.req_id == "REQ-001"
        assert req.title == "Test Requirement"
        assert req.priority == RequirementPriority.P1
        assert req.status == RequirementStatus.DRAFT
        assert req.target_release == "v1.0"
        assert req.jira_link == "https://jira.example.com/TEST-123"

    def test_parse_repos(self, sample_requirement_content):
        """Test parsing repos section."""
        parser = RequirementParser()
        req = parser.parse_content(sample_requirement_content)

        assert len(req.repos) == 1
        assert req.repos[0].repo == "test-repo"
        assert req.repos[0].base_branch == "develop"
        assert req.repos[0].path_scopes == ["src/", "tests/"]

    def test_parse_demo(self, sample_requirement_content):
        """Test parsing demo section."""
        parser = RequirementParser()
        req = parser.parse_content(sample_requirement_content)

        assert req.demo is not None
        assert req.demo.evidence_path == "dbfs:/tmp/demo/REQ-001/"
        assert "AC-1.png" in req.demo.required_assets
        assert "AC-2.html" in req.demo.required_assets

    def test_parse_problem_statement(self, sample_requirement_content):
        """Test parsing problem statement."""
        parser = RequirementParser()
        req = parser.parse_content(sample_requirement_content)

        assert "test problem statement" in req.problem_statement.lower()

    def test_parse_personas(self, sample_requirement_content):
        """Test parsing personas."""
        parser = RequirementParser()
        req = parser.parse_content(sample_requirement_content)

        assert len(req.personas) == 2
        assert "Persona A: Data Engineers" in req.personas
        assert "Persona B: Data Scientists" in req.personas

    def test_parse_scope(self, sample_requirement_content):
        """Test parsing scope sections."""
        parser = RequirementParser()
        req = parser.parse_content(sample_requirement_content)

        assert "Feature 1" in req.scope_in
        assert "Feature 2" in req.scope_in
        assert "Feature 3" in req.scope_out
        assert "Feature 4" in req.scope_out

    def test_parse_functional_requirements(self, sample_requirement_content):
        """Test parsing functional requirements."""
        parser = RequirementParser()
        req = parser.parse_content(sample_requirement_content)

        assert len(req.functional_requirements) == 2
        assert "FR-1: First functional requirement" in req.functional_requirements
        assert "FR-2: Second functional requirement" in req.functional_requirements

    def test_parse_acceptance_criteria(self, sample_requirement_content):
        """Test parsing acceptance criteria."""
        parser = RequirementParser()
        req = parser.parse_content(sample_requirement_content)

        assert len(req.acceptance_criteria) == 2

        # Check AC-1
        ac1 = req.acceptance_criteria[0]
        assert ac1.id == "AC-1"
        assert "valid data" in ac1.given.lower()
        assert "run the pipeline" in ac1.when.lower()
        assert "processed successfully" in ac1.then.lower()
        assert ac1.verification is not None
        assert ac1.verification.method == VerificationMethod.TEST
        assert len(ac1.demo_evidence) == 2

        # Check AC-2
        ac2 = req.acceptance_criteria[1]
        assert ac2.id == "AC-2"
        assert "invalid data" in ac2.given.lower()
        assert len(ac2.demo_evidence) == 1

    def test_parse_demo_script(self, sample_requirement_content):
        """Test parsing demo script."""
        parser = RequirementParser()
        req = parser.parse_content(sample_requirement_content)

        assert len(req.demo_script) == 2
        assert any("AC-1" in item for item in req.demo_script)
        assert any("AC-2" in item for item in req.demo_script)

    def test_validate_success(self, sample_requirement_content):
        """Test validation of valid requirement."""
        parser = RequirementParser()
        req = parser.parse_content(sample_requirement_content)

        errors = parser.validate(req)
        assert len(errors) == 0

    def test_validate_missing_req_id(self, sample_requirement_content):
        """Test validation with missing req_id."""
        parser = RequirementParser()
        req = parser.parse_content(sample_requirement_content)
        req.req_id = ""

        errors = parser.validate(req)
        assert any("req_id" in error.lower() for error in errors)

    def test_validate_no_repos(self, sample_requirement_content):
        """Test validation with no repos."""
        parser = RequirementParser()
        req = parser.parse_content(sample_requirement_content)
        req.repos = []

        errors = parser.validate(req)
        assert any("repositories" in error.lower() for error in errors)

    def test_validate_no_acceptance_criteria(self, sample_requirement_content):
        """Test validation with no acceptance criteria."""
        parser = RequirementParser()
        req = parser.parse_content(sample_requirement_content)
        req.acceptance_criteria = []

        errors = parser.validate(req)
        assert any("acceptance criteria" in error.lower() for error in errors)

    def test_validate_missing_verification(self, sample_requirement_content):
        """Test validation with missing verification."""
        parser = RequirementParser()
        req = parser.parse_content(sample_requirement_content)
        req.acceptance_criteria[0].verification = None

        errors = parser.validate(req)
        assert any("verification" in error.lower() for error in errors)

    def test_parse_invalid_frontmatter(self):
        """Test parsing with invalid YAML frontmatter."""
        content = """---
invalid yaml content
that: cannot: be: parsed:
---

# Body content
"""
        parser = RequirementParser()

        with pytest.raises(ValueError, match="Invalid YAML frontmatter"):
            parser.parse_content(content)

    def test_parse_missing_frontmatter(self):
        """Test parsing without frontmatter."""
        content = """
# REQ-001: Test

This is just a body without frontmatter.
"""
        parser = RequirementParser()

        with pytest.raises(ValueError, match="missing YAML frontmatter"):
            parser.parse_content(content)

    def test_parse_missing_required_fields(self):
        """Test parsing with missing required fields."""
        content = """---
req_id: REQ-001
title: "Test"
---

# Body
"""
        parser = RequirementParser()

        with pytest.raises(ValueError, match="Missing required fields"):
            parser.parse_content(content)
