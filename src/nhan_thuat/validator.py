"""Schema and repository-level validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

from .loader import LoadError, iter_documents, load_document
from .naming import (
    validate_filename_contains_id,
    validate_tag_name,
    validate_unit_identifier_matches_type,
)
from .ontology import known_relation_types


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
    epic_records: list[tuple[Path, dict[str, Any]]] = []

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
            elif directory.name == "epics":
                epic_records.append((path, data))

    issues.extend(_check_unique_ids(records))
    issues.extend(_check_relations(records))
    issues.extend(_check_architecture_rules(records))
    issues.extend(_check_frozen_register(repo, epic_records))
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


def _check_architecture_rules(records: Iterable[tuple[Path, dict[str, Any]]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    known_relations = set(known_relation_types())
    for path, data in records:
        record_id = data.get("id")
        record_type = data.get("type")
        if isinstance(record_id, str) and isinstance(record_type, str):
            message = validate_unit_identifier_matches_type(record_id, record_type)
            if message:
                issues.append(ValidationIssue(path, message))
            message = validate_filename_contains_id(path, record_id)
            if message:
                issues.append(ValidationIssue(path, message))
        primary_domain = data.get("primary_domain")
        secondary_domains = data.get("secondary_domains", [])
        if isinstance(primary_domain, str) and primary_domain in secondary_domains:
            issues.append(ValidationIssue(path, "secondary_domains must not include primary_domain"))
        for tag in data.get("tags", []):
            if isinstance(tag, str):
                message = validate_tag_name(tag)
                if message:
                    issues.append(ValidationIssue(path, message))
        for relation in data.get("relations", {}):
            if relation not in known_relations:
                issues.append(ValidationIssue(path, f"unknown relation type: {relation}"))
    return issues


def _check_frozen_register(
    repo: Path, epic_records: Iterable[tuple[Path, dict[str, Any]]]
) -> list[ValidationIssue]:
    register_path = repo / "governance" / "frozen-register.yaml"
    if not register_path.exists():
        return []
    try:
        register = load_document(register_path)
    except LoadError as exc:
        return [ValidationIssue(register_path, str(exc))]
    epics_by_relative_path = {
        path.relative_to(repo).as_posix(): data for path, data in epic_records if path.is_relative_to(repo)
    }
    issues: list[ValidationIssue] = []
    for entry in register.get("entries", []):
        if not isinstance(entry, dict) or entry.get("type") != "epic":
            continue
        source = entry.get("source")
        if not isinstance(source, str):
            issues.append(ValidationIssue(register_path, "frozen epic entry must declare source"))
            continue
        source_data = epics_by_relative_path.get(source)
        if source_data is None:
            issues.append(ValidationIssue(register_path, f"frozen source does not exist: {source}"))
            continue
        if source_data.get("status") != "frozen":
            issues.append(ValidationIssue(register_path, f"frozen source is not frozen: {source}"))
    return issues
