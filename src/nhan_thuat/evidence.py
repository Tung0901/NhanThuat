"""Evidence records and traceability helpers."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CONFIDENCE_LEVELS = ("hypothesis", "provisional", "supported", "strong", "contested")
SOURCE_KINDS = (
    "book",
    "article",
    "paper",
    "report",
    "web_page",
    "case_note",
    "interview",
    "dataset",
    "internal_document",
    "observation",
    "derived_analysis",
)
EVIDENCE_LINK_TYPES = ("supports", "contests", "contextualizes")


@dataclass(frozen=True)
class EvidenceSource:
    kind: str
    title: str
    authors: tuple[str, ...] = ()
    publisher: str | None = None
    published_at: str | None = None
    accessed_at: str | None = None
    language: str | None = None
    url: str | None = None
    path: str | None = None
    license: str | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> EvidenceSource:
        return cls(
            kind=str(data["kind"]),
            title=str(data["title"]),
            authors=tuple(str(author) for author in data.get("authors", [])),
            publisher=_optional_string(data.get("publisher")),
            published_at=_optional_string(data.get("published_at")),
            accessed_at=_optional_string(data.get("accessed_at")),
            language=_optional_string(data.get("language")),
            url=_optional_string(data.get("url")),
            path=_optional_string(data.get("path")),
            license=_optional_string(data.get("license")),
        )


@dataclass(frozen=True)
class Citation:
    id: str
    source_locator: str
    locator_type: str
    locator: str
    paraphrase: str
    quote: str | None = None
    accessed_at: str | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> Citation:
        return cls(
            id=str(data["id"]),
            source_locator=str(data["source_locator"]),
            locator_type=str(data["locator_type"]),
            locator=str(data["locator"]),
            paraphrase=str(data["paraphrase"]),
            quote=_optional_string(data.get("quote")),
            accessed_at=_optional_string(data.get("accessed_at")),
        )


@dataclass(frozen=True)
class EvidenceClaim:
    id: str
    summary: str
    citations: tuple[str, ...]

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> EvidenceClaim:
        return cls(
            id=str(data["id"]),
            summary=str(data["summary"]),
            citations=tuple(str(citation) for citation in data.get("citations", [])),
        )


@dataclass(frozen=True)
class Confidence:
    level: str
    basis: str
    factors: tuple[str, ...] = ()
    reviewed_by: str | None = None
    reviewed_at: str | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> Confidence:
        return cls(
            level=str(data["level"]),
            basis=str(data["basis"]),
            factors=tuple(str(factor) for factor in data.get("factors", [])),
            reviewed_by=_optional_string(data.get("reviewed_by")),
            reviewed_at=_optional_string(data.get("reviewed_at")),
        )


@dataclass(frozen=True)
class EvidenceRecord:
    id: str
    type: str
    status: str
    version: str
    title: str
    summary: str
    source: EvidenceSource
    citations: tuple[Citation, ...]
    claims: tuple[EvidenceClaim, ...]
    confidence: Confidence
    supports: tuple[str, ...] = ()
    contests: tuple[str, ...] = ()
    contextualizes: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    created_at: str | None = None
    updated_at: str | None = None
    source_path: Path | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_mapping(cls, data: dict[str, Any], source_path: Path | None = None) -> EvidenceRecord:
        return cls(
            id=str(data["id"]),
            type=str(data["type"]),
            status=str(data["status"]),
            version=str(data["version"]),
            title=str(data["title"]),
            summary=str(data["summary"]),
            source=EvidenceSource.from_mapping(data["source"]),
            citations=tuple(Citation.from_mapping(item) for item in data.get("citations", [])),
            claims=tuple(EvidenceClaim.from_mapping(item) for item in data.get("claims", [])),
            confidence=Confidence.from_mapping(data["confidence"]),
            supports=tuple(str(unit_id) for unit_id in data.get("supports", [])),
            contests=tuple(str(unit_id) for unit_id in data.get("contests", [])),
            contextualizes=tuple(str(unit_id) for unit_id in data.get("contextualizes", [])),
            limitations=tuple(str(item) for item in data.get("limitations", [])),
            tags=tuple(str(tag) for tag in data.get("tags", [])),
            created_at=_optional_string(data.get("created_at")),
            updated_at=_optional_string(data.get("updated_at")),
            source_path=source_path,
            raw=dict(data),
        )

    def iter_target_ids(self) -> tuple[str, ...]:
        return self.supports + self.contests + self.contextualizes

    def to_mapping(self) -> dict[str, Any]:
        return dict(self.raw)


@dataclass(frozen=True)
class EvidenceTraceability:
    by_unit: dict[str, dict[str, list[str]]]
    by_evidence: dict[str, dict[str, list[str]]]


def build_traceability(evidence_records: Iterable[EvidenceRecord]) -> EvidenceTraceability:
    by_unit: dict[str, dict[str, list[str]]] = {}
    by_evidence: dict[str, dict[str, list[str]]] = {}
    for evidence in sorted(evidence_records, key=lambda record: record.id):
        links = {
            "supports": list(evidence.supports),
            "contests": list(evidence.contests),
            "contextualizes": list(evidence.contextualizes),
        }
        by_evidence[evidence.id] = links
        for link_type, unit_ids in links.items():
            for unit_id in unit_ids:
                by_unit.setdefault(
                    unit_id,
                    {"supports": [], "contests": [], "contextualizes": []},
                )[link_type].append(evidence.id)
    return EvidenceTraceability(by_unit=by_unit, by_evidence=by_evidence)


def _optional_string(value: Any) -> str | None:
    return None if value is None else str(value)
