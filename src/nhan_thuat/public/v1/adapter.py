"""
Internal adapter mapping the internal KnowledgeEngine to the NhanThuat Public Contract V1.
"""
from typing import List, Dict, Any, Optional

from nhan_thuat.knowledge_engine import KnowledgeEngine, FALLBACK_INSUFFICIENT_KNOWLEDGE
from .provider import NhanThuatProviderV1
from .contracts import (
    KnowledgeQuery,
    KnowledgeResult,
    KnowledgeUnitSummary,
    ReasoningRequest,
    ReasoningResult,
    ContractVersion,
)
from .capabilities import NHANTHUAT_CAPABILITIES, CapabilityDescriptor
from .errors import PublicError, InsufficientVerifiedKnowledgeError


class KnowledgeEngineAdapterV1(NhanThuatProviderV1):
    """
    Adapter implementing the NhanThuatProviderV1 public contract
    using the internal KnowledgeEngine.
    """

    def __init__(self, engine: Optional[KnowledgeEngine] = None):
        self._engine = engine or KnowledgeEngine()
        self._version = ContractVersion(major=1, minor=0, patch=0, identifier="nhanthuat-public")

    def get_unit(self, unit_id: str) -> Optional[Dict[str, Any]]:
        result = self._engine.resolve_latest_active_unit(unit_id)
        if result["status"] == "success":
            return result["unit"]
        return None

    def query_knowledge(self, query: KnowledgeQuery) -> KnowledgeResult:
        internal_results = self._engine.query(
            domain=query.domain_slug,
            unit_type=query.unit_type,
            tag=query.tag,
            status=query.status,
        )
        
        # Apply limit
        limited_results = internal_results[:query.limit]

        summaries = [
            KnowledgeUnitSummary(
                unit_id=unit.unit_id,
                title=unit.title,
                domain=unit.domain,
                status=unit.status,
                description=unit.raw_data.get("metadata", {}).get("description", "")
            )
            for unit in limited_results
        ]

        query_filter = {
            "domain": query.domain_slug,
            "unit_type": query.unit_type,
            "tag": query.tag,
            "status": query.status,
            "limit": query.limit,
        }

        return KnowledgeResult(
            query_filter=query_filter,
            total_matches=len(internal_results),
            units=summaries,
            contract_version=self._version
        )

    def list_domain_units(self, domain_slug: str) -> List[KnowledgeUnitSummary]:
        query = KnowledgeQuery(domain_slug=domain_slug, limit=1000)
        result = self.query_knowledge(query)
        return result.units

    def reason(self, request: ReasoningRequest) -> ReasoningResult:
        # NhanThuat Core does not yet implement native reasoning (it is currently in BusinessOS).
        # Capability is marked as PLANNED.
        raise PublicError(
            message="Reasoning capability is PLANNED but not yet implemented in NhanThuat Core.",
            error_code="CAPABILITY_NOT_IMPLEMENTED"
        )

    def list_capabilities(self) -> List[CapabilityDescriptor]:
        return NHANTHUAT_CAPABILITIES

    def get_contract_metadata(self) -> ContractVersion:
        return self._version
