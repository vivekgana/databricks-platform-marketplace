"""
Planning Agent

Creates implementation plans from work item requirements.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent


class PlanningAgent(BaseAgent):
    """
    Agent for creating implementation plans.

    Analyzes work item requirements and creates detailed implementation plans
    with approach, steps, risks, and dependencies.
    """

    def execute(
        self,
        input_data: Dict[str, Any],
        timeout_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create an implementation plan from work item requirements.

        Args:
            input_data: Dictionary with work item info
            timeout_seconds: Optional timeout

        Returns:
            Result dictionary with plan and evidence paths
        """
        self._log_start()

        try:
            # Extract work item info
            work_item_title = input_data.get("work_item_title", "")
            work_item_description = input_data.get("work_item_description", "")

            if not work_item_title:
                return self._create_result(
                    success=False,
                    error_message="No work item title provided",
                )

            # Generate implementation plan
            plan = self._generate_plan(work_item_title, work_item_description)

            # Save plan as markdown
            plan_file = self._save_evidence_file("implementation-plan.md", plan)

            # Create requirements analysis JSON
            analysis = self._create_requirements_analysis(
                work_item_title, work_item_description
            )
            analysis_file = self._save_evidence_file(
                "requirements-analysis.json", json.dumps(analysis, indent=2)
            )

            self._log_complete(True)

            return self._create_result(
                success=True,
                data={
                    "plan_text": plan,
                    "analysis": analysis,
                    "work_item_id": self.work_item_id,
                },
                evidence_paths=[plan_file, analysis_file],
            )

        except Exception as e:
            self.logger.error(f"Error generating plan: {e}")
            return self._create_result(
                success=False,
                error_message=f"Plan generation failed: {e}",
            )

    def _generate_plan(self, title: str, description: str) -> str:
        """
        Generate implementation plan markdown.

        Args:
            title: Work item title
            description: Work item description

        Returns:
            Plan markdown content
        """
        # In production, this would use LLM to generate plan
        # For now, create a structured template

        plan = f"""# Implementation Plan: {title}

**Work Item ID:** {self.work_item_id}
**Created:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Status:** Draft

---

## 1. Overview

### Objective
{title}

### Description
{description if description else "No detailed description provided."}

---

## 2. Requirements Analysis

### Functional Requirements
- Extract key functionality from work item description
- Identify user-facing features
- Define expected behavior

### Non-Functional Requirements
- Performance requirements
- Security considerations
- Scalability needs

### Acceptance Criteria
- List all acceptance criteria from work item
- Map to implementation tasks
- Define verification methods

---

## 3. Implementation Approach

### Architecture
- Component design
- Module structure
- Data flow

### Technology Stack
- Python 3.10+
- PySpark for data processing
- Delta Lake for storage
- Unity Catalog for governance

### Design Patterns
- Repository pattern for data access
- Factory pattern for object creation
- Strategy pattern for algorithms

---

## 4. Implementation Steps

### Phase 1: Setup and Infrastructure
1. Set up project structure
2. Configure dependencies
3. Create base classes and interfaces
4. Set up logging and error handling

### Phase 2: Core Implementation
1. Implement main business logic
2. Create data models
3. Build API endpoints (if applicable)
4. Implement database operations

### Phase 3: Integration
1. Integrate with existing systems
2. Configure Unity Catalog
3. Set up Delta Lake tables
4. Implement data pipelines

### Phase 4: Testing
1. Write unit tests (target 80% coverage)
2. Create integration tests
3. Perform QA testing
4. Run performance tests

---

## 5. Dependencies

### Internal Dependencies
- Existing services that must be integrated
- Shared libraries and utilities
- Database schemas

### External Dependencies
- Third-party APIs
- External data sources
- Cloud services

### Prerequisite Tasks
- Tasks that must be completed first
- Infrastructure setup required
- Team member assignments

---

## 6. Risks and Mitigation

### Technical Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Integration complexity | High | Medium | Early prototyping and testing |
| Performance issues | Medium | Low | Load testing and optimization |
| Data quality | High | Medium | Validation and monitoring |

### Project Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Timeline delays | Medium | Medium | Buffer time and prioritization |
| Resource availability | Low | Low | Cross-training and documentation |
| Requirement changes | Medium | High | Agile approach and flexibility |

---

## 7. Testing Strategy

### Unit Testing
- Test all public methods
- Mock external dependencies
- Target 80% code coverage
- Use pytest framework

### Integration Testing
- Test API endpoints
- Verify database operations
- Test external integrations
- Use test fixtures

### Performance Testing
- Load testing with realistic data
- Response time benchmarks
- Scalability verification
- Resource usage monitoring

---

## 8. Success Criteria

1. All acceptance criteria met
2. Code coverage ≥ 80%
3. All tests passing
4. Performance benchmarks achieved
5. Code review approved
6. Documentation complete

---

## 9. Timeline Estimate

**Note:** This is a preliminary estimate and may change based on implementation complexity.

- Phase 1 (Setup): 1-2 days
- Phase 2 (Core): 3-5 days
- Phase 3 (Integration): 2-3 days
- Phase 4 (Testing): 2-3 days
- **Total:** 8-13 days

---

## 10. Next Steps

1. Review plan with team
2. Confirm technical approach
3. Finalize timeline
4. Begin Phase 1 implementation
5. Set up regular progress check-ins

---

**Plan Status:** Ready for Review
**Prepared by:** AI-SDLC Planning Agent
"""

        return plan

    def _create_requirements_analysis(
        self, title: str, description: str
    ) -> Dict[str, Any]:
        """
        Create requirements analysis JSON.

        Args:
            title: Work item title
            description: Work item description

        Returns:
            Analysis dictionary
        """
        # In production, would use NLP/LLM to extract requirements
        # For now, create structured template

        analysis = {
            "work_item_id": self.work_item_id,
            "title": title,
            "analyzed_at": datetime.now().isoformat(),
            "complexity": "medium",  # Would be calculated
            "estimated_story_points": 8,  # Would be calculated
            "functional_requirements": [
                "Extracted functional requirement 1",
                "Extracted functional requirement 2",
                "Extracted functional requirement 3",
            ],
            "non_functional_requirements": [
                "Performance: Response time < 2s",
                "Security: Authentication and authorization required",
                "Scalability: Support concurrent users",
            ],
            "acceptance_criteria": [
                {
                    "id": "AC-1",
                    "description": "Acceptance criterion 1",
                    "verification": "test",
                },
                {
                    "id": "AC-2",
                    "description": "Acceptance criterion 2",
                    "verification": "manual",
                },
            ],
            "dependencies": [
                "Dependency on service A",
                "Requires Unity Catalog setup",
            ],
            "risks": [
                {
                    "description": "Integration complexity",
                    "impact": "high",
                    "probability": "medium",
                    "mitigation": "Early prototyping",
                },
            ],
            "components_affected": [
                "module_a.py",
                "module_b.py",
                "api/endpoints.py",
            ],
        }

        return analysis
