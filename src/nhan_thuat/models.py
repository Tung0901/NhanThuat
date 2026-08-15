"""Typed records for the Nhan Thuat knowledge architecture."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

KnowledgeUnitType = str
LifecycleStatus = str


@dataclass(frozen=True)
class Domain:
    id: str
    slug: str
    type: str
    status: LifecycleStatus
    version: str
    name: str
    description: str
    topics: tuple[str, ...]
    source_path: Path | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any], source_path: Path | None = None) -> Domain:
        return cls(
            id=str(data["id"]),
            slug=str(data["slug"]),
            type=str(data["type"]),
            status=str(data["status"]),
            version=str(data["version"]),
            name=str(data["name"]),
            description=str(data["description"]),
            topics=tuple(str(topic) for topic in data.get("topics", [])),
            source_path=source_path,
        )


@dataclass(frozen=True)
class EvidenceSummary:
    level: str
    references: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> EvidenceSummary:
        return cls(
            level=str(data["level"]),
            references=tuple(str(reference) for reference in data.get("references", [])),
        )


@dataclass(frozen=True)
class KnowledgeRelation:
    source: str
    type: str
    target: str
    note: str | None = None

    def to_mapping(self) -> dict[str, str]:
        data = {"source": self.source, "type": self.type, "target": self.target}
        if self.note is not None:
            data["note"] = self.note
        return data


@dataclass(frozen=True)
class KnowledgeUnit:
    id: str
    type: KnowledgeUnitType
    status: LifecycleStatus
    version: str
    title: str
    summary: str
    primary_domain: str
    secondary_domains: tuple[str, ...]
    definition: str
    conditions: tuple[str, ...]
    exceptions: tuple[str, ...]
    applications: dict[str, tuple[str, ...]]
    risks: tuple[str, ...]
    evidence: EvidenceSummary
    relations: dict[str, tuple[str, ...]]
    tags: tuple[str, ...]
    source_path: Path | None = None
    mechanism: tuple[str, ...] = ()
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_mapping(cls, data: dict[str, Any], source_path: Path | None = None) -> KnowledgeUnit:
        applications = {
            str(name): tuple(str(item) for item in values)
            for name, values in data.get("applications", {}).items()
        }
        relations = {
            str(name): tuple(str(target) for target in targets)
            for name, targets in data.get("relations", {}).items()
        }
        return cls(
            id=str(data["id"]),
            type=str(data["type"]),
            status=str(data["status"]),
            version=str(data["version"]),
            title=str(data["title"]),
            summary=str(data["summary"]),
            primary_domain=str(data["primary_domain"]),
            secondary_domains=tuple(str(domain) for domain in data.get("secondary_domains", [])),
            definition=str(data["definition"]),
            mechanism=tuple(str(step) for step in data.get("mechanism", [])),
            conditions=tuple(str(condition) for condition in data.get("conditions", [])),
            exceptions=tuple(str(exception) for exception in data.get("exceptions", [])),
            applications=applications,
            risks=tuple(str(risk) for risk in data.get("risks", [])),
            evidence=EvidenceSummary.from_mapping(data["evidence"]),
            relations=relations,
            tags=tuple(str(tag) for tag in data.get("tags", [])),
            source_path=source_path,
            raw=dict(data),
        )

    def iter_relations(self) -> tuple[KnowledgeRelation, ...]:
        return tuple(
            KnowledgeRelation(source=self.id, type=relation_type, target=target)
            for relation_type, targets in self.relations.items()
            for target in targets
        )

    def to_mapping(self) -> dict[str, Any]:
        return dict(self.raw)
