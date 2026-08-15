import subprocess
import sys
from pathlib import Path


def test_public_v1_import_without_businessos():
    """
    Acceptance criterion: Prove src/nhan_thuat/public/v1 remains importable
    without the BusinessOS repository on PYTHONPATH.

    We achieve this by setting PYTHONPATH exclusively to the 'src' directory,
    which isolates the NhanThuat package from 'backend' and 'salesos_pack'.
    """
    repo_root = Path(__file__).resolve().parent.parent
    src_dir = repo_root / "src"

    # A short Python script that tries to import the public contract v1
    # and fails if it cannot.
    test_script = "from nhan_thuat.public.v1 import KnowledgeQuery; print('Import successful')"

    # Run the script in a subprocess with ONLY src in the PYTHONPATH
    # We must also inherit the system environment variables except for PYTHONPATH 
    # to allow Python to run correctly (like PATH).
    import os
    merged_env = os.environ.copy()
    merged_env["PYTHONPATH"] = str(src_dir)

    result = subprocess.run(
        [sys.executable, "-c", test_script],
        env=merged_env,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Failed to import public v1 contract in isolation.\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    assert "Import successful" in result.stdout
