"""Schema and repository-level validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

from .evidence import CONFIDENCE_LEVELS, SOURCE_KINDS
from .loader import LoadError, iter_documents, load_document
from .naming import (
    validate_filename_contains_id,
    validate_tag_name,
    validate_unit_identifier_matches_type,
)
from .ontology import known_relation_types


DOMAIN_LIFECYCLE_STATES = {
    "idea",
    "draft",
    "review",
    "ready_for_review",
    "approved",
    "frozen",
    "deprecated",
}
DOMAIN_ALLOWED_TRANSITIONS = {
    "idea": {"draft", "deprecated"},
    "draft": {"review", "deprecated"},
    "review": {"ready_for_review", "draft", "deprecated"},
    "ready_for_review": {"approved", "frozen", "review", "deprecated"},
    "approved": {"frozen", "ready_for_review", "deprecated"},
    "frozen": {"deprecated"},
    "deprecated": set(),
}
DOMAIN_MEMBER_GROUP_TYPES = {
    "laws": "law",
    "principles": "principle",
    "models": "model",
    "strategies": "strategy",
    "tools": "tool",
    "cases": "case",
    "evidence_units": "evidence",
    "anti_patterns": "anti-pattern",
    "anti-patterns": "anti-pattern",
    "phenomena": "phenomenon",
}


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
    evidence_schema = load_document(schema_dir / "evidence.schema.json")
    epic_schema = load_document(schema_dir / "epic.schema.json")
    issues: list[ValidationIssue] = []
    records: list[tuple[Path, dict[str, Any]]] = []
    evidence_records: list[tuple[Path, dict[str, Any]]] = []
    epic_records: list[tuple[Path, dict[str, Any]]] = []
    domain_status_records: list[tuple[Path, dict[str, Any]]] = []

    targets = [
        (repo / "knowledge" / "domains", domain_schema),
        (repo / "knowledge" / "units", unit_schema),
        (repo / "knowledge" / "evidence", evidence_schema),
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
            elif directory.name == "evidence":
                evidence_records.append((path, data))
            elif directory.name == "epics":
                epic_records.append((path, data))

    domain_status_records.extend(_load_domain_status_records(repo, issues))
    issues.extend(_check_unique_ids(records))
    issues.extend(_check_relations(records))
    issues.extend(_check_evidence_records(evidence_records, records))
    issues.extend(_check_knowledge_evidence_references(records, evidence_records))
    issues.extend(_check_architecture_rules(records))
    issues.extend(_check_domain_lifecycle(repo, domain_status_records))
    issues.extend(_check_frozen_register(repo, epic_records, domain_status_records, records))
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


def _check_evidence_records(
    evidence_records: Iterable[tuple[Path, dict[str, Any]]],
    unit_records: Iterable[tuple[Path, dict[str, Any]]],
) -> list[ValidationIssue]:
    materialized = list(evidence_records)
    unit_ids = {data.get("id") for _, data in unit_records}
    seen_ids: dict[str, Path] = {}
    issues: list[ValidationIssue] = []
    for path, data in materialized:
        evidence_id = data.get("id")
        if evidence_id in seen_ids:
            issues.append(
                ValidationIssue(path, f"duplicate evidence id {evidence_id}; first seen in {seen_ids[evidence_id]}")
            )
        elif isinstance(evidence_id, str):
            seen_ids[evidence_id] = path
        if isinstance(evidence_id, str):
            message = validate_filename_contains_id(path, evidence_id)
            if message:
                issues.append(ValidationIssue(path, message))
        source = data.get("source", {})
        if isinstance(source, dict) and source.get("kind") not in SOURCE_KINDS:
            issues.append(ValidationIssue(path, f"unknown evidence source kind: {source.get('kind')}"))
        confidence = data.get("confidence", {})
        if isinstance(confidence, dict) and confidence.get("level") not in CONFIDENCE_LEVELS:
            issues.append(ValidationIssue(path, f"unknown confidence level: {confidence.get('level')}"))
        citation_ids = {
            citation.get("id") for citation in data.get("citations", []) if isinstance(citation, dict)
        }
        if len(citation_ids) != len(data.get("citations", [])):
            issues.append(ValidationIssue(path, "citation ids must be unique and present"))
        for claim in data.get("claims", []):
            if not isinstance(claim, dict):
                continue
            for citation_id in claim.get("citations", []):
                if citation_id not in citation_ids:
                    issues.append(ValidationIssue(path, f"claim references unknown citation: {citation_id}"))
        for link_type in ("supports", "contests", "contextualizes"):
            for target in data.get(link_type, []):
                if target not in unit_ids:
                    issues.append(ValidationIssue(path, f"broken evidence {link_type} reference: {target}"))
    return issues


def _check_knowledge_evidence_references(
    records: Iterable[tuple[Path, dict[str, Any]]],
    evidence_records: Iterable[tuple[Path, dict[str, Any]]],
) -> list[ValidationIssue]:
    evidence_ids = {data.get("id") for _, data in evidence_records}
    issues: list[ValidationIssue] = []
    for path, data in records:
        references = data.get("evidence", {}).get("references", [])
        for reference in references:
            if isinstance(reference, str) and reference.startswith("NT-EVIDENCE-") and reference not in evidence_ids:
                issues.append(ValidationIssue(path, f"broken evidence reference: {reference}"))
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


def _load_domain_status_records(repo: Path, issues: list[ValidationIssue]) -> list[tuple[Path, dict[str, Any]]]:
    records: list[tuple[Path, dict[str, Any]]] = []
    for path in iter_documents(repo / "docs" / "domains"):
        if path.name != "status.yaml":
            continue
        try:
            records.append((path, load_document(path)))
        except LoadError as exc:
            issues.append(ValidationIssue(path, str(exc)))
    return records


def _check_domain_lifecycle(
    repo: Path, domain_status_records: Iterable[tuple[Path, dict[str, Any]]]
) -> list[ValidationIssue]:
    registry_path = repo / "knowledge" / "domain-registry.yaml"
    registry_ids: set[str] = set()
    registry_slugs: dict[str, str] = {}
    materialized_records = list(domain_status_records)
    if materialized_records and not registry_path.exists():
        return [ValidationIssue(registry_path, "domain status validation requires domain registry")]
    if registry_path.exists():
        try:
            registry = load_document(registry_path)
            for domain in registry.get("domains", []):
                if not isinstance(domain, dict):
                    continue
                domain_id = domain.get("id")
                slug = domain.get("slug")
                if isinstance(domain_id, str):
                    registry_ids.add(domain_id)
                    if isinstance(slug, str):
                        registry_slugs[domain_id] = slug
        except LoadError as exc:
            return [ValidationIssue(registry_path, str(exc))]

    issues: list[ValidationIssue] = []
    seen_domain_ids: dict[str, Path] = {}
    seen_slugs: dict[str, Path] = {}
    for path, data in materialized_records:
        domain_id = data.get("domain_area_id")
        slug = data.get("slug")
        name = data.get("name")
        status = data.get("status")
        if not isinstance(domain_id, str) or not domain_id.startswith("NT-DA-"):
            issues.append(ValidationIssue(path, "domain status must declare domain_area_id"))
        elif domain_id not in registry_ids:
            issues.append(ValidationIssue(path, f"domain_area_id is not in domain registry: {domain_id}"))
        if isinstance(domain_id, str):
            if domain_id in seen_domain_ids:
                issues.append(ValidationIssue(path, f"duplicate domain status id: {domain_id}"))
            else:
                seen_domain_ids[domain_id] = path
        if not isinstance(slug, str) or not slug:
            issues.append(ValidationIssue(path, "domain status must declare slug"))
        elif isinstance(domain_id, str) and domain_id in registry_slugs and registry_slugs[domain_id] != slug:
            issues.append(ValidationIssue(path, f"domain slug does not match registry for {domain_id}"))
        if isinstance(slug, str):
            if path.parent.name != slug:
                issues.append(ValidationIssue(path, f"domain status path does not match slug: {slug}"))
            if slug in seen_slugs:
                issues.append(ValidationIssue(path, f"duplicate domain status slug: {slug}"))
            else:
                seen_slugs[slug] = path
        if not isinstance(name, str) or not name:
            issues.append(ValidationIssue(path, "domain status must declare name"))
        blockers = data.get("blockers")
        if not isinstance(blockers, list):
            issues.append(ValidationIssue(path, "domain status must declare blockers list"))
        if status not in DOMAIN_LIFECYCLE_STATES:
            issues.append(ValidationIssue(path, f"invalid domain lifecycle state: {status}"))
            continue
        previous_status = data.get("previous_status")
        if isinstance(previous_status, str):
            if previous_status not in DOMAIN_LIFECYCLE_STATES:
                issues.append(ValidationIssue(path, f"invalid previous domain lifecycle state: {previous_status}"))
            allowed = DOMAIN_ALLOWED_TRANSITIONS.get(previous_status, set())
            if status == previous_status:
                issues.append(ValidationIssue(path, f"invalid domain lifecycle transition: {previous_status} -> {status}"))
            elif status not in allowed:
                issues.append(
                    ValidationIssue(path, f"invalid domain lifecycle transition: {previous_status} -> {status}")
                )
        if status == "approved" and not data.get("approved_by"):
            issues.append(ValidationIssue(path, "approved domain must declare approved_by"))
        if status == "frozen":
            if not isinstance(previous_status, str):
                issues.append(ValidationIssue(path, "frozen domain must declare previous_status"))
            if not data.get("approved_by"):
                issues.append(ValidationIssue(path, "frozen domain must declare approved_by"))
            if not data.get("frozen_at"):
                issues.append(ValidationIssue(path, "frozen domain must declare frozen_at"))
            elif not _is_iso_date(data.get("frozen_at")):
                issues.append(ValidationIssue(path, "frozen domain frozen_at must be an ISO date"))
            if blockers:
                issues.append(ValidationIssue(path, "frozen domain must not declare blockers"))
            issues.extend(_check_frozen_domain_members(path, data))
            issues.extend(_check_frozen_domain_artifacts(path, data))
    return issues


def _check_frozen_domain_members(path: Path, data: dict[str, Any]) -> list[ValidationIssue]:
    members = data.get("members")
    if not isinstance(members, dict) or not members:
        return [ValidationIssue(path, "frozen domain must declare non-empty members")]
    issues: list[ValidationIssue] = []
    seen: set[str] = set()
    for group, values in members.items():
        if group not in DOMAIN_MEMBER_GROUP_TYPES:
            issues.append(ValidationIssue(path, f"unknown frozen domain member group: {group}"))
        if not isinstance(values, list) or not values:
            issues.append(ValidationIssue(path, f"frozen domain member group must be a non-empty list: {group}"))
            continue
        for unit_id in values:
            if not isinstance(unit_id, str):
                issues.append(ValidationIssue(path, f"frozen domain member id must be a string: {group}"))
            elif unit_id in seen:
                issues.append(ValidationIssue(path, f"duplicate frozen domain member: {unit_id}"))
            else:
                seen.add(unit_id)
    unit_counts = data.get("unit_counts", {})
    if not isinstance(unit_counts, dict) or not unit_counts:
        issues.append(ValidationIssue(path, "frozen domain must declare unit_counts"))
    else:
        if set(unit_counts) != set(members):
            issues.append(ValidationIssue(path, "unit_counts keys must match frozen domain member groups"))
        for group, values in members.items():
            if isinstance(values, list) and group in unit_counts and unit_counts[group] != len(values):
                issues.append(ValidationIssue(path, f"unit_counts does not match members for {group}"))
    return issues


def _check_frozen_domain_artifacts(path: Path, data: dict[str, Any]) -> list[ValidationIssue]:
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        return [ValidationIssue(path, "frozen domain must declare non-empty artifacts")]
    issues: list[ValidationIssue] = []
    repo = path.parents[3]
    slug = path.parent.name
    artifact_values: list[str] = []
    for artifact in artifacts:
        if not isinstance(artifact, str):
            issues.append(ValidationIssue(path, "frozen domain artifact path must be a string"))
            continue
        artifact_values.append(artifact)
        if not artifact.startswith(f"docs/domains/{slug}/"):
            issues.append(ValidationIssue(path, f"frozen domain artifact is outside domain directory: {artifact}"))
        elif not (repo / artifact).exists():
            issues.append(ValidationIssue(path, f"frozen domain artifact does not exist: {artifact}"))
    if len(set(artifact_values)) != len(artifact_values):
        issues.append(ValidationIssue(path, "frozen domain artifacts must be unique"))
    if path.name == "status.yaml" and slug:
        status_path = f"docs/domains/{slug}/status.yaml"
        if status_path not in artifacts:
            issues.append(ValidationIssue(path, "frozen domain artifacts must include status.yaml"))
        actual_artifacts = {
            item.relative_to(repo).as_posix()
            for item in path.parent.iterdir()
            if item.is_file()
        }
        if set(artifact_values) != actual_artifacts:
            issues.append(ValidationIssue(path, "frozen domain artifacts must match domain file inventory"))
    return issues


def _check_frozen_register(
    repo: Path,
    epic_records: Iterable[tuple[Path, dict[str, Any]]],
    domain_status_records: Iterable[tuple[Path, dict[str, Any]]],
    unit_records: Iterable[tuple[Path, dict[str, Any]]],
) -> list[ValidationIssue]:
    register_path = repo / "governance" / "frozen-register.yaml"
    if not register_path.exists():
        return [
            ValidationIssue(
                register_path,
                f"frozen domain is not registered: {path.relative_to(repo).as_posix()}",
            )
            for path, data in domain_status_records
            if data.get("status") == "frozen" and path.is_relative_to(repo)
        ]
    try:
        register = load_document(register_path)
    except LoadError as exc:
        return [ValidationIssue(register_path, str(exc))]
    epics_by_relative_path = {
        path.relative_to(repo).as_posix(): data for path, data in epic_records if path.is_relative_to(repo)
    }
    domains_by_relative_path = {
        path.relative_to(repo).as_posix(): data for path, data in domain_status_records if path.is_relative_to(repo)
    }
    units_by_id = {data.get("id"): data for _, data in unit_records}
    issues: list[ValidationIssue] = []
    seen_entries: dict[tuple[str, str], Path] = {}
    seen_sources: dict[str, str] = {}
    for entry in register.get("entries", []):
        if not isinstance(entry, dict):
            continue
        entry_id = entry.get("id")
        entry_type = entry.get("type")
        source = entry.get("source")
        if isinstance(entry_id, str) and isinstance(entry_type, str):
            key = (entry_type, entry_id)
            if key in seen_entries:
                issues.append(ValidationIssue(register_path, f"duplicate frozen entry: {entry_type} {entry_id}"))
            else:
                seen_entries[key] = register_path
        if isinstance(source, str):
            if source in seen_sources:
                issues.append(ValidationIssue(register_path, f"duplicate frozen source: {source}"))
            else:
                seen_sources[source] = str(entry_id)
        if entry_type == "epic":
            issues.extend(_check_frozen_epic_entry(register_path, entry, epics_by_relative_path))
        elif entry_type == "domain_area":
            for field in ("id", "type", "title", "status", "source", "approved_by", "frozen_at", "rationale"):
                if not entry.get(field):
                    issues.append(ValidationIssue(register_path, f"frozen domain entry must declare {field}"))
            issues.extend(
                _check_frozen_domain_entry(
                    register_path,
                    entry,
                    domains_by_relative_path,
                    units_by_id,
                )
            )
    domain_register_ids = {
        entry.get("id")
        for entry in register.get("entries", [])
        if isinstance(entry, dict) and entry.get("type") == "domain_area" and entry.get("status") == "frozen"
    }
    for source, data in domains_by_relative_path.items():
        domain_id = data.get("domain_area_id")
        if data.get("status") == "frozen" and domain_id not in domain_register_ids:
            issues.append(ValidationIssue(register_path, f"frozen domain is not registered: {source}"))
    return issues


def _check_frozen_epic_entry(
    register_path: Path,
    entry: dict[str, Any],
    epics_by_relative_path: dict[str, dict[str, Any]],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    source = entry.get("source")
    if not isinstance(source, str):
        issues.append(ValidationIssue(register_path, "frozen epic entry must declare source"))
        return issues
    source_data = epics_by_relative_path.get(source)
    if source_data is None:
        issues.append(ValidationIssue(register_path, f"frozen source does not exist: {source}"))
        return issues
    if source_data.get("status") != "frozen":
        issues.append(ValidationIssue(register_path, f"frozen source is not frozen: {source}"))
    return issues


def _check_frozen_domain_entry(
    register_path: Path,
    entry: dict[str, Any],
    domains_by_relative_path: dict[str, dict[str, Any]],
    units_by_id: dict[Any, dict[str, Any]],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    source = entry.get("source")
    if not isinstance(source, str):
        issues.append(ValidationIssue(register_path, "frozen domain entry must declare source"))
        return issues
    source_data = domains_by_relative_path.get(source)
    if source_data is None:
        issues.append(ValidationIssue(register_path, f"frozen source does not exist: {source}"))
        return issues
    if entry.get("id") != source_data.get("domain_area_id"):
        issues.append(ValidationIssue(register_path, f"frozen domain id does not match source: {source}"))
    if entry.get("status") != "frozen":
        issues.append(ValidationIssue(register_path, f"frozen domain register entry is not frozen: {source}"))
    if source_data.get("status") != "frozen":
        issues.append(ValidationIssue(register_path, f"frozen source is not frozen: {source}"))
    if entry.get("title") != source_data.get("name"):
        issues.append(ValidationIssue(register_path, f"frozen domain title does not match source: {source}"))
    for field in ("approved_by", "frozen_at"):
        if not entry.get(field):
            issues.append(ValidationIssue(register_path, f"frozen domain entry must declare {field}"))
        elif source_data.get(field) != entry.get(field):
            issues.append(ValidationIssue(register_path, f"frozen domain {field} does not match source: {source}"))
    if entry.get("frozen_at") and not _is_iso_date(entry.get("frozen_at")):
        issues.append(ValidationIssue(register_path, f"frozen domain entry frozen_at must be an ISO date: {source}"))
    for group, unit_id in _domain_member_ids(source_data):
        unit = units_by_id.get(unit_id)
        if unit is None:
            issues.append(ValidationIssue(register_path, f"frozen domain member does not exist: {unit_id}"))
            continue
        expected_type = DOMAIN_MEMBER_GROUP_TYPES.get(group)
        if expected_type is not None and unit.get("type") != expected_type:
            issues.append(ValidationIssue(register_path, f"frozen domain member type mismatch: {group} {unit_id}"))
        if unit.get("status") != "frozen":
            issues.append(ValidationIssue(register_path, f"frozen domain member is not frozen: {unit_id}"))
    return issues


def _domain_member_ids(data: dict[str, Any]) -> list[tuple[str, str]]:
    members = data.get("members", {})
    if not isinstance(members, dict):
        return []
    ids: list[tuple[str, str]] = []
    for group, value in members.items():
        if isinstance(value, list):
            ids.extend((str(group), item) for item in value if isinstance(item, str))
    return ids


def _is_iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True
