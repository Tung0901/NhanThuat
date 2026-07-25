"""
SALESOS-SKILL-001 — Validate Lead Input.
Validates mandatory lead intake fields: customer_name, phone_number, lead_source, product_interest.
"""

from typing import Any, Dict, List, Tuple


def validate_lead_input_skill(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate raw lead intake input payload.
    
    Required fields: customer_name, phone_number, lead_source, product_interest.
    Returns (is_valid: bool, errors: List[str]).
    """
    errors = []
    
    customer_name = payload.get("customer_name")
    if not customer_name or not isinstance(customer_name, str) or not customer_name.strip():
        errors.append("customer_name is required and must be a non-empty string.")
        
    phone_number = payload.get("phone_number")
    if not phone_number or not isinstance(phone_number, str) or not phone_number.strip():
        errors.append("phone_number is required and must be a non-empty string.")
        
    lead_source = payload.get("lead_source")
    if not lead_source or not isinstance(lead_source, str) or not lead_source.strip():
        errors.append("lead_source is required and must be a non-empty string.")

    product_interest = payload.get("product_interest")
    if not product_interest or not isinstance(product_interest, str) or not product_interest.strip():
        errors.append("product_interest is required and must be a non-empty string.")

    return len(errors) == 0, errors
