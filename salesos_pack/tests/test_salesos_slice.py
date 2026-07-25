"""
SalesOS Plugin Unit and Integration Test Suite.
Tests all vertical slice requirements for Milestone M14-F.
"""

import json
from pathlib import Path
from salesos_pack.capabilities.lead_intake_capability import LeadIntakeCapability
from salesos_pack.personas.sales_ops_coordinator import SalesOpsCoordinatorPersona
from salesos_pack.plugin import SalesOSPlugin
from salesos_pack.tools.phone_normalizer import normalize_vietnamese_phone


def test_vietnamese_phone_normalization() -> None:
    # Test valid formats
    valid_cases = [
        ("0912345678", "0912345678", "+84912345678"),
        ("+84912345678", "0912345678", "+84912345678"),
        ("84912345678", "0912345678", "+84912345678"),
        ("0912.345.678", "0912345678", "+84912345678"),
        ("0912 345 678", "0912345678", "+84912345678"),
        ("0912-345-678", "0912345678", "+84912345678"),
        ("(0912) 345 678", "0912345678", "+84912345678"),
        ("0389998888", "0389998888", "+84389998888"),
    ]
    for raw, expected_local, expected_e164 in valid_cases:
        is_valid, local, e164, err = normalize_vietnamese_phone(raw)
        assert is_valid is True, f"Failed for {raw}: {err}"
        assert local == expected_local
        assert e164 == expected_e164

    # Test invalid formats
    invalid_cases = [
        "12345",
        "0212345678",  # Invalid prefix (not 03, 05, 07, 08, 09)
        "abc0912345678",
        "",
        None,
    ]
    for raw in invalid_cases:
        is_valid, _, _, _ = normalize_vietnamese_phone(raw)
        assert is_valid is False, f"Should be invalid for {raw}"


def test_valid_lead_intake_workflow_end_to_end() -> None:
    plugin = SalesOSPlugin()
    payload = {
        "customer_name": "Nguyen Van C",
        "phone_number": "0988777666",
        "lead_source": "Facebook Ad",
        "product_interest": "Enterprise SaaS Solution",
        "notes": "Urgent request",
    }
    result = plugin.process_lead(payload)

    assert result.status == "SUCCESS"
    assert result.lead is not None
    assert result.lead.customer_name == "Nguyen Van C"
    assert result.lead.normalized_phone == "0988777666"
    assert result.lead.status == "NEW"
    assert result.lead.checksum.startswith("sha256:")

    assert result.customer is not None
    assert result.customer.name == "Nguyen Van C"
    assert result.customer.phone == "0988777666"

    assert result.assignment is not None
    assert result.assignment.assigned_to_user_id in ["USER-SALES-001", "USER-SALES-002"]
    assert result.assignment.status == "ASSIGNED"

    assert result.next_action is not None
    assert result.next_action.action_type == "SCHEDULE_DISCOVERY_CALL"
    assert "NT-LAW-0054" in result.next_action.backed_by_knowledge_units

    assert result.audit_event is not None
    assert result.audit_event.event_type == "LEAD_INTAKE_COMPLETED"
    assert result.audit_event.checksum.startswith("sha256:")

    assert result.provenance_trace is not None
    assert result.provenance_trace.capability_id == "SALESOS-CAP-001"
    assert "NT-LAW-0054" in result.provenance_trace.knowledge_citations
    assert result.provenance_trace.confidence_score == 0.95


def test_invalid_input_rejection() -> None:
    plugin = SalesOSPlugin()
    # Missing customer_name
    result1 = plugin.process_lead({"phone_number": "0912345678", "lead_source": "Web", "product_interest": "SaaS"})
    assert result1.status == "VALIDATION_ERROR"
    assert "customer_name is required" in result1.message

    # Invalid phone
    result2 = plugin.process_lead({
        "customer_name": "Test",
        "phone_number": "123",
        "lead_source": "Web",
        "product_interest": "SaaS"
    })
    assert result2.status == "VALIDATION_ERROR"
    assert result2.error_code == "PHONE_NORMALIZATION_FAILED"


def test_duplicate_lead_detection() -> None:
    plugin = SalesOSPlugin()
    payload = {
        "customer_name": "Tran Van D",
        "phone_number": "0911222333",
        "lead_source": "Google Search",
        "product_interest": "BusinessOS Pro",
    }
    # First submission -> Success
    res1 = plugin.process_lead(payload)
    assert res1.status == "SUCCESS"

    # Second submission (same phone) -> Duplicate Rejected
    res2 = plugin.process_lead(payload)
    assert res2.status == "DUPLICATE_REJECTED"
    assert res2.error_code == "DUPLICATE_LEAD_DETECTED"
    assert res2.lead.object_id == res1.lead.object_id


def test_deterministic_lead_assignment() -> None:
    capability = LeadIntakeCapability()
    p1 = {"customer_name": "Lead 1", "phone_number": "0911000001", "lead_source": "Web", "product_interest": "Plan A"}
    p2 = {"customer_name": "Lead 2", "phone_number": "0911000002", "lead_source": "Web", "product_interest": "Plan B"}

    res1 = capability.process_lead_intake(p1)
    res2 = capability.process_lead_intake(p2)

    assert res1.status == "SUCCESS"
    assert res2.status == "SUCCESS"

    # Verify assigned to different users under round-robin
    assigned_user1 = res1.assignment.assigned_to_user_id
    assigned_user2 = res2.assignment.assigned_to_user_id
    assert assigned_user1 != assigned_user2


def test_unverified_knowledge_fallback() -> None:
    plugin = SalesOSPlugin()
    payload = {
        "customer_name": "Test Fallback",
        "phone_number": "0912345678",
        "lead_source": "Web",
        "product_interest": "SaaS",
        "force_unverified_knowledge": True
    }
    result = plugin.process_lead(payload)
    assert result.status == "INSUFFICIENT_VERIFIED_KNOWLEDGE"
    assert result.error_code == "INSUFFICIENT_VERIFIED_KNOWLEDGE"


def test_plugin_manifest_validation_and_metadata() -> None:
    plugin = SalesOSPlugin()
    health = plugin.health_check()

    assert health["plugin_id"] == "com.nhanthuat.salesos"
    assert health["version"] == "1.0.0"
    assert health["status"] == "HEALTHY"

    manifest_path = Path(__file__).resolve().parent.parent / "plugin.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["plugin_id"] == "com.nhanthuat.salesos"
    assert manifest["version"] == "1.0.0"
    assert "provenance" in manifest
    assert manifest["provenance"]["governance_status"] == "frozen"


def test_persona_authority_limits() -> None:
    persona = SalesOpsCoordinatorPersona()
    spec = persona.get_persona_spec()
    assert spec["persona_id"] == "SALESOS-PERSONA-001"
    assert spec["authority_level"] == 2
    assert spec["temperament_vector"]["analytical_vs_intuitive"] == 0.70
