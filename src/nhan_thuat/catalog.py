"""Deterministic knowledge catalog projection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import KnowledgeRelation, KnowledgeUnit
from .taxonomy import Taxonomy


@dataclass(frozen=True)
class KnowledgeCatalog:
    taxonomy: Taxonomy
    units: dict[str, KnowledgeUnit]
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
            "indexes": {
                "by_type": self._index_by("type"),
                "by_status": self._index_by("status"),
                "by_primary_domain": self._index_by("primary_domain"),
                "by_evidence_level": self._index_by_evidence_level(),
                "by_evidence_reference": self._index_by_evidence_reference(),
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
