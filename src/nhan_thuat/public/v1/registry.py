"""
Public Contract Registry for NhanThuat Contract V1.
"""
from typing import Dict, Type, Optional


class ContractRegistry:
    """Registry to map capability IDs to their respective input/output contracts."""
    
    def __init__(self):
        self._contracts: Dict[str, Dict[str, Type]] = {}

    def register_capability(self, capability_id: str, input_contract: Type, output_contract: Type) -> None:
        self._contracts[capability_id] = {
            "input": input_contract,
            "output": output_contract
        }

    def get_input_contract(self, capability_id: str) -> Optional[Type]:
        cap = self._contracts.get(capability_id)
        if cap:
            return cap["input"]
        return None

    def get_output_contract(self, capability_id: str) -> Optional[Type]:
        cap = self._contracts.get(capability_id)
        if cap:
            return cap["output"]
        return None


# Global immutable registry for V1
registry = ContractRegistry()
