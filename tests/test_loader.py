from pathlib import Path

import pytest

from nhan_thuat.loader import LoadError, load_document


def test_load_yaml_document(tmp_path: Path) -> None:
    path = tmp_path / "sample.yaml"
    path.write_text("id: NT-TEST-0001\n", encoding="utf-8")
    assert load_document(path)["id"] == "NT-TEST-0001"


def test_reject_non_object_root(tmp_path: Path) -> None:
    path = tmp_path / "sample.yaml"
    path.write_text("- item\n", encoding="utf-8")
    with pytest.raises(LoadError, match="root must be an object"):
        load_document(path)

