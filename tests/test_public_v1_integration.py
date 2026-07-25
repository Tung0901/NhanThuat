"""
BusinessOS Consumer Fixture Test.

This test validates that a BusinessOS application (or downstream consumer)
can use the NhanThuat Public Contract V1 without importing internal modules.
"""
from nhan_thuat.public.v1 import (
    KnowledgeQuery,
    NhanThuatProviderV1,
    InsufficientVerifiedKnowledgeError,
    PublicError
)
from nhan_thuat.public.v1.adapter import KnowledgeEngineAdapterV1


def test_businessos_can_consume_public_contract() -> None:
    # 1. Setup the adapter (In a real BusinessOS deployment, this is injected by the gateway)
    provider: NhanThuatProviderV1 = KnowledgeEngineAdapterV1()

    # 2. Consume Metadata
    contract = provider.get_contract_metadata()
    assert contract.major == 1
    assert contract.identifier == "nhanthuat-public"

    # 3. Query Knowledge using Public Contract Types
    query = KnowledgeQuery(limit=5)
    result = provider.query_knowledge(query)

    assert result.total_matches >= 0
    assert result.contract_version.major == 1
    if result.total_matches > 0:
        assert len(result.units) <= 5
        # Ensure we don't have internal models exposed, only summaries
        assert hasattr(result.units[0], "unit_id")
        assert hasattr(result.units[0], "title")
        assert not hasattr(result.units[0], "raw_data") # Ensure no internal details leaked

    # 4. Fetch Capabilities
    capabilities = provider.list_capabilities()
    assert len(capabilities) > 0
    
    # Ensure Reasoning is PLANNED
    reasoning_cap = next(c for c in capabilities if c.capability_id == "NHANTHUAT-CAP-002")
    assert reasoning_cap.status == "PLANNED"
