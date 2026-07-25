"""
Public data contracts for NhanThuat Contract V1.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .compatibility import ContractVersion
from .provenance import ProvenanceRecord


@dataclass(frozen=True)
class KnowledgeQuery:
    domain_slug: Optional[str] = None
    unit_type: Optional[str] = None
    tag: Optional[str] = None
    status: Optional[str] = None
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
    query_filter: Dict[str, Any]
    total_matches: int
    units: List[KnowledgeUnitSummary]
    contract_version: ContractVersion


@dataclass(frozen=True)
class ReasoningRequest:
    session_id: str
    correlation_id: str
    intent_action: str
    scenario_type: str
    context_stack: Dict[str, Any]
    requested_knowledge_ids: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ReasoningResult:
    correlation_id: str
    status_code: str
    primary_lens: Optional[str] = None
    secondary_lenses: List[str] = field(default_factory=list)
    applied_knowledge_units: List[str] = field(default_factory=list)
    recommended_action: str = ""
    reasoning_explanation: str = ""
    causal_provenance: Optional[ProvenanceRecord] = None
    contract_version: Optional[ContractVersion] = None
