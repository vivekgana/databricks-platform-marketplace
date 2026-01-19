"""
State Machine for AI-SDLC Workflow

Defines workflow stages, ADO states, and state transitions for the automated
development lifecycle.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Type, Any

# Import will be needed when agents/evals are created
# from ai_sdlc.agents.base_agent import BaseAgent
# from ai_sdlc.evals.eval_framework import BaseEval


class ADOState(Enum):
    """
    Azure DevOps work item states for Audit Cortex 2 custom process.

    These match the custom states configured in the Azure DevOps project.
    """

    NEW = "New"
    PLANNING = "Planning"
    IN_DEVELOPMENT = "In Development"
    TESTING = "Testing"
    DONE = "Done"


class WorkflowStage(Enum):
    """
    Internal workflow stages that map to ADO states.

    Each stage represents a distinct phase in the automated development lifecycle.
    Multiple stages may map to the same ADO state.
    """

    PLANNING = "planning"
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    UNIT_TESTING = "unit_testing"
    QA_TESTING = "qa_testing"
    INTEGRATION_TESTING = "integration_testing"
    PERFORMANCE_TESTING = "performance_testing"
    EVIDENCE_COLLECTION = "evidence_collection"
    COMPLETE = "complete"


# Mapping from workflow stages to ADO states
STAGE_TO_ADO_STATE: Dict[WorkflowStage, ADOState] = {
    WorkflowStage.PLANNING: ADOState.PLANNING,
    WorkflowStage.CODE_GENERATION: ADOState.IN_DEVELOPMENT,
    WorkflowStage.CODE_REVIEW: ADOState.IN_DEVELOPMENT,
    WorkflowStage.UNIT_TESTING: ADOState.IN_DEVELOPMENT,
    WorkflowStage.QA_TESTING: ADOState.TESTING,
    WorkflowStage.INTEGRATION_TESTING: ADOState.TESTING,
    WorkflowStage.PERFORMANCE_TESTING: ADOState.TESTING,
    WorkflowStage.EVIDENCE_COLLECTION: ADOState.TESTING,
    WorkflowStage.COMPLETE: ADOState.DONE,
}


@dataclass
class StageConfig:
    """
    Configuration for a workflow stage.

    Defines the agent, evaluation, evidence requirements, and constraints for a stage.
    """

    stage: WorkflowStage
    ado_state: ADOState
    agent_class_name: str  # Will be resolved to class dynamically
    eval_class_name: str  # Will be resolved to class dynamically
    evidence_types: List[str]
    min_eval_score: float = 0.7
    timeout_minutes: int = 30
    description: str = ""
    dependencies: List[WorkflowStage] = field(default_factory=list)


# Default stage configurations
DEFAULT_STAGE_CONFIGS: Dict[WorkflowStage, StageConfig] = {
    WorkflowStage.PLANNING: StageConfig(
        stage=WorkflowStage.PLANNING,
        ado_state=ADOState.PLANNING,
        agent_class_name="PlanningAgent",
        eval_class_name="PlanEval",
        evidence_types=["implementation-plan.md", "requirements-analysis.json"],
        min_eval_score=0.7,
        timeout_minutes=15,
        description="Create implementation plan from requirements",
        dependencies=[],
    ),
    WorkflowStage.CODE_GENERATION: StageConfig(
        stage=WorkflowStage.CODE_GENERATION,
        ado_state=ADOState.IN_DEVELOPMENT,
        agent_class_name="CodeGeneratorAgent",
        eval_class_name="CodeEval",
        evidence_types=["*.py", "*.sql", "code-quality-report.json"],
        min_eval_score=0.75,
        timeout_minutes=30,
        description="Generate Python/PySpark/SQL code from plan",
        dependencies=[WorkflowStage.PLANNING],
    ),
    WorkflowStage.CODE_REVIEW: StageConfig(
        stage=WorkflowStage.CODE_REVIEW,
        ado_state=ADOState.IN_DEVELOPMENT,
        agent_class_name="CodeReviewAgent",
        eval_class_name="CodeReviewEval",
        evidence_types=["code-review-report.md", "code-review-summary.json"],
        min_eval_score=0.7,
        timeout_minutes=15,
        description="Review code for security, logic, and performance issues",
        dependencies=[WorkflowStage.CODE_GENERATION],
    ),
    WorkflowStage.UNIT_TESTING: StageConfig(
        stage=WorkflowStage.UNIT_TESTING,
        ado_state=ADOState.IN_DEVELOPMENT,
        agent_class_name="TestGeneratorAgent",
        eval_class_name="TestEval",
        evidence_types=[
            "test_*.py",
            "pytest-report.html",
            "coverage-report.html",
            "coverage.json",
        ],
        min_eval_score=0.8,
        timeout_minutes=20,
        description="Generate and run unit tests with 80% coverage",
        dependencies=[WorkflowStage.CODE_REVIEW],  # Code must pass review first
    ),
    WorkflowStage.QA_TESTING: StageConfig(
        stage=WorkflowStage.QA_TESTING,
        ado_state=ADOState.TESTING,
        agent_class_name="QAAgent",
        eval_class_name="QAEval",
        evidence_types=[
            "*.png",
            "*.jpg",
            "playwright-report.html",
            "console-logs.txt",
        ],
        min_eval_score=0.75,
        timeout_minutes=25,
        description="Run Playwright UI tests with screenshot evidence",
        dependencies=[WorkflowStage.UNIT_TESTING],
    ),
    WorkflowStage.INTEGRATION_TESTING: StageConfig(
        stage=WorkflowStage.INTEGRATION_TESTING,
        ado_state=ADOState.TESTING,
        agent_class_name="IntegrationTestAgent",
        eval_class_name="IntegrationEval",
        evidence_types=[
            "api-test-results.json",
            "db-integration-results.json",
            "integration-report.html",
        ],
        min_eval_score=0.7,
        timeout_minutes=20,
        description="Run integration tests for APIs and databases",
        dependencies=[WorkflowStage.UNIT_TESTING],
    ),
    WorkflowStage.PERFORMANCE_TESTING: StageConfig(
        stage=WorkflowStage.PERFORMANCE_TESTING,
        ado_state=ADOState.TESTING,
        agent_class_name="PerformanceTestAgent",
        eval_class_name="PerformanceEval",
        evidence_types=[
            "load-test-report.html",
            "response-times.json",
            "performance-metrics.json",
        ],
        min_eval_score=0.7,
        timeout_minutes=30,
        description="Run performance and load tests",
        dependencies=[WorkflowStage.INTEGRATION_TESTING],
    ),
    WorkflowStage.EVIDENCE_COLLECTION: StageConfig(
        stage=WorkflowStage.EVIDENCE_COLLECTION,
        ado_state=ADOState.TESTING,
        agent_class_name="EvidenceCollectorAgent",
        eval_class_name="EvidenceEval",
        evidence_types=["summary.md", "metadata.json"],
        min_eval_score=0.9,
        timeout_minutes=10,
        description="Collect and organize all stage evidence",
        dependencies=[
            WorkflowStage.QA_TESTING,
            WorkflowStage.INTEGRATION_TESTING,
            WorkflowStage.PERFORMANCE_TESTING,
        ],
    ),
    WorkflowStage.COMPLETE: StageConfig(
        stage=WorkflowStage.COMPLETE,
        ado_state=ADOState.DONE,
        agent_class_name="ADOUpdaterAgent",
        eval_class_name="CompletionEval",
        evidence_types=[],
        min_eval_score=1.0,
        timeout_minutes=10,
        description="Update ADO work item with results and evidence",
        dependencies=[WorkflowStage.EVIDENCE_COLLECTION],
    ),
}


@dataclass
class StateTransition:
    """Represents a state transition in the workflow."""

    from_stage: WorkflowStage
    to_stage: WorkflowStage
    timestamp: datetime
    success: bool
    eval_score: Optional[float] = None
    notes: str = ""


class WorkflowStateMachine:
    """
    State machine for managing workflow stage transitions.

    Validates transitions, tracks progress, and enforces dependencies.
    """

    def __init__(
        self,
        stage_configs: Optional[Dict[WorkflowStage, StageConfig]] = None,
    ):
        """
        Initialize the state machine.

        Args:
            stage_configs: Custom stage configurations (uses defaults if None)
        """
        self.stage_configs = stage_configs or DEFAULT_STAGE_CONFIGS
        self.current_stage: Optional[WorkflowStage] = None
        self.transition_history: List[StateTransition] = []
        self.stage_results: Dict[WorkflowStage, Any] = {}

    def get_stage_config(self, stage: WorkflowStage) -> StageConfig:
        """Get configuration for a workflow stage."""
        return self.stage_configs[stage]

    def get_ado_state(self, stage: WorkflowStage) -> ADOState:
        """Get the ADO state for a workflow stage."""
        return STAGE_TO_ADO_STATE[stage]

    def can_transition_to(self, target_stage: WorkflowStage) -> tuple[bool, str]:
        """
        Check if transition to target stage is allowed.

        Args:
            target_stage: The stage to transition to

        Returns:
            Tuple of (allowed, reason)
        """
        config = self.get_stage_config(target_stage)

        # Check dependencies
        for dep in config.dependencies:
            if dep not in self.stage_results:
                return False, f"Dependency {dep.value} not completed"

            # Check if dependency passed evaluation
            dep_result = self.stage_results[dep]
            if not dep_result.get("eval_passed", False):
                return (
                    False,
                    f"Dependency {dep.value} did not pass evaluation",
                )

        return True, "Transition allowed"

    def transition_to(
        self,
        target_stage: WorkflowStage,
        eval_score: Optional[float] = None,
        notes: str = "",
    ) -> bool:
        """
        Transition to a new workflow stage.

        Args:
            target_stage: The stage to transition to
            eval_score: Optional evaluation score
            notes: Optional notes about the transition

        Returns:
            True if transition successful, False otherwise
        """
        can_transition, reason = self.can_transition_to(target_stage)

        if not can_transition:
            raise ValueError(f"Cannot transition to {target_stage.value}: {reason}")

        # Record transition
        transition = StateTransition(
            from_stage=self.current_stage,
            to_stage=target_stage,
            timestamp=datetime.now(),
            success=True,
            eval_score=eval_score,
            notes=notes,
        )
        self.transition_history.append(transition)

        # Update current stage
        self.current_stage = target_stage

        return True

    def record_stage_result(
        self,
        stage: WorkflowStage,
        eval_passed: bool,
        eval_score: float,
        result_data: Dict[str, Any],
    ):
        """
        Record the result of a stage execution.

        Args:
            stage: The workflow stage
            eval_passed: Whether the stage evaluation passed
            eval_score: The evaluation score (0.0 to 1.0)
            result_data: Additional result data
        """
        self.stage_results[stage] = {
            "eval_passed": eval_passed,
            "eval_score": eval_score,
            "result_data": result_data,
            "timestamp": datetime.now(),
        }

    def get_next_stages(self) -> List[WorkflowStage]:
        """
        Get the list of stages that can be transitioned to next.

        Returns:
            List of valid next stages
        """
        if self.current_stage is None:
            return [WorkflowStage.PLANNING]

        valid_stages = []
        for stage in WorkflowStage:
            if stage not in self.stage_results:
                can_transition, _ = self.can_transition_to(stage)
                if can_transition:
                    valid_stages.append(stage)

        return valid_stages

    def is_complete(self) -> bool:
        """Check if the workflow is complete."""
        return self.current_stage == WorkflowStage.COMPLETE

    def get_progress_summary(self) -> Dict[str, Any]:
        """
        Get a summary of workflow progress.

        Returns:
            Dictionary with progress information
        """
        total_stages = len(WorkflowStage)
        completed_stages = len(self.stage_results)

        return {
            "current_stage": self.current_stage.value if self.current_stage else None,
            "completed_stages": completed_stages,
            "total_stages": total_stages,
            "progress_percentage": (completed_stages / total_stages) * 100,
            "is_complete": self.is_complete(),
            "transition_count": len(self.transition_history),
        }

    def get_failed_stages(self) -> List[tuple[WorkflowStage, Dict[str, Any]]]:
        """
        Get list of stages that failed evaluation.

        Returns:
            List of tuples (stage, result_data)
        """
        failed = []
        for stage, result in self.stage_results.items():
            if not result.get("eval_passed", False):
                failed.append((stage, result))
        return failed
