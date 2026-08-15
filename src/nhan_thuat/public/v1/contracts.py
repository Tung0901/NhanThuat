"""
Public data contracts for NhanThuat Contract V1.
"""
from dataclasses import dataclass, field
from typing import Any

from .compatibility import ContractVersion
from .provenance import ProvenanceRecord


@dataclass(frozen=True)
class KnowledgeQuery:
    domain_slug: str | None = None
    unit_type: str | None = None
    tag: str | None = None
    status: str | None = None
    limit: int = 100


@dataclass(frozen=True)
class KnowledgeUnitSummary:
    unit_id: str
    title: str
    domain: str
    status: str
    description: str


@dataclass(frozen=True)
class KnowledgeResult:
    query_filter: dict[str, Any]
    total_matches: int
    units: list[KnowledgeUnitSummary]
    contract_version: ContractVersion


@dataclass(frozen=True)
class ReasoningRequest:
    session_id: str
    correlation_id: str
    intent_action: str
    scenario_type: str
    context_stack: dict[str, Any]
    requested_knowledge_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ReasoningResult:
    correlation_id: str
    status_code: str
    primary_lens: str | None = None
    secondary_lenses: list[str] = field(default_factory=list)
    applied_knowledge_units: list[str] = field(default_factory=list)
    recommended_action: str = ""
    reasoning_explanation: str = ""
    causal_provenance: ProvenanceRecord | None = None
    contract_version: ContractVersion | None = None
