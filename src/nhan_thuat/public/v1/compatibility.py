"""
Compatibility metadata for NhanThuat Contract V1.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ContractVersion:
    major: int
    minor: int
    patch: int
    identifier: str

    def __str__(self) -> str:
        return f"{self.identifier} v{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True)
class CompatibilityMetadata:
    contract_version: ContractVersion
    supported_businessos_versions: list[str]
    is_deprecated: bool = False
