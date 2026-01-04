---
req_id: REQ-000
title: "<short title>"
owner: "<product owner>"
product: "<product/domain>"
team: "<team>"
priority: "P1|P2|P3"
status: "Draft|In Review|Approved|In Dev|In QA|Ready for Demo|Done"
target_release: "<vX.Y or date>"
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
links:
  jira: ""
  ado: ""
  pr: ""
  docs: ""

# Multi-repo aware: list the repo(s) this requirement touches.
# Default base branch is develop everywhere.
repos:
  - repo: "vivekgana/databricks-platform-marketplace"
    base_branch: "develop"
    release_branch: "main"
    path_scopes:
      - "src/"
      - "notebooks/"
      - "tests/"
      - "databricks.yml"
    change_types: ["feature", "defect"]
    ci:
      workflow: "ci.yml"
    demo:
      workflow: "demo-evidence.yml"
    deploy:
      targets: ["dev", "stage", "prod"]

demo:
  evidence_path: "dbfs:/tmp/demo/REQ-000/"
  required_assets:
    - "AC-1.png"
    - "AC-2.html"
    - "summary.md"
---

# REQ-000: <short title>

## 1. Problem statement
What problem are we solving, for whom, and why now?

## 2. Personas and users
- Persona A: …
- Persona B: …

## 3. Scope
### In scope
- …
### Out of scope / Non-goals
- …

## 4. Functional requirements
- FR-1 …
- FR-2 …

## 5. Acceptance criteria (AC)
Use Given/When/Then. Each AC must include a verification hook and evidence outputs.

### AC-1
**Given** …  
**When** …  
**Then** …  

**Verify:**  
- test: tests/integration/test_x.py::test_y  OR  
- job: bundle_run: smoke_job              OR  
- query: sql: SELECT ...                  OR  
- manual: screenshot (discouraged unless truly UI-specific)  

**Demo Evidence:**  
- AC-1.png  
- AC-1.html  
- AC-1.txt  

### AC-2
...

## 6. Data & Databricks objects
- Catalog/Schema: …
- Tables: …
- DLT pipelines: …
- Jobs: …
- Notebooks: …

## 7. Observability / Quality gates
- Unit test threshold: …
- Data quality checks: …
- Performance/SLA: …

## 8. Risks & mitigations
- …

## 9. Rollout plan (A/B / feature flags)
- Strategy: canary / A-B / blue-green
- Rollback trigger: …

## 10. Demo script (mapped to AC IDs)
- Step 1 → AC-1 evidence
- Step 2 → AC-2 evidence
