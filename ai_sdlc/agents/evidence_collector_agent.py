"""
Evidence Collector Agent

Collects and organizes all evidence artifacts from workflow stages.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent


class EvidenceCollectorAgent(BaseAgent):
    """
    Agent for collecting and organizing evidence.

    Aggregates all evidence from previous stages and creates summary documentation.
    """

    def execute(
        self,
        input_data: Dict[str, Any],
        timeout_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Collect and organize evidence from all stages.

        Args:
            input_data: Dictionary with data from all previous stages
            timeout_seconds: Optional timeout

        Returns:
            Result dictionary with evidence summary
        """
        self._log_start()

        try:
            # Get data from all previous stages
            previous_stages = input_data.get("previous_stages", {})

            # Collect evidence paths from each stage
            all_evidence = self._collect_all_evidence(previous_stages)

            # Create evidence metadata
            metadata = self._create_evidence_metadata(all_evidence, previous_stages)
            metadata_file = self._save_evidence_file(
                "metadata.json",
                json.dumps(metadata, indent=2),
            )

            # Create summary markdown
            summary = self._create_evidence_summary(all_evidence, previous_stages)
            summary_file = self._save_evidence_file("summary.md", summary)

            # Organize evidence by category
            organized_evidence = self._organize_evidence_by_category(all_evidence)

            evidence_paths = [metadata_file, summary_file]

            # Optionally create persistent artifact package in ADO
            artifact_package_info = None
            create_persistent_artifact = input_data.get(
                "create_persistent_artifact", False
            )
            if create_persistent_artifact:
                artifact_package_info = self._create_persistent_artifact(
                    all_evidence, previous_stages, input_data
                )

            self._log_complete(True)

            result_data = {
                "total_artifacts": len(all_evidence),
                "organized_evidence": organized_evidence,
                "metadata": metadata,
                "summary_file": summary_file,
                "work_item_id": self.work_item_id,
            }

            if artifact_package_info:
                result_data["artifact_package"] = artifact_package_info

            return self._create_result(
                success=True, data=result_data, evidence_paths=evidence_paths
            )

        except Exception as e:
            self.logger.error(f"Error collecting evidence: {e}")
            return self._create_result(
                success=False,
                error_message=f"Evidence collection failed: {e}",
            )

    def _collect_all_evidence(
        self, previous_stages: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Collect evidence from all previous stages.

        Args:
            previous_stages: Dictionary of stage results

        Returns:
            List of evidence items
        """
        all_evidence = []

        stage_names = [
            "planning",
            "code_generation",
            "unit_testing",
            "qa_testing",
            "integration_testing",
            "performance_testing",
        ]

        for stage_name in stage_names:
            stage_data = previous_stages.get(stage_name, {})
            if not stage_data:
                continue

            # Get evidence paths from stage data
            evidence_paths = stage_data.get("evidence_paths", [])

            for path in evidence_paths:
                evidence_item = {
                    "stage": stage_name,
                    "path": path,
                    "filename": Path(path).name,
                    "type": self._classify_evidence_type(path),
                    "exists": Path(path).exists() if path else False,
                }
                all_evidence.append(evidence_item)

        return all_evidence

    def _classify_evidence_type(self, path: str) -> str:
        """
        Classify evidence type based on filename.

        Args:
            path: File path

        Returns:
            Evidence type (plan, code, test, screenshot, report, etc.)
        """
        filename = Path(path).name.lower()

        if "plan" in filename:
            return "plan"
        elif filename.endswith(".py"):
            if "test_" in filename:
                return "test_code"
            return "source_code"
        elif filename.endswith((".png", ".jpg", ".jpeg")):
            return "screenshot"
        elif "coverage" in filename:
            return "coverage_report"
        elif "report" in filename:
            return "test_report"
        elif filename.endswith(".json"):
            return "data"
        elif filename.endswith(".sql"):
            return "sql_code"
        elif filename.endswith(".log") or filename.endswith(".txt"):
            return "logs"
        else:
            return "other"

    def _organize_evidence_by_category(
        self, all_evidence: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Organize evidence by category.

        Args:
            all_evidence: List of evidence items

        Returns:
            Dictionary with evidence organized by type
        """
        organized = {}

        for item in all_evidence:
            evidence_type = item["type"]
            if evidence_type not in organized:
                organized[evidence_type] = []
            organized[evidence_type].append(item)

        return organized

    def _create_evidence_metadata(
        self,
        all_evidence: List[Dict[str, Any]],
        previous_stages: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create evidence metadata.

        Args:
            all_evidence: List of evidence items
            previous_stages: Stage results

        Returns:
            Metadata dictionary
        """
        return {
            "work_item_id": self.work_item_id,
            "collected_at": datetime.now().isoformat(),
            "total_artifacts": len(all_evidence),
            "artifacts_by_stage": {
                stage: len([e for e in all_evidence if e["stage"] == stage])
                for stage in set(e["stage"] for e in all_evidence)
            },
            "artifacts_by_type": {
                etype: len([e for e in all_evidence if e["type"] == etype])
                for etype in set(e["type"] for e in all_evidence)
            },
            "workflow_summary": {
                "planning_completed": "planning" in previous_stages,
                "code_generated": "code_generation" in previous_stages,
                "tests_passed": previous_stages.get("unit_testing", {}).get(
                    "tests_passed", False
                ),
                "qa_completed": "qa_testing" in previous_stages,
                "integration_tested": "integration_testing" in previous_stages,
                "performance_tested": "performance_testing" in previous_stages,
            },
            "evidence_paths": [e["path"] for e in all_evidence],
        }

    def _create_evidence_summary(
        self,
        all_evidence: List[Dict[str, Any]],
        previous_stages: Dict[str, Dict[str, Any]],
    ) -> str:
        """
        Create evidence summary markdown.

        Args:
            all_evidence: List of evidence items
            previous_stages: Stage results

        Returns:
            Summary markdown
        """
        # Count artifacts by stage
        planning_count = len([e for e in all_evidence if e["stage"] == "planning"])
        code_count = len([e for e in all_evidence if e["stage"] == "code_generation"])
        unit_test_count = len([e for e in all_evidence if e["stage"] == "unit_testing"])
        qa_count = len([e for e in all_evidence if e["stage"] == "qa_testing"])
        integration_count = len(
            [e for e in all_evidence if e["stage"] == "integration_testing"]
        )
        perf_count = len(
            [e for e in all_evidence if e["stage"] == "performance_testing"]
        )

        # Get test results
        unit_test_data = previous_stages.get("unit_testing", {})
        coverage_data = unit_test_data.get("coverage", {})
        coverage_pct = coverage_data.get("coverage_percentage", 0.0)

        qa_data = previous_stages.get("qa_testing", {})
        qa_results = qa_data.get("test_results", {})

        integration_data = previous_stages.get("integration_testing", {})
        integration_results = integration_data.get("api_tests", {})

        perf_data = previous_stages.get("performance_testing", {})
        perf_metrics = perf_data.get("performance_metrics", {})

        summary = f"""# Workflow Evidence Summary

**Work Item ID:** {self.work_item_id}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Artifacts:** {len(all_evidence)}

---

## Workflow Execution Summary

### ✅ All Stages Completed

1. **Planning** - Implementation plan created
2. **Code Generation** - Source code generated
3. **Unit Testing** - Tests passed with {coverage_pct:.1f}% coverage
4. **QA Testing** - UI tests completed with screenshots
5. **Integration Testing** - API and database tests passed
6. **Performance Testing** - Load tests and benchmarks completed

---

## Evidence Artifacts by Stage

### 1. Planning ({planning_count} artifacts)
- Implementation plan document
- Requirements analysis

### 2. Code Generation ({code_count} artifacts)
- Source code files (Python, PySpark, SQL)
- Code quality reports

### 3. Unit Testing ({unit_test_count} artifacts)
- Test files
- Test execution results
- Coverage reports ({coverage_pct:.1f}%)

### 4. QA Testing ({qa_count} artifacts)
- Playwright test scripts
- Screenshots ({len([e for e in all_evidence if e["type"] == "screenshot"])} screenshots)
- Console logs
- HTML test report

### 5. Integration Testing ({integration_count} artifacts)
- API test results
- Database integration results
- Integration test report

### 6. Performance Testing ({perf_count} artifacts)
- Load test results
- Response time measurements
- Performance metrics
- Resource usage data

---

## Test Results Summary

### Unit Tests
- **Tests Passed:** {unit_test_data.get("test_results", {}).get("passed", 0)}
- **Tests Failed:** {unit_test_data.get("test_results", {}).get("failed", 0)}
- **Coverage:** {coverage_pct:.1f}%
- **Status:** {'✅ PASSED' if coverage_pct >= 80.0 else '❌ FAILED'}

### QA Tests
- **Tests Passed:** {qa_results.get("passed", 0)}
- **Tests Failed:** {qa_results.get("failed", 0)}
- **Screenshots:** {len([e for e in all_evidence if e["type"] == "screenshot"])}
- **Status:** {'✅ PASSED' if qa_results.get("failed", 0) == 0 else '❌ FAILED'}

### Integration Tests
- **Tests Passed:** {integration_results.get("passed", 0)}
- **Tests Failed:** {integration_results.get("failed", 0)}
- **Status:** {'✅ PASSED' if integration_results.get("failed", 0) == 0 else '❌ FAILED'}

### Performance Tests
- **Avg Response Time:** {perf_metrics.get("overall_avg_response_time_ms", 0):.1f}ms
- **Max Response Time:** {perf_metrics.get("overall_max_response_time_ms", 0):.1f}ms
- **Success Rate:** {perf_metrics.get("success_rate_percentage", 0):.1f}%
- **Meets 2s Requirement:** {'✅ YES' if perf_metrics.get("meets_2s_requirement") else '❌ NO'}

---

## Quality Gates

| Gate | Requirement | Result | Status |
|------|-------------|--------|--------|
| Test Coverage | ≥ 80% | {coverage_pct:.1f}% | {'✅ PASS' if coverage_pct >= 80.0 else '❌ FAIL'} |
| Unit Tests | All Pass | {unit_test_data.get("tests_passed", False)} | {'✅ PASS' if unit_test_data.get("tests_passed") else '❌ FAIL'} |
| QA Tests | All Pass | {qa_results.get("failed", 0) == 0} | {'✅ PASS' if qa_results.get("failed", 0) == 0 else '❌ FAIL'} |
| Integration Tests | All Pass | {integration_results.get("failed", 0) == 0} | {'✅ PASS' if integration_results.get("failed", 0) == 0 else '❌ FAIL'} |
| Response Time | < 2s | {perf_metrics.get("overall_max_response_time_ms", 0):.0f}ms | {'✅ PASS' if perf_metrics.get("meets_2s_requirement") else '❌ FAIL'} |

---

## Evidence Files

### Planning
"""

        # Add file listings
        for stage in [
            "planning",
            "code_generation",
            "unit_testing",
            "qa_testing",
            "integration_testing",
            "performance_testing",
        ]:
            stage_evidence = [e for e in all_evidence if e["stage"] == stage]
            if stage_evidence:
                summary += f"\n### {stage.replace('_', ' ').title()}\n"
                for item in stage_evidence:
                    summary += f"- `{item['filename']}` ({item['type']})\n"

        summary += f"""

---

## Next Steps

1. Review all evidence artifacts
2. Verify quality gates are met
3. Update ADO work item with results
4. Proceed with deployment or request changes

---

**Evidence Collection Completed**
**Generated by:** AI-SDLC Evidence Collector Agent
"""

        return summary

    def _create_persistent_artifact(
        self,
        all_evidence: List[Dict[str, Any]],
        previous_stages: Dict[str, Dict[str, Any]],
        input_data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Create a persistent artifact package in Azure Artifacts.

        Args:
            all_evidence: List of all evidence items
            previous_stages: Stage results
            input_data: Input data containing ADO config

        Returns:
            Artifact package info or None if creation fails
        """
        try:
            # Get ADO plugin from input data
            ado_plugin = input_data.get("ado_plugin")
            ado_config = input_data.get("ado_config")
            artifact_version = input_data.get("artifact_version", "1.0.0")

            if not ado_plugin or not ado_config:
                self.logger.warning(
                    "ADO plugin or config not provided, skipping persistent artifact creation"
                )
                return None

            # Convert evidence dict to EvidenceItem-like objects
            from ai_sdlc.evidence import EvidenceItem, EvidenceCategory

            evidence_items = []
            for evidence in all_evidence:
                if evidence.get("exists"):
                    try:
                        # Parse category from type
                        category_map = {
                            "plan": EvidenceCategory.PLAN,
                            "source_code": EvidenceCategory.CODE,
                            "sql_code": EvidenceCategory.CODE,
                            "test_code": EvidenceCategory.TEST,
                            "screenshot": EvidenceCategory.SCREENSHOT,
                            "test_report": EvidenceCategory.REPORT,
                            "coverage_report": EvidenceCategory.REPORT,
                            "data": EvidenceCategory.DATA,
                            "logs": EvidenceCategory.LOG,
                        }
                        category = category_map.get(
                            evidence.get("type"), EvidenceCategory.DOCUMENTATION
                        )

                        item = EvidenceItem(
                            path=evidence["path"],
                            category=category,
                            stage=evidence["stage"],
                            filename=evidence["filename"],
                            size_bytes=(
                                Path(evidence["path"]).stat().st_size
                                if Path(evidence["path"]).exists()
                                else 0
                            ),
                            created_at=datetime.now(),
                            metadata={},
                        )
                        evidence_items.append(item)
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to convert evidence item {evidence.get('filename')}: {e}"
                        )

            if not evidence_items:
                self.logger.warning(
                    "No valid evidence items to create artifact package"
                )
                return None

            # Create artifact package name
            artifact_name = f"pbi-{self.work_item_id}-evidence"

            # Call ADO plugin to create artifact package
            self.logger.info(
                f"Creating persistent artifact package {artifact_name}:{artifact_version} with {len(evidence_items)} files"
            )

            artifact_info = ado_plugin.create_artifact_package(
                work_item_id=self.work_item_id,
                artifact_name=artifact_name,
                artifact_version=artifact_version,
                evidence_items=evidence_items,
                config=ado_config,
            )

            self.logger.info(
                f"Successfully created persistent artifact package: {artifact_info.get('package_url')}"
            )
            return artifact_info

        except Exception as e:
            self.logger.error(f"Failed to create persistent artifact: {e}")
            # Don't fail the workflow if artifact creation fails
            return None
