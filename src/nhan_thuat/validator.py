"""Schema and repository-level validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

from .loader import LoadError, iter_documents, load_document


@dataclass(frozen=True)
class ValidationIssue:
    path: Path
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


def validate_document(data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [error.message for error in sorted(validator.iter_errors(data), key=lambda e: list(e.path))]


def validate_repository(root: str | Path) -> list[ValidationIssue]:
    repo = Path(root)
    schema_dir = repo / "schemas"
    domain_schema = load_document(schema_dir / "domain.schema.json")
    unit_schema = load_document(schema_dir / "knowledge-unit.schema.json")
    epic_schema = load_document(schema_dir / "epic.schema.json")
    issues: list[ValidationIssue] = []
    records: list[tuple[Path, dict[str, Any]]] = []

    targets = [
        (repo / "knowledge" / "domains", domain_schema),
        (repo / "knowledge" / "units", unit_schema),
        (repo / "epics", epic_schema),
    ]
    for directory, schema in targets:
        for path in iter_documents(directory):
            if directory.name == "epics" and path.name != "status.yaml":
                continue
            try:
                data = load_document(path)
            except LoadError as exc:
                issues.append(ValidationIssue(path, str(exc)))
                continue
            for message in validate_document(data, schema):
                issues.append(ValidationIssue(path, message))
            if directory.name == "units":
                records.append((path, data))

    issues.extend(_check_unique_ids(records))
    issues.extend(_check_relations(records))
    return issues


def _check_unique_ids(records: Iterable[tuple[Path, dict[str, Any]]]) -> list[ValidationIssue]:
    seen: dict[str, Path] = {}
    issues: list[ValidationIssue] = []
    for path, data in records:
        record_id = data.get("id")
        if record_id in seen:
            issues.append(ValidationIssue(path, f"duplicate id {record_id}; first seen in {seen[record_id]}"))
        elif isinstance(record_id, str):
            seen[record_id] = path
    return issues


def _check_relations(records: Iterable[tuple[Path, dict[str, Any]]]) -> list[ValidationIssue]:
    materialized = list(records)
    ids = {data.get("id") for _, data in materialized}
    issues: list[ValidationIssue] = []
    for path, data in materialized:
        for relation, targets in data.get("relations", {}).items():
            for target in targets:
                if target not in ids:
                    issues.append(ValidationIssue(path, f"broken relation {relation}: {target}"))
    return issues

