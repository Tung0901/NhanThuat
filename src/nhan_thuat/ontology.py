"""Ontology relationship model and relation expansion helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import KnowledgeRelation, KnowledgeUnit


@dataclass(frozen=True)
class RelationSpec:
    name: str
    description: str
    reciprocal: bool = False
    cycles_allowed: bool = True


RELATION_SPECS: dict[str, RelationSpec] = {
    "supports": RelationSpec(
        name="supports",
        description="Source strengthens or provides conceptual support for target.",
    ),
    "conflicts_with": RelationSpec(
        name="conflicts_with",
        description="Source conflicts with target or marks a boundary condition.",
        reciprocal=True,
    ),
    "depends_on": RelationSpec(
        name="depends_on",
        description="Source requires target as a prerequisite.",
        cycles_allowed=False,
    ),
    "applies_to": RelationSpec(
        name="applies_to",
        description="Source is applicable to target.",
    ),
}


def known_relation_types() -> tuple[str, ...]:
    return tuple(RELATION_SPECS)


def iter_unit_relations(units: Iterable[KnowledgeUnit]) -> tuple[KnowledgeRelation, ...]:
    return tuple(relation for unit in units for relation in unit.iter_relations())
