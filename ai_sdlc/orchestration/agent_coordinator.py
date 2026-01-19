"""
Agent Coordinator for AI-SDLC Workflow

Manages agent lifecycle, execution, and result aggregation.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .state_machine import WorkflowStage, StageConfig

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Status of an agent execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class AgentResult:
    """
    Result from an agent execution.
    """

    agent_name: str
    stage: WorkflowStage
    status: AgentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    output_data: Dict[str, Any] = field(default_factory=dict)
    evidence_paths: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    logs: List[str] = field(default_factory=list)

    def is_success(self) -> bool:
        """Check if agent execution was successful."""
        return self.status == AgentStatus.COMPLETED

    def add_log(self, message: str):
        """Add a log message."""
        self.logs.append(f"[{datetime.now().isoformat()}] {message}")


class AgentCoordinator:
    """
    Coordinates agent execution for workflow stages.

    Manages agent lifecycle, monitors execution, and aggregates results.
    """

    def __init__(
        self,
        work_item_id: str,
        config: Any,  # PluginConfig
        evidence_base_path: str,
    ):
        """
        Initialize the agent coordinator.

        Args:
            work_item_id: The work item ID being processed
            config: Plugin configuration
            evidence_base_path: Base path for evidence storage
        """
        self.work_item_id = work_item_id
        self.config = config
        self.evidence_base_path = evidence_base_path
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Track agent results
        self.agent_results: Dict[WorkflowStage, AgentResult] = {}

        # Agent registry (will be populated dynamically)
        self.agent_registry: Dict[str, Any] = {}

    def register_agent(self, agent_class_name: str, agent_class: Any):
        """
        Register an agent class.

        Args:
            agent_class_name: Name of the agent class
            agent_class: The agent class itself
        """
        self.agent_registry[agent_class_name] = agent_class
        self.logger.info(f"Registered agent: {agent_class_name}")

    def execute_stage(
        self,
        stage_config: StageConfig,
        input_data: Dict[str, Any],
        timeout_seconds: Optional[int] = None,
    ) -> AgentResult:
        """
        Execute an agent for a workflow stage.

        Args:
            stage_config: Configuration for the stage
            input_data: Input data for the agent
            timeout_seconds: Optional timeout in seconds (overrides config)

        Returns:
            AgentResult with execution results
        """
        agent_name = stage_config.agent_class_name
        stage = stage_config.stage

        self.logger.info(f"Executing stage {stage.value} with agent {agent_name}")

        # Create agent result
        result = AgentResult(
            agent_name=agent_name,
            stage=stage,
            status=AgentStatus.PENDING,
            start_time=datetime.now(),
        )

        try:
            # Check if agent is registered
            if agent_name not in self.agent_registry:
                # Try to dynamically import agent (for future extension)
                self.logger.warning(
                    f"Agent {agent_name} not registered. Attempting dynamic import."
                )
                # For now, return a placeholder result
                result.status = AgentStatus.FAILED
                result.error_message = f"Agent {agent_name} not implemented yet"
                result.end_time = datetime.now()
                result.duration_seconds = (
                    result.end_time - result.start_time
                ).total_seconds()
                self.agent_results[stage] = result
                return result

            # Get agent class
            agent_class = self.agent_registry[agent_name]

            # Update status to running
            result.status = AgentStatus.RUNNING
            result.add_log(f"Starting agent {agent_name} for stage {stage.value}")

            # Create agent instance
            agent_instance = agent_class(
                work_item_id=self.work_item_id,
                config=self.config,
                evidence_path=f"{self.evidence_base_path}/{stage.value}",
            )

            # Execute agent
            timeout = timeout_seconds or (stage_config.timeout_minutes * 60)
            self.logger.info(f"Executing agent with timeout: {timeout} seconds")

            # Execute (this would be the actual agent execution)
            # For now, we'll define the interface
            output = agent_instance.execute(input_data, timeout_seconds=timeout)

            # Update result
            result.status = AgentStatus.COMPLETED
            result.output_data = output.get("data", {})
            result.evidence_paths = output.get("evidence_paths", [])
            result.add_log(f"Agent {agent_name} completed successfully")

        except TimeoutError as e:
            result.status = AgentStatus.TIMEOUT
            result.error_message = f"Agent execution timed out: {e}"
            result.add_log(f"Agent {agent_name} timed out")
            self.logger.error(result.error_message)

        except Exception as e:
            result.status = AgentStatus.FAILED
            result.error_message = f"Agent execution failed: {e}"
            result.add_log(f"Agent {agent_name} failed: {e}")
            self.logger.error(result.error_message)

        finally:
            # Record end time
            result.end_time = datetime.now()
            result.duration_seconds = (
                result.end_time - result.start_time
            ).total_seconds()

            # Store result
            self.agent_results[stage] = result

        return result

    def get_stage_result(self, stage: WorkflowStage) -> Optional[AgentResult]:
        """
        Get the result for a specific stage.

        Args:
            stage: The workflow stage

        Returns:
            AgentResult if stage was executed, None otherwise
        """
        return self.agent_results.get(stage)

    def get_all_results(self) -> Dict[WorkflowStage, AgentResult]:
        """Get all agent results."""
        return self.agent_results

    def get_successful_stages(self) -> List[WorkflowStage]:
        """Get list of stages that completed successfully."""
        return [
            stage for stage, result in self.agent_results.items() if result.is_success()
        ]

    def get_failed_stages(self) -> List[tuple[WorkflowStage, AgentResult]]:
        """
        Get list of stages that failed.

        Returns:
            List of tuples (stage, result)
        """
        return [
            (stage, result)
            for stage, result in self.agent_results.items()
            if not result.is_success()
        ]

    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all agent executions.

        Returns:
            Dictionary with execution summary
        """
        total_stages = len(self.agent_results)
        successful_stages = len(self.get_successful_stages())
        failed_stages = len(self.get_failed_stages())

        total_duration = sum(
            result.duration_seconds for result in self.agent_results.values()
        )

        return {
            "work_item_id": self.work_item_id,
            "total_stages_executed": total_stages,
            "successful_stages": successful_stages,
            "failed_stages": failed_stages,
            "total_duration_seconds": total_duration,
            "average_duration_seconds": (
                total_duration / total_stages if total_stages > 0 else 0
            ),
            "evidence_base_path": self.evidence_base_path,
        }

    def get_all_evidence_paths(self) -> List[str]:
        """
        Get all evidence paths from all stages.

        Returns:
            List of evidence paths
        """
        all_paths = []
        for result in self.agent_results.values():
            all_paths.extend(result.evidence_paths)
        return all_paths

    def reset(self):
        """Reset the coordinator (clear all results)."""
        self.agent_results.clear()
        self.logger.info("Agent coordinator reset")
