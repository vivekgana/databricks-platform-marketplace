# AI-SDLC Agent Development Guide

**Document Version:** 1.0
**Last Updated:** 2026-01-17
**Prepared by:** AI-SDLC Platform Team

---

## Table of Contents

1. [Introduction](#introduction)
2. [Agent Architecture](#agent-architecture)
3. [Creating Custom Agents](#creating-custom-agents)
4. [Agent Lifecycle](#agent-lifecycle)
5. [Evidence Management](#evidence-management)
6. [LLM Integration](#llm-integration)
7. [Error Handling](#error-handling)
8. [Testing Agents](#testing-agents)
9. [Best Practices](#best-practices)
10. [Reference](#reference)

---

## Introduction

### What is an Agent?

In the AI-SDLC system, an **agent** is a specialized component that performs a specific task in the software development workflow. Each agent:

- Extends the `BaseAgent` abstract class
- Executes one workflow stage (planning, code generation, testing, etc.)
- Produces evidence artifacts for audit and review
- Integrates with the evaluation framework
- Reports results to the orchestrator

### When to Create a Custom Agent

Create a custom agent when you need to:
- Add a new workflow stage
- Implement custom code generation logic
- Support a new testing framework
- Integrate with external services
- Extend existing agent functionality

---

## Agent Architecture

### BaseAgent Class

All agents must extend the `BaseAgent` abstract class:

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional
import logging

class BaseAgent(ABC):
    """Base class for all SDLC agents."""

    def __init__(
        self,
        work_item_id: str,
        config: Any,
        evidence_path: str
    ):
        """
        Initialize base agent.

        Args:
            work_item_id: Work item ID
            config: Agent configuration
            evidence_path: Path for storing evidence
        """
        self.work_item_id = work_item_id
        self.config = config
        self.evidence_path = evidence_path
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Create evidence directory
        Path(evidence_path).mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def execute(
        self,
        input_data: Dict[str, Any],
        timeout_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute the agent's main task.

        Args:
            input_data: Input data for the agent
            timeout_seconds: Optional timeout

        Returns:
            Dictionary with:
                - success: bool
                - output_data: Dict with results
                - evidence_files: List of evidence file paths
                - error_message: str (if failed)
        """
        pass

    # Helper methods for evidence management
    def _get_evidence_file_path(self, filename: str) -> str:
        """Get full path for evidence file."""
        return str(Path(self.evidence_path) / filename)

    def _save_evidence_file(self, filename: str, content: str) -> str:
        """Save text content as evidence file."""
        file_path = self._get_evidence_file_path(filename)
        Path(file_path).write_text(content, encoding="utf-8")
        self.logger.info(f"Saved evidence file: {filename}")
        return file_path

    def _save_json_evidence(self, filename: str, data: Dict[str, Any]) -> str:
        """Save JSON data as evidence file."""
        import json
        content = json.dumps(data, indent=2)
        return self._save_evidence_file(filename, content)
```

### Agent Contract

Every agent must:

1. **Accept standard inputs:**
   - `work_item_id` - The work item being processed
   - `config` - Configuration object
   - `evidence_path` - Where to store artifacts

2. **Implement execute() method:**
   - Takes `input_data` dictionary
   - Returns standardized result dictionary
   - Handles timeouts gracefully

3. **Produce evidence:**
   - Save all artifacts to `evidence_path`
   - Return list of evidence file paths
   - Include metadata in output

4. **Handle errors:**
   - Catch and log exceptions
   - Return error message in result
   - Don't crash the orchestrator

---

## Creating Custom Agents

### Step 1: Define Agent Class

```python
from ai_sdlc.agents.base_agent import BaseAgent
from typing import Any, Dict, Optional
import logging

class MyCustomAgent(BaseAgent):
    """
    Custom agent for [specific purpose].

    This agent performs [detailed description of what it does].
    """

    def __init__(
        self,
        work_item_id: str,
        config: Any,
        evidence_path: str
    ):
        super().__init__(work_item_id, config, evidence_path)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Initialize agent-specific state
        self.custom_setting = config.get("custom_setting", "default")

    def execute(
        self,
        input_data: Dict[str, Any],
        timeout_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute custom agent logic.

        Args:
            input_data: Input with keys:
                - work_item_title: str
                - work_item_description: str
                - [other inputs specific to this agent]
            timeout_seconds: Optional timeout

        Returns:
            Result dictionary with:
                - success: bool
                - output_data: Dict with agent outputs
                - evidence_files: List[str] of file paths
                - error_message: Optional[str]
        """
        self.logger.info(f"Starting execution for work item {self.work_item_id}")

        try:
            # Extract inputs
            title = input_data.get("work_item_title", "")
            description = input_data.get("work_item_description", "")

            # Perform agent logic
            result_data = self._do_agent_work(title, description)

            # Save evidence
            evidence_files = []

            # Example: Save a text report
            report_path = self._save_evidence_file(
                "custom-report.txt",
                self._generate_report(result_data)
            )
            evidence_files.append(report_path)

            # Example: Save JSON data
            json_path = self._save_json_evidence(
                "custom-data.json",
                result_data
            )
            evidence_files.append(json_path)

            self.logger.info("Agent execution completed successfully")

            return {
                "success": True,
                "output_data": result_data,
                "evidence_files": evidence_files,
            }

        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "output_data": {},
                "evidence_files": [],
                "error_message": str(e),
            }

    def _do_agent_work(self, title: str, description: str) -> Dict[str, Any]:
        """
        Implement the core logic of your agent.

        This is where you would:
        - Call LLMs for AI-powered operations
        - Generate code or tests
        - Run external tools
        - Process data
        """
        # Your implementation here
        return {
            "processed_title": title.upper(),
            "processed_description": description[:100],
            "custom_metric": 42,
        }

    def _generate_report(self, data: Dict[str, Any]) -> str:
        """Generate a text report from results."""
        return f"""
Custom Agent Report
==================

Work Item: {self.work_item_id}
Custom Metric: {data.get('custom_metric', 0)}

[Your report content here]
"""
```

### Step 2: Register Agent with Orchestrator

```python
from ai_sdlc.orchestration import WorkflowOrchestrator, WorkflowStage

# Create orchestrator
orchestrator = WorkflowOrchestrator(
    ado_plugin=ado_plugin,
    config=config,
    evidence_base_path="azure-blob://evidence",
)

# Register custom agent
orchestrator.register_agent(
    stage=WorkflowStage.CUSTOM_STAGE,  # Define your stage enum
    agent_class=MyCustomAgent,
    agent_config={
        "custom_setting": "value",
    }
)
```

### Step 3: Add Evaluation

Create an evaluator for your agent:

```python
from ai_sdlc.evals.base_eval import BaseEval

class MyCustomEval(BaseEval):
    """Evaluates MyCustomAgent output."""

    def __init__(self, min_score: float = 0.7, config: Any = None):
        super().__init__(min_score, config)

    def evaluate(self, agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate agent output.

        Returns:
            {
                "passed": bool,
                "score": float (0.0-1.0),
                "issues": List[str],
                "recommendations": List[str]
            }
        """
        output_data = agent_result.get("output_data", {})

        score = 0.0
        issues = []
        recommendations = []

        # Evaluation logic
        if output_data.get("custom_metric", 0) >= 40:
            score += 0.5
        else:
            issues.append("Custom metric below threshold")

        # Add more evaluation criteria...

        passed = score >= self.min_score and len(issues) == 0

        return {
            "passed": passed,
            "score": score,
            "issues": issues,
            "recommendations": recommendations,
        }
```

---

## Agent Lifecycle

### Execution Flow

```
1. Orchestrator instantiates agent
   ↓
2. Orchestrator calls agent.execute(input_data)
   ↓
3. Agent performs work
   ├─> Calls LLMs
   ├─> Generates artifacts
   ├─> Saves evidence
   └─> Returns result
   ↓
4. Orchestrator receives result
   ↓
5. Evaluation framework assesses result
   ↓
6. Evidence uploaded to storage
   ↓
7. ADO work item updated
```

### State Transitions

```python
# Agent states during execution
INITIALIZING → EXECUTING → SAVING_EVIDENCE → COMPLETED
                    ↓
                  FAILED
```

---

## Evidence Management

### Evidence Types

Agents should produce evidence in these categories:

```python
from ai_sdlc.evidence import EvidenceCategory

# Available categories:
EvidenceCategory.PLAN          # Implementation plans
EvidenceCategory.CODE          # Generated code
EvidenceCategory.TEST          # Test files
EvidenceCategory.SCREENSHOT    # UI screenshots
EvidenceCategory.REPORT        # Reports and summaries
EvidenceCategory.LOG           # Execution logs
EvidenceCategory.DATA          # Data files
EvidenceCategory.DOCUMENTATION # Documentation
```

### Saving Evidence

```python
def execute(self, input_data: Dict[str, Any], timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
    # ... agent logic ...

    # Method 1: Save text file
    report_path = self._save_evidence_file(
        filename="my-report.txt",
        content="Report content..."
    )

    # Method 2: Save JSON
    data_path = self._save_json_evidence(
        filename="my-data.json",
        data={"key": "value"}
    )

    # Method 3: Save binary file (e.g., image)
    image_path = self._get_evidence_file_path("screenshot.png")
    with open(image_path, "wb") as f:
        f.write(image_bytes)

    # Return evidence files
    return {
        "success": True,
        "output_data": {...},
        "evidence_files": [report_path, data_path, image_path],
    }
```

### Evidence Best Practices

1. **Use descriptive filenames:** `code-quality-report.json` not `output.json`
2. **Include timestamps:** `screenshot-2024-01-15-14-30-00.png`
3. **Document format:** Add `.md` for markdown, `.json` for JSON, etc.
4. **Keep files small:** Large files (>10MB) should be referenced, not embedded
5. **Include metadata:** Add JSON sidecar files for complex artifacts

---

## LLM Integration

### Using LLM Clients

Agents can integrate with LLMs for AI-powered operations:

```python
from anthropic import Anthropic

class AICodeGeneratorAgent(BaseAgent):
    def __init__(self, work_item_id: str, config: Any, evidence_path: str):
        super().__init__(work_item_id, config, evidence_path)

        # Initialize LLM client
        self.llm_client = Anthropic(api_key=config.get("anthropic_api_key"))
        self.model = config.get("llm_model", "databricks-claude-sonnet-4-5")

    def _generate_code_with_llm(self, prompt: str) -> str:
        """Generate code using LLM."""
        try:
            response = self.llm_client.messages.create(
                model=self.model,
                max_tokens=8000,
                temperature=0.2,  # Lower for code generation
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise

    def execute(self, input_data: Dict[str, Any], timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
        # Build prompt
        prompt = self._build_code_generation_prompt(
            input_data.get("requirements", "")
        )

        # Generate code with LLM
        generated_code = self._generate_code_with_llm(prompt)

        # Save as evidence
        code_path = self._save_evidence_file("generated_code.py", generated_code)

        return {
            "success": True,
            "output_data": {"code": generated_code},
            "evidence_files": [code_path],
        }

    def _build_code_generation_prompt(self, requirements: str) -> str:
        """Build a prompt for code generation."""
        return f"""
Generate Python code to implement the following requirements:

{requirements}

Requirements:
- Use type hints
- Include docstrings
- Follow PEP 8 style guidelines
- Add error handling

Return only the code, no explanations.
"""
```

### LLM Best Practices

1. **Use appropriate temperature:**
   - Code generation: 0.2
   - Creative writing: 0.7
   - Analysis: 0.4

2. **Set reasonable token limits:**
   - Short code: 2000 tokens
   - Full modules: 8000 tokens
   - Don't exceed model limits

3. **Handle errors gracefully:**
   - Retry on transient failures
   - Fall back to templates
   - Log all LLM interactions

4. **Cost awareness:**
   - Cache prompts when possible
   - Use smaller models for simple tasks
   - Monitor token usage

---

## Error Handling

### Exception Hierarchy

```python
# Custom exceptions for agents
class AgentException(Exception):
    """Base exception for agents."""
    pass

class AgentTimeoutException(AgentException):
    """Agent execution timed out."""
    pass

class AgentInputException(AgentException):
    """Invalid input data."""
    pass

class AgentResourceException(AgentException):
    """Resource not available (LLM, storage, etc.)."""
    pass
```

### Implementing Error Handling

```python
def execute(self, input_data: Dict[str, Any], timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
    try:
        # Validate inputs
        self._validate_inputs(input_data)

        # Execute with timeout
        if timeout_seconds:
            result = self._execute_with_timeout(input_data, timeout_seconds)
        else:
            result = self._execute_internal(input_data)

        return {
            "success": True,
            "output_data": result,
            "evidence_files": self._get_evidence_files(),
        }

    except AgentTimeoutException as e:
        self.logger.error(f"Agent timed out: {e}")
        return {
            "success": False,
            "output_data": {},
            "evidence_files": [],
            "error_message": f"Execution timed out after {timeout_seconds}s",
        }

    except AgentInputException as e:
        self.logger.error(f"Invalid input: {e}")
        return {
            "success": False,
            "output_data": {},
            "evidence_files": [],
            "error_message": f"Invalid input: {str(e)}",
        }

    except Exception as e:
        self.logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "success": False,
            "output_data": {},
            "evidence_files": [],
            "error_message": f"Unexpected error: {str(e)}",
        }

def _validate_inputs(self, input_data: Dict[str, Any]):
    """Validate required inputs."""
    required_keys = ["work_item_title", "work_item_description"]
    for key in required_keys:
        if key not in input_data:
            raise AgentInputException(f"Missing required input: {key}")
```

---

## Testing Agents

### Unit Testing

```python
import pytest
from unittest.mock import Mock, patch
from my_custom_agent import MyCustomAgent

class TestMyCustomAgent:
    @pytest.fixture
    def agent(self, tmp_path):
        """Create agent instance for testing."""
        config = {"custom_setting": "test_value"}
        return MyCustomAgent(
            work_item_id="TEST-123",
            config=config,
            evidence_path=str(tmp_path)
        )

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.work_item_id == "TEST-123"
        assert agent.custom_setting == "test_value"

    def test_execute_success(self, agent):
        """Test successful execution."""
        input_data = {
            "work_item_title": "Test Title",
            "work_item_description": "Test Description"
        }

        result = agent.execute(input_data)

        assert result["success"] is True
        assert "output_data" in result
        assert len(result["evidence_files"]) > 0

    def test_execute_missing_input(self, agent):
        """Test execution with missing input."""
        input_data = {}  # Missing required keys

        result = agent.execute(input_data)

        assert result["success"] is False
        assert "error_message" in result

    @patch('my_custom_agent.external_service_call')
    def test_execute_with_mock(self, mock_service, agent):
        """Test execution with mocked external service."""
        mock_service.return_value = {"data": "mocked"}

        input_data = {
            "work_item_title": "Test",
            "work_item_description": "Test"
        }

        result = agent.execute(input_data)

        assert result["success"] is True
        mock_service.assert_called_once()

    def test_evidence_files_created(self, agent, tmp_path):
        """Test evidence files are created."""
        input_data = {
            "work_item_title": "Test",
            "work_item_description": "Test"
        }

        result = agent.execute(input_data)

        # Verify evidence files exist
        for file_path in result["evidence_files"]:
            assert Path(file_path).exists()
```

### Integration Testing

```python
def test_agent_with_orchestrator():
    """Test agent integration with orchestrator."""
    from ai_sdlc.orchestration import WorkflowOrchestrator

    orchestrator = WorkflowOrchestrator(
        ado_plugin=mock_ado_plugin,
        config=test_config,
        evidence_base_path="./test_evidence"
    )

    orchestrator.register_agent(
        stage=WorkflowStage.CUSTOM_STAGE,
        agent_class=MyCustomAgent,
        agent_config={}
    )

    result = orchestrator.run_stage(
        work_item_id="TEST-123",
        stage=WorkflowStage.CUSTOM_STAGE
    )

    assert result.success is True
```

---

## Best Practices

### 1. Agent Design

- **Single Responsibility:** Each agent should do one thing well
- **Stateless Execution:** Don't rely on instance state between execute() calls
- **Idempotent:** Running the same inputs multiple times should produce the same results
- **Fail Fast:** Validate inputs early and fail quickly if something is wrong

### 2. Evidence Management

- **Comprehensive:** Capture everything needed for audit and review
- **Organized:** Use clear directory structure and filenames
- **Efficient:** Don't duplicate large files unnecessarily
- **Metadata:** Include context in evidence files

### 3. Error Handling

- **Graceful Degradation:** Return partial results if possible
- **Informative Messages:** Help users understand what went wrong
- **Logging:** Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- **Don't Crash:** Never let uncaught exceptions propagate

### 4. Performance

- **Timeouts:** Respect timeout parameters
- **Streaming:** Stream large outputs instead of loading into memory
- **Caching:** Cache expensive operations when appropriate
- **Parallelism:** Use async/await for I/O-bound operations

### 5. Testing

- **Unit Tests:** Test each method independently
- **Integration Tests:** Test with real orchestrator
- **Mocking:** Mock external services and LLMs
- **Edge Cases:** Test error conditions and edge cases

---

## Reference

### Complete Agent Template

```python
"""
Custom Agent Template

Replace [AGENT_NAME] with your agent name.
Replace [DESCRIPTION] with detailed description.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ai_sdlc.agents.base_agent import BaseAgent


class [AGENT_NAME](BaseAgent):
    """
    [DESCRIPTION]

    This agent performs [detailed explanation].
    """

    def __init__(
        self,
        work_item_id: str,
        config: Any,
        evidence_path: str
    ):
        """
        Initialize [AGENT_NAME].

        Args:
            work_item_id: Work item ID
            config: Agent configuration
            evidence_path: Path for evidence storage
        """
        super().__init__(work_item_id, config, evidence_path)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Initialize agent-specific configuration
        self.setting_a = config.get("setting_a", "default_a")
        self.setting_b = config.get("setting_b", "default_b")

    def execute(
        self,
        input_data: Dict[str, Any],
        timeout_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute [AGENT_NAME] logic.

        Args:
            input_data: Input data containing:
                - [list required inputs]
            timeout_seconds: Optional execution timeout

        Returns:
            Dictionary containing:
                - success: bool - Whether execution succeeded
                - output_data: Dict - Agent outputs
                - evidence_files: List[str] - Paths to evidence files
                - error_message: Optional[str] - Error if failed
        """
        self.logger.info(f"Starting [AGENT_NAME] for work item {self.work_item_id}")

        try:
            # Validate inputs
            self._validate_inputs(input_data)

            # Extract inputs
            input_a = input_data.get("input_a")
            input_b = input_data.get("input_b")

            # Perform agent work
            result = self._perform_work(input_a, input_b)

            # Save evidence
            evidence_files = self._save_evidence(result)

            self.logger.info("[AGENT_NAME] execution completed successfully")

            return {
                "success": True,
                "output_data": result,
                "evidence_files": evidence_files,
            }

        except Exception as e:
            self.logger.error(f"[AGENT_NAME] execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "output_data": {},
                "evidence_files": [],
                "error_message": str(e),
            }

    def _validate_inputs(self, input_data: Dict[str, Any]):
        """Validate required inputs."""
        required = ["input_a", "input_b"]
        for key in required:
            if key not in input_data:
                raise ValueError(f"Missing required input: {key}")

    def _perform_work(self, input_a: Any, input_b: Any) -> Dict[str, Any]:
        """
        Perform the main agent work.

        Args:
            input_a: First input
            input_b: Second input

        Returns:
            Results dictionary
        """
        # Your implementation here
        return {
            "result_a": f"Processed {input_a}",
            "result_b": f"Processed {input_b}",
            "metrics": {
                "metric_1": 42,
                "metric_2": 3.14,
            }
        }

    def _save_evidence(self, result: Dict[str, Any]) -> List[str]:
        """
        Save evidence files.

        Args:
            result: Agent results to save

        Returns:
            List of evidence file paths
        """
        evidence_files = []

        # Save main report
        report_path = self._save_evidence_file(
            "agent-report.txt",
            self._generate_report(result)
        )
        evidence_files.append(report_path)

        # Save metrics as JSON
        metrics_path = self._save_json_evidence(
            "agent-metrics.json",
            result.get("metrics", {})
        )
        evidence_files.append(metrics_path)

        return evidence_files

    def _generate_report(self, result: Dict[str, Any]) -> str:
        """Generate text report from results."""
        return f"""
[AGENT_NAME] Report
{'=' * 50}

Work Item: {self.work_item_id}

Results:
{'-' * 50}
{result}

Generated by [AGENT_NAME]
"""
```

---

## Document History

| Version | Date       | Author                | Changes                     |
|---------|------------|-----------------------|-----------------------------|
| 1.0     | 2026-01-17 | AI-SDLC Platform Team | Initial agent guide         |

---

**Need Help?**
- Report issues: [GitHub Issues](https://github.com/your-org/ai-sdlc/issues)
- Slack: #ai-sdlc-support
- Email: ai-sdlc-support@yourcompany.com
