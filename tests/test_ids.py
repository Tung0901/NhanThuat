from pathlib import Path

from nhan_thuat.registry import build_registry

ROOT = Path(__file__).resolve().parents[1]


def test_registry_ids_are_unique() -> None:
    registry = build_registry(ROOT)
    assert len(registry) == len(set(registry))

