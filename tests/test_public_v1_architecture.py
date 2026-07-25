"""
Architecture boundary tests for NhanThuat Public Contract V1.
"""
import ast
from pathlib import Path


def get_all_imports(file_path: Path) -> set[str]:
    """Helper to extract all import statements from a Python file."""
    imports = set()
    if not file_path.exists():
        return imports
        
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
    except Exception:
        pass
    return imports


def test_public_v1_does_not_import_businessos_or_salesos() -> None:
    public_dir = Path(__file__).resolve().parent.parent / "src" / "nhan_thuat" / "public" / "v1"
    
    for py_file in public_dir.rglob("*.py"):
        imports = get_all_imports(py_file)
        for imp in imports:
            assert not imp.startswith("backend"), f"File {py_file.name} illegally imports BusinessOS module: {imp}"
            assert not imp.startswith("salesos_pack"), f"File {py_file.name} illegally imports SalesOS module: {imp}"


def test_businessos_fixture_only_imports_public_v1() -> None:
    fixture_path = Path(__file__).resolve().parent / "test_public_v1_integration.py"
    imports = get_all_imports(fixture_path)
    
    for imp in imports:
        if imp.startswith("nhan_thuat"):
            assert imp.startswith("nhan_thuat.public.v1"), f"Fixture illegally imports internal module: {imp}"
            assert imp != "nhan_thuat.knowledge_engine", "Fixture must not import KnowledgeEngine directly"
