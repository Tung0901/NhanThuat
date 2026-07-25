"""
Public serializers for NhanThuat Contract V1.
"""
from dataclasses import is_dataclass, asdict
from typing import Any, Dict


def serialize_contract(obj: Any) -> Dict[str, Any]:
    """Serialize a public contract dataclass to a dictionary."""
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, dict):
        return {k: serialize_contract(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize_contract(v) for v in obj]
    return obj
