"""Naming convention checks for source records."""

from __future__ import annotations

import re
from pathlib import Path

from .identifiers import parse_identifier, prefix_for_unit_type

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def is_kebab_slug(value: str) -> bool:
    return bool(SLUG_PATTERN.fullmatch(value))


def validate_tag_name(value: str) -> str | None:
    if not is_kebab_slug(value):
        return f"tag must be lowercase kebab-case: {value}"
    return None


def validate_unit_identifier_matches_type(unit_id: str, unit_type: str) -> str | None:
    try:
        identifier = parse_identifier(unit_id)
        expected = prefix_for_unit_type(unit_type)
    except ValueError as exc:
        return str(exc)
    if identifier.prefix != expected:
        return f"id prefix {identifier.prefix} does not match type {unit_type} ({expected})"
    return None


def validate_filename_contains_id(path: Path, record_id: str) -> str | None:
    if record_id not in path.stem:
        return f"filename must contain record id {record_id}"
    return None
