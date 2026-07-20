from pathlib import Path

from nhan_thuat.loader import iter_documents, load_document
from nhan_thuat.validator import validate_document, validate_repository

ROOT = Path(__file__).resolve().parents[1]


def test_all_managed_documents_are_valid() -> None:
    assert validate_repository(ROOT) == []


def test_all_five_domains_exist_and_validate() -> None:
    schema = load_document(ROOT / "schemas" / "domain.schema.json")
    paths = iter_documents(ROOT / "knowledge" / "domains")
    assert len(paths) == 5
    assert all(validate_document(load_document(path), schema) == [] for path in paths)


def test_evidence_records_exist_and_validate() -> None:
    schema = load_document(ROOT / "schemas" / "evidence.schema.json")
    paths = iter_documents(ROOT / "knowledge" / "evidence")

    assert len(paths) == 1
    assert all(validate_document(load_document(path), schema) == [] for path in paths)
