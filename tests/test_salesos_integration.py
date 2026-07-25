"""
SalesOS Integration Test Suite for BusinessOS.
Tests API Gateway endpoints (/salesos/leads, /salesos/health) and full repository integration.
"""

from backend.app.main import BusinessOSGatewayHandler, salesos_plugin


def test_salesos_plugin_loaded_in_gateway() -> None:
    health = salesos_plugin.health_check()
    assert health["plugin_id"] == "com.nhanthuat.salesos"
    assert health["status"] == "HEALTHY"


def test_api_gateway_lead_creation_and_retrieval() -> None:
    # Reset salesos_plugin repository for clean test
    salesos_plugin.capability.lead_repository.clear()

    payload = {
        "customer_name": "Le Van E",
        "phone_number": "+84 977 888 999",
        "lead_source": "Zalo Mini App",
        "product_interest": "BusinessOS Enterprise Pack",
    }
    result = salesos_plugin.process_lead(payload)

    assert result.status == "SUCCESS"
    lead_id = result.lead.object_id

    # Retrieve lead from repository
    fetched_lead = next(
        (l for l in salesos_plugin.capability.lead_repository if l.object_id == lead_id),
        None
    )
    assert fetched_lead is not None
    assert fetched_lead.customer_name == "Le Van E"
    assert fetched_lead.normalized_phone == "0977888999"


def test_api_gateway_unverified_fallback() -> None:
    payload = {
        "customer_name": "Test Fallback",
        "phone_number": "0912345678",
        "lead_source": "Web",
        "product_interest": "SaaS",
        "force_unverified_knowledge": True,
    }
    result = salesos_plugin.process_lead(payload)
    assert result.status == "INSUFFICIENT_VERIFIED_KNOWLEDGE"
    assert result.error_code == "INSUFFICIENT_VERIFIED_KNOWLEDGE"
