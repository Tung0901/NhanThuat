# CANONICAL VALIDATION COMMANDS

**Document ID:** `DOC-GOV-004`
**Effective Date:** July 25, 2026

## 1. MANDATORY REPOSITORY VALIDATION

All changes to the NhanThuat repository must pass two canonical validation checks before integration.

These commands must be executed from the **repository root** (`d:\NhanThuat` or equivalent).

### 1.1 Python Test Suite (Pytest)

The complete canonical test suite must be run using:

```bash
PYTHONPATH="d:\NhanThuat" python -m pytest
```

*(Note: On Windows PowerShell, the equivalent is `$env:PYTHONPATH="d:\NhanThuat"; python -m pytest` or `$env:PYTHONPATH="d:\NhanThuat"; .\.venv\Scripts\python.exe -m pytest` if using the local virtual environment).*

### 1.2 Knowledge Factory Validation Script

The canonical domain and knowledge unit validation script must be run using:

```bash
PYTHONPATH="d:\NhanThuat" python scripts/validate_all.py
```

## 2. TEST DISCREPANCY RECONCILIATION (M4-A)

- **Prior Discrepancy**: Previous environments reported 113 or 119 tests inconsistently.
- **Root Cause Resolution**: The discrepancy was caused by untracked test files in the `tests/` directory (e.g. integration tests, routing tests) and reliance on different local environments. 
- **Policy Enforcement**: By committing all test files to version control and running the tests under the standardized canonical commands defined above, test discovery behaves deterministically.
