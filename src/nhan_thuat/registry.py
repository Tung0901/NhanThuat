"""Repository-backed knowledge registry."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .catalog import KnowledgeCatalog
from .evidence import EvidenceRecord
from .loader import iter_documents, load_document
from .models import Domain, KnowledgeRelation, KnowledgeUnit
from .ontology import iter_unit_relations
from .taxonomy import Taxonomy


@dataclass(frozen=True)
class RegistrySource:
    path: Path
    data: dict[str, Any]


@dataclass(frozen=True)
class KnowledgeRegistry:
    root: Path
    domains: dict[str, Domain]
    units: dict[str, KnowledgeUnit]
    evidence: dict[str, EvidenceRecord]
    relations: tuple[KnowledgeRelation, ...]

    @classmethod
    def load(cls, root: str | Path) -> KnowledgeRegistry:
        repo = Path(root)
        domains = _load_domains(repo)
        units = _load_units(repo)
        evidence = _load_evidence(repo)
        return cls(
            root=repo,
            domains=domains,
            units=units,
            evidence=evidence,
            relations=iter_unit_relations(units.values()),
        )

    @property
    def taxonomy(self) -> Taxonomy:
        return Taxonomy.from_domains(self.domains.values())

    def catalog(self) -> KnowledgeCatalog:
        return KnowledgeCatalog(
            taxonomy=self.taxonomy,
            units=self.units,
            evidence=self.evidence,
            relations=self.relations,
        )

    def get_unit(self, unit_id: str) -> KnowledgeUnit:
        try:
            return self.units[unit_id]
        except KeyError as exc:
            raise KeyError(f"Unknown knowledge unit: {unit_id}") from exc

    def units_by_type(self, unit_type: str) -> tuple[KnowledgeUnit, ...]:
        return tuple(unit for unit in self.units.values() if unit.type == unit_type)

    def units_by_domain(self, domain_slug: str) -> tuple[KnowledgeUnit, ...]:
        return tuple(
            unit
            for unit in self.units.values()
            if unit.primary_domain == domain_slug or domain_slug in unit.secondary_domains
        )

    def get_evidence(self, evidence_id: str) -> EvidenceRecord:
        try:
            return self.evidence[evidence_id]
        except KeyError as exc:
            raise KeyError(f"Unknown evidence record: {evidence_id}") from exc


def load_registry(root: str | Path) -> KnowledgeRegistry:
    return KnowledgeRegistry.load(root)


def build_registry(root: str | Path) -> dict[str, dict[str, Any]]:
    return {unit_id: unit.to_mapping() for unit_id, unit in load_registry(root).units.items()}


def _load_domains(repo: Path) -> dict[str, Domain]:
    domains: dict[str, Domain] = {}
    for source in _iter_sources(repo / "knowledge" / "domains"):
        domain = Domain.from_mapping(source.data, source.path)
        if domain.slug in domains:
            raise ValueError(f"Duplicate domain slug: {domain.slug}")
        domains[domain.slug] = domain
    return dict(sorted(domains.items()))


def _load_units(repo: Path) -> dict[str, KnowledgeUnit]:
    units: dict[str, KnowledgeUnit] = {}
    for source in _iter_sources(repo / "knowledge" / "units"):
        unit = KnowledgeUnit.from_mapping(source.data, source.path)
        if unit.id in units:
            raise ValueError(f"Duplicate id: {unit.id}")
        units[unit.id] = unit
    return dict(sorted(units.items()))


def _load_evidence(repo: Path) -> dict[str, EvidenceRecord]:
    evidence: dict[str, EvidenceRecord] = {}
    for source in _iter_sources(repo / "knowledge" / "evidence"):
        record = EvidenceRecord.from_mapping(source.data, source.path)
        if record.id in evidence:
            raise ValueError(f"Duplicate evidence id: {record.id}")
        evidence[record.id] = record
    return dict(sorted(evidence.items()))


def _iter_sources(directory: Path) -> tuple[RegistrySource, ...]:
    return tuple(RegistrySource(path=path, data=load_document(path)) for path in iter_documents(directory))
