"""Deterministic knowledge catalog projection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .evidence import EvidenceRecord, build_traceability
from .models import KnowledgeRelation, KnowledgeUnit
from .taxonomy import Taxonomy


@dataclass(frozen=True)
class KnowledgeCatalog:
    taxonomy: Taxonomy
    units: dict[str, KnowledgeUnit]
    evidence: dict[str, EvidenceRecord]
    relations: tuple[KnowledgeRelation, ...]

    def to_mapping(self) -> dict[str, Any]:
        return {
            "domains": {
                slug: {
                    "id": domain.id,
                    "slug": domain.slug,
                    "name": domain.name,
                    "status": domain.status,
                    "topics": list(domain.topics),
                    "source_path": str(domain.source_path) if domain.source_path else None,
                }
                for slug, domain in self.taxonomy.domains.items()
            },
            "units": {
                unit_id: {
                    **unit.to_mapping(),
                    "source_path": str(unit.source_path) if unit.source_path else None,
                }
                for unit_id, unit in sorted(self.units.items())
            },
            "relations": [relation.to_mapping() for relation in self.relations],
            "evidence": {
                evidence_id: {
                    **evidence.to_mapping(),
                    "source_path": str(evidence.source_path) if evidence.source_path else None,
                }
                for evidence_id, evidence in sorted(self.evidence.items())
            },
            "evidence_traceability": self._evidence_traceability(),
            "indexes": {
                "by_type": self._index_by("type"),
                "by_status": self._index_by("status"),
                "by_primary_domain": self._index_by("primary_domain"),
                "by_evidence_level": self._index_by_evidence_level(),
                "by_evidence_reference": self._index_by_evidence_reference(),
                "by_evidence_confidence": self._index_by_evidence_confidence(),
                "by_tag": self._index_by_tag(),
            },
        }

    def to_legacy_mapping(self) -> dict[str, dict[str, Any]]:
        return {unit_id: unit.to_mapping() for unit_id, unit in sorted(self.units.items())}

    def _index_by(self, field_name: str) -> dict[str, list[str]]:
        index: dict[str, list[str]] = {}
        for unit_id, unit in sorted(self.units.items()):
            value = str(getattr(unit, field_name))
            index.setdefault(value, []).append(unit_id)
        return index

    def _index_by_tag(self) -> dict[str, list[str]]:
        index: dict[str, list[str]] = {}
        for unit_id, unit in sorted(self.units.items()):
            for tag in unit.tags:
                index.setdefault(tag, []).append(unit_id)
        return index

    def _index_by_evidence_level(self) -> dict[str, list[str]]:
        index: dict[str, list[str]] = {}
        for unit_id, unit in sorted(self.units.items()):
            index.setdefault(unit.evidence.level, []).append(unit_id)
        return index

    def _index_by_evidence_reference(self) -> dict[str, list[str]]:
        index: dict[str, list[str]] = {}
        for unit_id, unit in sorted(self.units.items()):
            for reference in unit.evidence.references:
                index.setdefault(reference, []).append(unit_id)
        return index

    def _index_by_evidence_confidence(self) -> dict[str, list[str]]:
        index: dict[str, list[str]] = {}
        for evidence_id, evidence in sorted(self.evidence.items()):
            index.setdefault(evidence.confidence.level, []).append(evidence_id)
        return index

    def _evidence_traceability(self) -> dict[str, Any]:
        traceability = build_traceability(self.evidence.values())
        return {
            "by_unit": traceability.by_unit,
            "by_evidence": traceability.by_evidence,
        }
