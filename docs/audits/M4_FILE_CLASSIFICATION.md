# M4 FILE CLASSIFICATION AUDIT

**Document ID:** `DOC-AUDIT-M4-002`
**Execution Date:** July 25, 2026

## 1. FILE OWNERSHIP AND CLASSIFICATION

All currently untracked and modified files have been reviewed and classified according to the M4 Repository Stabilization policy.

### 1.1 NHANTHUAT_CORE
*Definition: Core NhanThuat knowledge engine source code and registered knowledge units.*
- `src/nhan_thuat/knowledge_engine.py`
- All untracked YAML files under `knowledge/units/laws/` (e.g., `NT-LAW-0056` to `NT-LAW-0075`)
- All untracked YAML files under `knowledge/units/models/` (e.g., `NT-MODEL-0009` to `NT-MODEL-0031`)
- All untracked YAML files under `knowledge/units/principles/` (e.g., `NT-PRINCIPLE-0063` to `NT-PRINCIPLE-0113`)

### 1.2 TEST
*Definition: Unit and integration tests that prove system functionality.*
- `tests/test_communication_blueprint.py`
- `tests/test_delegation_blueprint.py`
- `tests/test_hiring_blueprint.py`
- `tests/test_import_boundaries.py`
- `tests/test_leadership_blueprint.py`
- `tests/test_m15_runtime_hardening.py`
- `tests/test_motivation_domain.py`
- `tests/test_philosophy_router.py`
- `tests/test_salesos_integration.py`
- `tests/test_team_building_blueprint.py`
- `tests/test_web_dashboard_api.py`

### 1.3 SALESOS_INTEGRATION_FIXTURE
*Definition: The SalesOS plugin pack used as an integration validation consumer for BusinessOS.*
- `salesos_pack/` (All files inside, including schemas, personas, skills, tools, and events).

### 1.4 BUSINESSOS_INTEGRATION_ADAPTER
*Definition: Interfaces and entrypoints connecting NhanThuat/BusinessOS for runtime execution.*
- `scripts/run_web_dashboard.py`
- `scripts/run_executive_streamlit.py`
- `scripts/app_executive.py`

### 1.5 NHANTHUAT_TOOLING
*Definition: Internal tools and scripts used for managing the repository and NhanThuat.*
- `scripts/check_models.py`
- `scripts/test_nhan_thuat_cli.py`

### 1.6 GENERATED_OR_LOCAL_ONLY
*Definition: Ephemeral files generated during test runs, environment locking, or scratchpads.*
- `scratch/` (One-off generator scripts and temporary validation code)
- `tmp_pytest/` (Generated during pytest runs)
- `skills-lock.json` (Agent skills cache/lock file)

### 1.7 NHANTHUAT_PUBLIC_CONTRACT
*Definition: The new versioned public boundary.*
- *(No existing files fall under this category yet; to be populated in M4-B)*

### 1.8 DOCUMENTATION
*Definition: Governance and markdown artifacts.*
- `docs/audits/M4_REPOSITORY_STABILIZATION_AUDIT.md`
- `docs/governance/CANONICAL_VALIDATION_COMMANDS.md`
- `docs/audits/M4_FILE_CLASSIFICATION.md`

### 1.9 OUT_OF_SCOPE_OR_MISPLACED
*Definition: Files that should be deleted or moved.*
- *(None identified)*

---

## 2. ACTION PLAN FOR CLEAN BASELINE
1. Add `tmp_pytest/`, `scratch/`, and `skills-lock.json` to `.gitignore`.
2. Stage all files in `NHANTHUAT_CORE`, `TEST`, `SALESOS_INTEGRATION_FIXTURE`, `BUSINESSOS_INTEGRATION_ADAPTER`, `NHANTHUAT_TOOLING`, and `DOCUMENTATION`.
3. Commit to baseline.
