"""
Vietnamese Phone Number Normalizer Tool for SalesOS.
Normalizes Vietnamese mobile phone numbers into local canonical (09xxxxxxxx)
and international E.164 (+849xxxxxxxx) formats.
"""

import re
from typing import Tuple


def normalize_vietnamese_phone(raw_phone: str) -> Tuple[bool, str, str, str]:
    """
    Normalize Vietnamese phone number.
    
    Returns:
        Tuple[is_valid, local_canonical, e164_canonical, error_message]
        e.g. (True, "0912345678", "+84912345678", "")
    """
    if not raw_phone or not isinstance(raw_phone, str):
        return False, "", "", "Phone number string is required."

    # Remove all whitespace, dots, dashes, parentheses
    cleaned = re.sub(r"[\s\.\-\(\)]", "", raw_phone.strip())

    # Handle leading +84 or 84
    if cleaned.startswith("+84"):
        digits = "0" + cleaned[3:]
    elif cleaned.startswith("84") and len(cleaned) == 11:
        digits = "0" + cleaned[2:]
    else:
        digits = cleaned

    # Check basic 10-digit mobile rule for Vietnam
    if not digits.isdigit():
        return False, "", "", f"Phone number '{raw_phone}' contains invalid non-numeric characters."

    if len(digits) != 10 or not digits.startswith("0"):
        return False, "", "", f"Vietnamese phone number '{raw_phone}' must be 10 digits starting with 0."

    # Validate mobile prefixes: 03, 05, 07, 08, 09
    prefix = digits[:2]
    if prefix not in {"03", "05", "07", "08", "09"}:
        return False, "", "", f"Invalid Vietnamese mobile prefix '{prefix}'."

    local_canonical = digits
    e164_canonical = "+84" + digits[1:]

    return True, local_canonical, e164_canonical, ""
