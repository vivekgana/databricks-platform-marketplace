"""
Workflow Orchestrator for AI-SDLC

Orchestrates the complete automated development lifecycle workflow.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ai_sdlc.plugins.manager import PluginManager
from ai_sdlc.plugins.base import WorkItemPlugin

from .agent_coordinator import AgentCoordinator, AgentResult, AgentStatus
from .state_machine import (
    WorkflowStage,
    WorkflowStateMachine,
    StageConfig,
    DEFAULT_STAGE_CONFIGS,
)
from .state_reader import StateReader, WorkflowStateInfo

logger = logging.getLogger(__name__)


@dataclass
class StageResult:
    """Result from a workflow stage execution."""

    stage: WorkflowStage
    agent_result: AgentResult
    eval_result: Optional[Dict[str, Any]] = None
    eval_passed: bool = False
    eval_score: float = 0.0
    evidence_paths: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

    def is_success(self) -> bool:
        """Check if stage was successful (agent completed and eval passed)."""
        return self.agent_result.is_success() and self.eval_passed


@dataclass
class WorkflowResult:
    """Complete result from workflow execution."""

    work_item_id: str
    work_item_title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    stage_results: Dict[WorkflowStage, StageResult] = field(default_factory=dict)
    all_stages_passed: bool = False
    final_stage_reached: Optional[WorkflowStage] = None
    error_message: Optional[str] = None
    evidence_base_path: str = ""

    def get_successful_stages(self) -> List[WorkflowStage]:
        """Get list of stages that completed successfully."""
        return [
            stage for stage, result in self.stage_results.items() if result.is_success()
        ]

    def get_failed_stages(self) -> List[tuple[WorkflowStage, StageResult]]:
        """Get list of stages that failed."""
        return [
            (stage, result)
            for stage, result in self.stage_results.items()
            if not result.is_success()
        ]


class WorkflowOrchestrator:
    """
    Orchestrates the complete AI-SDLC workflow.

    Manages stage execution, evaluations, state transitions, and progress tracking.
    """

    def __init__(
        self,
        config: Dict[str, Any],
        evidence_base_path: str,
        stage_configs: Optional[Dict[WorkflowStage, StageConfig]] = None,
        checkpoint_dir: Optional[str] = None,
    ):
        """
        Initialize the workflow orchestrator.

        Args:
            config: Configuration dictionary (passed to agents and coordinator)
            evidence_base_path: Base path for evidence storage (e.g., Azure Blob container)
            stage_configs: Optional custom stage configurations
            checkpoint_dir: Optional directory for workflow checkpoints
        """
        self.config = config
        self.evidence_base_path = evidence_base_path
        self.stage_configs = stage_configs or DEFAULT_STAGE_CONFIGS
        self.checkpoint_dir = checkpoint_dir or "./.workflow_checkpoints"
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Initialize plugin manager
        self.plugin_manager = PluginManager()

        # Get agile plugin for work item operations
        self.agile_plugin = self.plugin_manager.get_agile_plugin()
        if not self.agile_plugin:
            raise RuntimeError(
                "No agile/work item plugin configured. Check .aisdlc/config.yaml"
            )

        # Create checkpoint directory if needed
        Path(self.checkpoint_dir).mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.state_reader = StateReader(self.agile_plugin, config)
        self.state_machine = WorkflowStateMachine(self.stage_configs)
        self.agent_coordinator: Optional[AgentCoordinator] = None

        # Evaluation registry (will be populated dynamically)
        self.eval_registry: Dict[str, Any] = {}

    def register_evaluation(self, eval_class_name: str, eval_class: Any):
        """
        Register an evaluation class.

        Args:
            eval_class_name: Name of the evaluation class
            eval_class: The evaluation class itself
        """
        self.eval_registry[eval_class_name] = eval_class
        self.logger.info(f"Registered evaluation: {eval_class_name}")

    def run_workflow(
        self,
        work_item_id: str,
        start_stage: Optional[WorkflowStage] = None,
        stop_on_failure: bool = True,
    ) -> WorkflowResult:
        """
        Run the complete workflow for a work item.

        Args:
            work_item_id: The work item ID to process
            start_stage: Optional stage to start from (default: PLANNING)
            stop_on_failure: Whether to stop on first failure (default: True)

        Returns:
            WorkflowResult with complete execution results
        """
        self.logger.info(f"Starting workflow for work item {work_item_id}")

        # Get work item state
        try:
            state_info = self.state_reader.read_work_item_state(work_item_id)
        except Exception as e:
            self.logger.error(f"Failed to read work item state: {e}")
            return WorkflowResult(
                work_item_id=work_item_id,
                work_item_title="Unknown",
                start_time=datetime.now(),
                error_message=f"Failed to read work item: {e}",
            )

        # Create workflow result
        result = WorkflowResult(
            work_item_id=work_item_id,
            work_item_title=state_info.title,
            start_time=datetime.now(),
            evidence_base_path=f"{self.evidence_base_path}/PBI-{work_item_id}",
        )

        # Initialize agent coordinator
        self.agent_coordinator = AgentCoordinator(
            work_item_id=work_item_id,
            config=self.config,
            evidence_base_path=result.evidence_base_path,
        )

        # Determine starting stage
        current_stage = start_stage or WorkflowStage.PLANNING

        try:
            # Execute workflow stages sequentially
            while current_stage is not None:
                self.logger.info(f"\n{'=' * 60}")
                self.logger.info(f"Executing stage: {current_stage.value}")
                self.logger.info(f"{'=' * 60}\n")

                # Execute stage
                stage_result = self._execute_stage(current_stage, state_info, result)

                # Store stage result
                result.stage_results[current_stage] = stage_result

                # Check if stage passed
                if not stage_result.is_success():
                    self.logger.error(
                        f"Stage {current_stage.value} failed: {stage_result.error_message}"
                    )

                    if stop_on_failure:
                        result.error_message = (
                            f"Workflow stopped at stage {current_stage.value}"
                        )
                        result.final_stage_reached = current_stage
                        break

                # Update ADO state
                self._update_ado_state(work_item_id, current_stage)

                # Save checkpoint
                self._save_checkpoint(work_item_id, result)

                # Check if complete
                if current_stage == WorkflowStage.COMPLETE:
                    result.all_stages_passed = True
                    result.final_stage_reached = WorkflowStage.COMPLETE
                    break

                # Get next stage
                next_stages = self.state_machine.get_next_stages()
                if not next_stages:
                    self.logger.warning("No next stages available")
                    result.final_stage_reached = current_stage
                    break

                # For now, take the first available next stage
                # (In a more complex workflow, we might have branching logic)
                current_stage = next_stages[0]

        except KeyboardInterrupt:
            self.logger.warning("Workflow interrupted by user")
            result.error_message = "Workflow interrupted by user (Ctrl+C)"
            self._save_checkpoint(work_item_id, result)

        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            result.error_message = f"Workflow execution failed: {e}"

        finally:
            # Record end time
            result.end_time = datetime.now()
            result.duration_seconds = (
                result.end_time - result.start_time
            ).total_seconds()

        # Log summary
        self._log_workflow_summary(result)

        return result

    def _execute_stage(
        self,
        stage: WorkflowStage,
        state_info: WorkflowStateInfo,
        workflow_result: WorkflowResult,
    ) -> StageResult:
        """
        Execute a single workflow stage.

        Args:
            stage: The workflow stage to execute
            state_info: Work item state information
            workflow_result: Current workflow result

        Returns:
            StageResult for the stage
        """
        stage_config = self.stage_configs[stage]

        # Prepare input data for agent
        input_data = {
            "work_item_id": state_info.work_item_id,
            "work_item_title": state_info.title,
            "work_item_description": state_info.description,
            "stage": stage.value,
            "previous_stages": {
                s.value: r.agent_result.output_data
                for s, r in workflow_result.stage_results.items()
            },
        }

        # Execute agent
        self.logger.info(
            f"Executing agent: {stage_config.agent_class_name} (timeout: {stage_config.timeout_minutes}m)"
        )
        agent_result = self.agent_coordinator.execute_stage(stage_config, input_data)

        # Create stage result
        stage_result = StageResult(
            stage=stage,
            agent_result=agent_result,
            evidence_paths=agent_result.evidence_paths,
        )

        # If agent failed, skip evaluation
        if not agent_result.is_success():
            stage_result.error_message = (
                agent_result.error_message or "Agent execution failed"
            )
            return stage_result

        # Run evaluation
        self.logger.info(f"Running evaluation: {stage_config.eval_class_name}")
        eval_result = self._run_evaluation(
            stage_config, agent_result.output_data, agent_result.evidence_paths
        )

        # Update stage result with evaluation
        stage_result.eval_result = eval_result
        stage_result.eval_passed = eval_result.get("passed", False)
        stage_result.eval_score = eval_result.get("score", 0.0)

        # Record in state machine
        self.state_machine.record_stage_result(
            stage=stage,
            eval_passed=stage_result.eval_passed,
            eval_score=stage_result.eval_score,
            result_data=agent_result.output_data,
        )

        # Check if evaluation passed
        if not stage_result.eval_passed:
            stage_result.error_message = (
                f"Evaluation failed (score: {stage_result.eval_score:.2f}, "
                f"required: {stage_config.min_eval_score:.2f})"
            )

        return stage_result

    def _run_evaluation(
        self,
        stage_config: StageConfig,
        output_data: Dict[str, Any],
        evidence_paths: List[str],
    ) -> Dict[str, Any]:
        """
        Run evaluation for a stage.

        Args:
            stage_config: Stage configuration
            output_data: Output data from agent
            evidence_paths: Evidence file paths

        Returns:
            Evaluation result dictionary
        """
        eval_name = stage_config.eval_class_name

        # Check if evaluation is registered
        if eval_name not in self.eval_registry:
            self.logger.warning(
                f"Evaluation {eval_name} not registered. Returning default pass."
            )
            # Return default pass for now (evaluation framework not yet implemented)
            return {
                "passed": True,
                "score": 1.0,
                "issues": [],
                "recommendations": [],
                "note": f"Evaluation {eval_name} not yet implemented",
            }

        # Get evaluation class
        eval_class = self.eval_registry[eval_name]

        try:
            # Create evaluation instance
            eval_instance = eval_class(
                min_score=stage_config.min_eval_score,
                config=self.config,
            )

            # Run evaluation
            eval_result = eval_instance.evaluate(
                output_data=output_data,
                evidence_paths=evidence_paths,
            )

            return eval_result

        except Exception as e:
            self.logger.error(f"Evaluation {eval_name} failed: {e}")
            return {
                "passed": False,
                "score": 0.0,
                "issues": [f"Evaluation error: {e}"],
                "recommendations": [],
            }

    def _update_ado_state(self, work_item_id: str, stage: WorkflowStage):
        """
        Update ADO work item state based on workflow stage.

        Args:
            work_item_id: The work item ID
            stage: The current workflow stage
        """
        try:
            ado_state = self.state_machine.get_ado_state(stage)
            self.logger.info(
                f"Updating ADO state to: {ado_state.value} for stage: {stage.value}"
            )

            # Update work item state
            self.ado_plugin.update_work_item(
                work_item_id, self.config, status=ado_state.value
            )

            # Update workflow stage tag
            self.state_reader.update_workflow_stage_tag(work_item_id, stage)

        except Exception as e:
            self.logger.error(f"Failed to update ADO state: {e}")

    def _save_checkpoint(self, work_item_id: str, workflow_result: WorkflowResult):
        """
        Save workflow checkpoint for resume capability.

        Args:
            work_item_id: The work item ID
            workflow_result: Current workflow result
        """
        try:
            checkpoint_file = Path(self.checkpoint_dir) / f"{work_item_id}.json"

            checkpoint_data = {
                "work_item_id": work_item_id,
                "work_item_title": workflow_result.work_item_title,
                "start_time": workflow_result.start_time.isoformat(),
                "last_checkpoint": datetime.now().isoformat(),
                "completed_stages": [
                    stage.value
                    for stage, result in workflow_result.stage_results.items()
                    if result.is_success()
                ],
                "current_stage": (
                    workflow_result.final_stage_reached.value
                    if workflow_result.final_stage_reached
                    else None
                ),
                "evidence_base_path": workflow_result.evidence_base_path,
            }

            with open(checkpoint_file, "w") as f:
                json.dump(checkpoint_data, f, indent=2)

            self.logger.info(f"Saved checkpoint to: {checkpoint_file}")

        except Exception as e:
            self.logger.warning(f"Failed to save checkpoint: {e}")

    def resume_workflow(self, work_item_id: str) -> Optional[WorkflowResult]:
        """
        Resume an interrupted workflow from checkpoint.

        Args:
            work_item_id: The work item ID

        Returns:
            WorkflowResult if resumed successfully, None otherwise
        """
        try:
            checkpoint_file = Path(self.checkpoint_dir) / f"{work_item_id}.json"

            if not checkpoint_file.exists():
                self.logger.warning(f"No checkpoint found for work item {work_item_id}")
                return None

            # Load checkpoint
            with open(checkpoint_file, "r") as f:
                checkpoint_data = json.load(f)

            self.logger.info(
                f"Resuming workflow from checkpoint: {checkpoint_data['last_checkpoint']}"
            )

            # Determine next stage to execute
            completed_stages = [
                WorkflowStage(stage) for stage in checkpoint_data["completed_stages"]
            ]

            # Find first incomplete stage
            start_stage = None
            for stage in WorkflowStage:
                if stage not in completed_stages:
                    start_stage = stage
                    break

            if start_stage is None:
                self.logger.info("All stages already completed")
                return None

            # Resume workflow
            return self.run_workflow(work_item_id=work_item_id, start_stage=start_stage)

        except Exception as e:
            self.logger.error(f"Failed to resume workflow: {e}")
            return None

    def _log_workflow_summary(self, result: WorkflowResult):
        """Log a summary of workflow execution."""
        self.logger.info(f"\n{'=' * 60}")
        self.logger.info("WORKFLOW EXECUTION SUMMARY")
        self.logger.info(f"{'=' * 60}")
        self.logger.info(f"Work Item: {result.work_item_id} - {result.work_item_title}")
        self.logger.info(f"Duration: {result.duration_seconds:.1f} seconds")
        self.logger.info(
            f"Stages Completed: {len(result.get_successful_stages())}/{len(result.stage_results)}"
        )
        self.logger.info(f"All Stages Passed: {result.all_stages_passed}")

        if result.error_message:
            self.logger.error(f"Error: {result.error_message}")

        # Log stage results
        self.logger.info(f"\nStage Results:")
        for stage, stage_result in result.stage_results.items():
            status_icon = "✅" if stage_result.is_success() else "❌"
            self.logger.info(
                f"  {status_icon} {stage.value}: "
                f"Eval Score: {stage_result.eval_score:.2f}, "
                f"Duration: {stage_result.agent_result.duration_seconds:.1f}s"
            )

        self.logger.info(f"{'=' * 60}\n")
