# AI-SDLC Design Document (Develop-First)

**Date:** January 03, 2026  
**Repo Model:** Multi-repo, Databricks-first  
**Default PR Branch:** develop  
**Release Branch:** main  

---

## 1. Design Goals
- Product Owner–friendly requirement intake
- Acceptance Criteria (AC) as the contract of “done”
- Repo-aware, multi-repo AI code generation
- Deterministic demo evidence generation (no fragile UI screenshots)
- Develop-first branching with gated promotion to main

---

## 2. End-to-End AI-SDLC Flow

1. **PO creates requirement**
   - Uses GitHub Issue Form or `requirements/REQ-*.md`
   - Defines ACs + required demo evidence

2. **AI analyzes repos**
   - Reads `ai_sdlc/project.yml`
   - Scans code patterns, Databricks bundles, notebooks, tests

3. **AI raises PR(s)**
   - Base branch = `develop`
   - One PR per repo (default)
   - CI validates AC verification hooks

4. **Demo Evidence Automation**
   - Databricks bundle job runs demo notebook
   - Evidence written to `/dbfs/tmp/demo/<REQ_ID>/`
   - GitHub Action uploads evidence artifact

5. **Human Gates**
   - Review plan → review PR → review demo evidence
   - Promotion to `main` only after approval

---

## 3. Branching Model

- `develop`: default branch for all AI + human PRs
- `main`: protected release branch
- Promotion via workflow or release PR only

---

## 4. Multi-Repo Support

Defined in `ai_sdlc/project.yml`:
- Repo scopes
- Routing rules
- CI/CD workflows
- Databricks deployment targets

This prevents AI from modifying unintended repos or paths.

---

## 5. Demo Evidence Philosophy

Instead of UI screenshots:
- PNG plots
- HTML reports
- Markdown summaries
- Job logs / JSON metadata

These are:
- Deterministic
- CI-friendly
- Auditable
- Easy for POs to review

---

## 6. What This Enables

- Faster delivery with guardrails
- Clear PO → engineering contract
- Auditable AI-generated changes
- Scalable, enterprise-ready AI-SDLC

