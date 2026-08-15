"""Identifier parsing and generation utilities."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

ID_PATTERN = re.compile(
    r"^(?:NT-(?P<prefix>[A-Z]+(?:-[A-Z]+)*|EPIC)-(?P<number>[0-9]{2,4})|"
    r"NT-(?P<compact_prefix>D)(?P<compact_number>[0-9]{2}))$"
)
UNIT_TYPE_PREFIXES = {
    "law": "LAW",
    "principle": "PRINCIPLE",
    "model": "MODEL",
    "strategy": "STRATEGY",
    "tool": "TOOL",
    "case": "CASE",
    "evidence": "EVIDENCE",
    "anti-pattern": "ANTI-PATTERN",
    "phenomenon": "PHENOMENON",
}


@dataclass(frozen=True)
class Identifier:
    value: str
    prefix: str
    number: int
    width: int


def parse_identifier(value: str) -> Identifier:
    match = ID_PATTERN.match(value)
    if match is None:
        raise ValueError(f"Invalid identifier: {value}")
    prefix = match.group("prefix") or match.group("compact_prefix")
    raw_number = match.group("number") or match.group("compact_number")
    if prefix is None or raw_number is None:
        raise ValueError(f"Invalid identifier: {value}")
    return Identifier(
        value=value,
        prefix=prefix,
        number=int(raw_number),
        width=len(raw_number),
    )


def prefix_for_unit_type(unit_type: str) -> str:
    try:
        return UNIT_TYPE_PREFIXES[unit_type]
    except KeyError as exc:
        raise ValueError(f"Unknown knowledge unit type: {unit_type}") from exc


def generate_identifier(prefix: str, number: int, width: int = 4) -> str:
    if number < 0:
        raise ValueError("Identifier number must be non-negative")
    return f"NT-{prefix}-{number:0{width}d}"


def next_identifier(existing_ids: Iterable[str], prefix: str, width: int = 4) -> str:
    numbers = []
    for value in existing_ids:
        try:
            identifier = parse_identifier(value)
        except ValueError:
            continue
        if identifier.prefix == prefix:
            numbers.append(identifier.number)
    return generate_identifier(prefix, max(numbers, default=0) + 1, width=width)
