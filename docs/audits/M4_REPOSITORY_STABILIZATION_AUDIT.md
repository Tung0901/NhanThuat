# M4 REPOSITORY STABILIZATION AUDIT

**Document ID:** `DOC-AUDIT-M4-001`
**Execution Date:** July 25, 2026

## Git Reality Check

- **Current Branch**: `main`
- **Local Commits**: Ahead of `origin/main` by 1 commit (`8e5f378 feat(personality): freeze NT-DA-0003 Personality domain and knowledge units`)
- **Tracked Modified Files**: 0 files.
- **Staged Files**: 0 files.
- **Untracked Files**: 120+ files. (Including 11 `tests/` files, `src/nhan_thuat/knowledge_engine.py`, `salesos_pack/`, `scripts/`, `tmp_pytest/`, `scratch/`, `skills-lock.json`, and numerous newly created knowledge units).
- **Ignored Generated Files**: `.pytest_cache/`, `.ruff_cache/`, `.venv/`

## Environment & Validation

- **Repository Root**: `d:\NhanThuat`
- **Active Python Interpreter**: `.venv/Scripts/python.exe`
- **Canonical Test Command**: `PYTHONPATH="d:\NhanThuat" python -m pytest`
- **Canonical Validation Command**: `PYTHONPATH="d:\NhanThuat" python scripts/validate_all.py`

## Test Count Discrepancy Resolution

- **Discrepancy**: Reports show 113 tests passing, but some reports cite 119 tests.
- **Root Cause**: There are 11 test files in the `tests/` directory (e.g. `test_m15_runtime_hardening.py`, `test_philosophy_router.py`, `test_salesos_integration.py`, etc.) that are **untracked** (`??` in git status). Because they are untracked, different repository environments or CI runs may or may not include them depending on how the files were created locally.
- **Resolution**: All valid test files will be tracked, and the canonical test command will be documented to establish the exact collected test count for M4-A completion.
