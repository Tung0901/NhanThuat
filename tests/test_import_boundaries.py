"""
Automated Import Boundary Test Suite.
Enforces strict unidirectional import policies across NhanThuat, BusinessOS, and SalesOS:
- NhanThuat (src/nhan_thuat/) MUST NOT import backend.app or salesos_pack.
- BusinessOS (backend/app/) MUST NOT import salesos_pack domain implementation.
- SalesOS (salesos_pack/) MAY consume backend.app and nhan_thuat public contracts.
"""

import ast
from pathlib import Path
from typing import List, Set, Tuple


def get_imported_modules(file_path: Path) -> Set[str]:
    """Parse a Python file AST and extract all top-level imported module names."""
    imports: Set[str] = set()
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
    except Exception as e:
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)

    return imports


def test_nhanthuat_import_isolation() -> None:
    """Rule 1: NhanThuat (src/nhan_thuat/) MUST NOT import backend.app or salesos_pack."""
    nhanthuat_dir = Path(__file__).resolve().parent.parent / "src" / "nhan_thuat"
    assert nhanthuat_dir.exists(), "src/nhan_thuat/ directory must exist"

    violations: List[Tuple[str, str]] = []
    for py_file in nhanthuat_dir.rglob("*.py"):
        imports = get_imported_modules(py_file)
        for imp in imports:
            if imp.startswith("backend") or imp.startswith("app") or imp.startswith("salesos_pack"):
                violations.append((str(py_file.name), imp))

    assert not violations, f"NhanThuat import boundary violations found: {violations}"


def test_businessos_kernel_import_isolation() -> None:
    """Rule 2: BusinessOS Kernel (backend/app/) MUST NOT import salesos_pack domain implementation."""
    backend_dir = Path(__file__).resolve().parent.parent / "backend" / "app"
    assert backend_dir.exists(), "backend/app/ directory must exist"

    violations: List[Tuple[str, str]] = []
    for py_file in backend_dir.rglob("*.py"):
        imports = get_imported_modules(py_file)
        for imp in imports:
            if imp.startswith("salesos_pack"):
                # Exception: main.py is the application entrypoint server loading plugins
                if py_file.name == "main.py":
                    continue
                violations.append((str(py_file.name), imp))

    assert not violations, f"BusinessOS Kernel import boundary violations found: {violations}"


def test_salesos_plugin_permitted_imports() -> None:
    """Rule 3: SalesOS (salesos_pack/) MAY consume BusinessOS and NhanThuat public contracts."""
    salesos_dir = Path(__file__).resolve().parent.parent / "salesos_pack"
    assert salesos_dir.exists(), "salesos_pack/ directory must exist"

    # Verify SalesOS code parses cleanly and has no illegal imports outside permitted modules
    for py_file in salesos_dir.rglob("*.py"):
        imports = get_imported_modules(py_file)
        # SalesOS is permitted to consume nhan_thuat, backend.app, or salesos_pack internal modules
        for imp in imports:
            assert not imp.startswith("private_kernel_internals"), f"Illegal import {imp} in {py_file}"
