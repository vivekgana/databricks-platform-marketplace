"""
Requirement Parser for AI-SDLC

Parses REQ-*.md files with YAML frontmatter and Markdown body including
Given/When/Then acceptance criteria.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class RequirementStatus(Enum):
    """Requirement status values."""

    DRAFT = "Draft"
    IN_REVIEW = "In Review"
    APPROVED = "Approved"
    IN_DEV = "In Dev"
    IN_QA = "In QA"
    READY_FOR_DEMO = "Ready for Demo"
    DONE = "Done"


class RequirementPriority(Enum):
    """Requirement priority values."""

    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class VerificationMethod(Enum):
    """Acceptance criteria verification methods."""

    TEST = "test"  # pytest test
    JOB = "job"  # Databricks bundle job
    QUERY = "query"  # SQL query
    MANUAL = "manual"  # Manual verification


@dataclass
class VerificationSpec:
    """Specification for how to verify an acceptance criterion."""

    method: VerificationMethod
    details: str  # test path, job name, SQL, or manual steps

    @classmethod
    def parse(cls, verify_text: str) -> Optional["VerificationSpec"]:
        """
        Parse verification specification from text.

        Examples:
            "test: tests/integration/test_x.py::test_y"
            "job: bundle_run: smoke_job"
            "query: sql: SELECT COUNT(*) FROM table"
            "manual: screenshot"
        """
        if not verify_text:
            return None

        verify_text = verify_text.strip()

        # Match "method: details"
        match = re.match(
            r"^(test|job|query|manual):\s*(.+)$", verify_text, re.IGNORECASE
        )
        if not match:
            return None

        method_str, details = match.groups()
        try:
            method = VerificationMethod(method_str.lower())
            return cls(method=method, details=details.strip())
        except ValueError:
            return None


@dataclass
class AcceptanceCriteria:
    """Acceptance criterion with Given/When/Then format."""

    id: str  # e.g., "AC-1"
    given: str
    when: str
    then: str
    verification: Optional[VerificationSpec] = None
    demo_evidence: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        """Format as Given/When/Then."""
        return f"**Given** {self.given}\n**When** {self.when}\n**Then** {self.then}"


@dataclass
class DemoSpec:
    """Demo evidence specification."""

    evidence_path: str  # DBFS path for evidence
    required_assets: List[str] = field(default_factory=list)


@dataclass
class RepoSpec:
    """Repository specification from requirement."""

    repo: str
    base_branch: str = "develop"
    release_branch: str = "main"
    path_scopes: List[str] = field(default_factory=list)
    change_types: List[str] = field(default_factory=list)


@dataclass
class Requirement:
    """Parsed requirement from REQ-*.md file."""

    # Frontmatter metadata
    req_id: str
    title: str
    owner: str
    product: str
    team: str
    priority: RequirementPriority
    status: RequirementStatus
    target_release: str
    created: str
    updated: str

    # Links
    jira_link: Optional[str] = None
    ado_link: Optional[str] = None
    pr_link: Optional[str] = None
    docs_link: Optional[str] = None

    # Repo configuration
    repos: List[RepoSpec] = field(default_factory=list)

    # Demo spec
    demo: Optional[DemoSpec] = None

    # Markdown body sections
    problem_statement: str = ""
    personas: List[str] = field(default_factory=list)
    scope_in: List[str] = field(default_factory=list)
    scope_out: List[str] = field(default_factory=list)
    functional_requirements: List[str] = field(default_factory=list)
    acceptance_criteria: List[AcceptanceCriteria] = field(default_factory=list)
    databricks_objects: Dict[str, Any] = field(default_factory=dict)
    observability: Dict[str, Any] = field(default_factory=dict)
    risks: List[str] = field(default_factory=list)
    rollout_plan: str = ""
    demo_script: List[str] = field(default_factory=list)

    # Raw content
    raw_body: str = ""


class RequirementParser:
    """Parser for REQ-*.md requirement files."""

    # Regex patterns for parsing
    AC_HEADER_PATTERN = re.compile(r"^###\s+(AC-\d+)", re.MULTILINE)
    GIVEN_PATTERN = re.compile(r"\*\*Given\*\*\s+(.+?)(?=\*\*When\*\*)", re.DOTALL)
    WHEN_PATTERN = re.compile(r"\*\*When\*\*\s+(.+?)(?=\*\*Then\*\*)", re.DOTALL)
    THEN_PATTERN = re.compile(r"\*\*Then\*\*\s+(.+?)(?=\*\*Verify|\n\n|$)", re.DOTALL)
    VERIFY_PATTERN = re.compile(r"\*\*Verify:\*\*\s*\n-\s*(.+)", re.MULTILINE)
    EVIDENCE_PATTERN = re.compile(
        r"\*\*Demo Evidence:\*\*\s*\n((?:-\s*.+\n?)+)", re.MULTILINE
    )

    def __init__(self):
        """Initialize RequirementParser."""
        pass

    def parse_file(self, file_path: str) -> Requirement:
        """
        Parse a REQ-*.md file.

        Args:
            file_path: Path to REQ-*.md file

        Returns:
            Parsed Requirement object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Requirement file not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        return self.parse_content(content)

    def parse_content(self, content: str) -> Requirement:
        """
        Parse requirement content.

        Args:
            content: Full REQ-*.md file content

        Returns:
            Parsed Requirement object

        Raises:
            ValueError: If content format is invalid
        """
        # Split frontmatter and body
        frontmatter, body = self._split_frontmatter(content)

        # Parse frontmatter YAML
        metadata = self._parse_frontmatter(frontmatter)

        # Parse body sections
        sections = self._parse_body(body)

        # Build Requirement object
        requirement = Requirement(
            req_id=metadata["req_id"],
            title=metadata["title"],
            owner=metadata["owner"],
            product=metadata["product"],
            team=metadata["team"],
            priority=RequirementPriority(metadata["priority"]),
            status=RequirementStatus(metadata["status"]),
            target_release=metadata["target_release"],
            created=metadata["created"],
            updated=metadata["updated"],
            jira_link=metadata.get("links", {}).get("jira"),
            ado_link=metadata.get("links", {}).get("ado"),
            pr_link=metadata.get("links", {}).get("pr"),
            docs_link=metadata.get("links", {}).get("docs"),
            repos=self._parse_repos(metadata.get("repos", [])),
            demo=self._parse_demo(metadata.get("demo", {})),
            problem_statement=sections.get("problem_statement", ""),
            personas=sections.get("personas", []),
            scope_in=sections.get("scope_in", []),
            scope_out=sections.get("scope_out", []),
            functional_requirements=sections.get("functional_requirements", []),
            acceptance_criteria=sections.get("acceptance_criteria", []),
            databricks_objects=sections.get("databricks_objects", {}),
            observability=sections.get("observability", {}),
            risks=sections.get("risks", []),
            rollout_plan=sections.get("rollout_plan", ""),
            demo_script=sections.get("demo_script", []),
            raw_body=body,
        )

        return requirement

    def _split_frontmatter(self, content: str) -> tuple[str, str]:
        """Split YAML frontmatter from Markdown body."""
        # Match ---\n...\n---
        match = re.match(r"^---\n(.*?)\n---\n(.+)$", content, re.DOTALL)
        if not match:
            raise ValueError("Invalid format: missing YAML frontmatter (---...---)")

        frontmatter = match.group(1)
        body = match.group(2)

        return frontmatter, body

    def _parse_frontmatter(self, frontmatter: str) -> Dict[str, Any]:
        """Parse YAML frontmatter."""
        try:
            metadata = yaml.safe_load(frontmatter)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML frontmatter: {e}")

        # Validate required fields
        required = [
            "req_id",
            "title",
            "owner",
            "product",
            "team",
            "priority",
            "status",
            "target_release",
            "created",
            "updated",
        ]
        missing = [field for field in required if field not in metadata]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        return metadata

    def _parse_repos(self, repos_data: List[Dict[str, Any]]) -> List[RepoSpec]:
        """Parse repos section from frontmatter."""
        repos = []
        for repo_data in repos_data:
            repos.append(
                RepoSpec(
                    repo=repo_data.get("repo", ""),
                    base_branch=repo_data.get("base_branch", "develop"),
                    release_branch=repo_data.get("release_branch", "main"),
                    path_scopes=repo_data.get("path_scopes", []),
                    change_types=repo_data.get("change_types", []),
                )
            )
        return repos

    def _parse_demo(self, demo_data: Dict[str, Any]) -> Optional[DemoSpec]:
        """Parse demo section from frontmatter."""
        if not demo_data:
            return None

        return DemoSpec(
            evidence_path=demo_data.get("evidence_path", ""),
            required_assets=demo_data.get("required_assets", []),
        )

    def _parse_body(self, body: str) -> Dict[str, Any]:
        """Parse Markdown body into sections."""
        sections = {}

        # Extract problem statement (## 1. Problem statement)
        sections["problem_statement"] = self._extract_section(
            body, r"##\s+1\.\s+Problem statement"
        )

        # Extract personas (## 2. Personas and users)
        personas_text = self._extract_section(body, r"##\s+2\.\s+Personas and users")
        sections["personas"] = self._extract_list_items(personas_text)

        # Extract scope in (### In scope)
        scope_in_text = self._extract_section(body, r"###\s+In scope")
        sections["scope_in"] = self._extract_list_items(scope_in_text)

        # Extract scope out (### Out of scope)
        scope_out_text = self._extract_section(body, r"###\s+Out of scope")
        sections["scope_out"] = self._extract_list_items(scope_out_text)

        # Extract functional requirements (## 4. Functional requirements)
        fr_text = self._extract_section(body, r"##\s+4\.\s+Functional requirements")
        sections["functional_requirements"] = self._extract_list_items(fr_text)

        # Extract acceptance criteria (## 5. Acceptance criteria)
        ac_section = self._extract_section(body, r"##\s+5\.\s+Acceptance criteria")
        sections["acceptance_criteria"] = self._parse_acceptance_criteria(ac_section)

        # Extract demo script (## 10. Demo script)
        demo_text = self._extract_section(body, r"##\s+10\.\s+Demo script")
        sections["demo_script"] = self._extract_list_items(demo_text)

        return sections

    def _extract_section(self, content: str, header_pattern: str) -> str:
        """Extract content between section header and next ## header."""
        pattern = f"{header_pattern}(.+?)(?=##|$)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_list_items(self, text: str) -> List[str]:
        """Extract bulleted list items from text."""
        if not text:
            return []

        items = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                item = line.lstrip("-*").strip()
                if item:
                    items.append(item)
        return items

    def _parse_acceptance_criteria(self, ac_section: str) -> List[AcceptanceCriteria]:
        """Parse acceptance criteria with Given/When/Then format."""
        if not ac_section:
            return []

        acs = []

        # Find all AC headers (### AC-1, ### AC-2, etc.)
        ac_headers = list(self.AC_HEADER_PATTERN.finditer(ac_section))

        for i, header_match in enumerate(ac_headers):
            ac_id = header_match.group(1)

            # Extract AC content (from this header to next header or end)
            start = header_match.end()
            if i + 1 < len(ac_headers):
                end = ac_headers[i + 1].start()
            else:
                end = len(ac_section)

            ac_content = ac_section[start:end]

            # Parse Given/When/Then
            given_match = self.GIVEN_PATTERN.search(ac_content)
            when_match = self.WHEN_PATTERN.search(ac_content)
            then_match = self.THEN_PATTERN.search(ac_content)

            if not all([given_match, when_match, then_match]):
                continue  # Skip malformed AC

            given = given_match.group(1).strip()
            when = when_match.group(1).strip()
            then = then_match.group(1).strip()

            # Parse verification
            verify_match = self.VERIFY_PATTERN.search(ac_content)
            verification = None
            if verify_match:
                verify_text = verify_match.group(1).strip()
                verification = VerificationSpec.parse(verify_text)

            # Parse demo evidence
            evidence_match = self.EVIDENCE_PATTERN.search(ac_content)
            demo_evidence = []
            if evidence_match:
                evidence_lines = evidence_match.group(1).strip()
                demo_evidence = self._extract_list_items(evidence_lines)

            acs.append(
                AcceptanceCriteria(
                    id=ac_id,
                    given=given,
                    when=when,
                    then=then,
                    verification=verification,
                    demo_evidence=demo_evidence,
                )
            )

        return acs

    def validate(self, requirement: Requirement) -> List[str]:
        """
        Validate requirement completeness.

        Args:
            requirement: Requirement to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check required metadata
        if not requirement.req_id:
            errors.append("Missing req_id")
        if not requirement.title:
            errors.append("Missing title")
        if not requirement.owner:
            errors.append("Missing owner")

        # Check repos
        if not requirement.repos:
            errors.append("No repositories specified")

        # Check acceptance criteria
        if not requirement.acceptance_criteria:
            errors.append("No acceptance criteria defined")

        # Check each AC has verification
        for ac in requirement.acceptance_criteria:
            if not ac.verification:
                errors.append(f"{ac.id}: Missing verification method")
            if not ac.demo_evidence:
                errors.append(f"{ac.id}: No demo evidence specified")

        return errors
