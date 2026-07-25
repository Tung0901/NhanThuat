"""
SALESOS-SKILL-002 — Normalize Contact Data.
Normalizes customer name, lead source, product interest, and invokes Vietnamese phone normalizer tool.
"""

from typing import Any, Dict, Tuple
from salesos_pack.tools.phone_normalizer import normalize_vietnamese_phone


def normalize_contact_data_skill(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
    """
    Normalize contact data.
    
    Returns (success: bool, normalized_payload: Dict, error_message: str).
    """
    raw_phone = str(payload.get("phone_number", "")).strip()
    is_valid, local_phone, e164_phone, err = normalize_vietnamese_phone(raw_phone)
    if not is_valid:
        return False, {}, err

    customer_name = str(payload.get("customer_name", "")).strip().title()
    lead_source = str(payload.get("lead_source", "")).strip().lower()
    product_interest = str(payload.get("product_interest", "")).strip()
    notes = str(payload.get("notes", "")).strip() if payload.get("notes") else ""

    normalized_payload = {
        "customer_name": customer_name,
        "raw_phone": raw_phone,
        "normalized_phone": local_phone,
        "e164_phone": e164_phone,
        "lead_source": lead_source,
        "product_interest": product_interest,
        "notes": notes,
    }

    return True, normalized_payload, ""
