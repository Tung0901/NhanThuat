"""
Data models for persistent storage layer in NhanThuat (Sparring Sessions, Messages, Case Studies).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SparringSession:
    id: str
    title: str
    philosophy_lens: str = "auto"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "active"  # 'active', 'completed', 'archived'
    summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: dict[str, Any] | tuple[Any, ...]) -> SparringSession:
        if isinstance(row, dict):
            meta = row.get("metadata", {})
            if isinstance(meta, str):
                try:
                    meta = json.loads(meta)
                except Exception:
                    meta = {}
            return cls(
                id=str(row["id"]),
                title=str(row["title"]),
                philosophy_lens=str(row.get("philosophy_lens", "auto")),
                created_at=str(row.get("created_at", "")),
                status=str(row.get("status", "active")),
                summary=str(row.get("summary", "")),
                metadata=meta,
            )
        # Tuple format: (id, title, philosophy_lens, created_at, status, summary, metadata)
        meta = {}
        if len(row) > 6 and row[6]:
            try:
                meta = json.loads(row[6])
            except Exception:
                meta = {}
        return cls(
            id=str(row[0]),
            title=str(row[1]),
            philosophy_lens=str(row[2]) if len(row) > 2 else "auto",
            created_at=str(row[3]) if len(row) > 3 else "",
            status=str(row[4]) if len(row) > 4 else "active",
            summary=str(row[5]) if len(row) > 5 else "",
            metadata=meta,
        )


@dataclass
class SparringMessage:
    id: str
    session_id: str
    role: str  # 'user' or 'assistant' or 'system'
    content: str
    matched_unit_ids: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: dict[str, Any] | tuple[Any, ...]) -> SparringMessage:
        if isinstance(row, dict):
            units = row.get("matched_unit_ids", [])
            if isinstance(units, str):
                try:
                    units = json.loads(units)
                except Exception:
                    units = []
            meta = row.get("metadata", {})
            if isinstance(meta, str):
                try:
                    meta = json.loads(meta)
                except Exception:
                    meta = {}
            return cls(
                id=str(row["id"]),
                session_id=str(row["session_id"]),
                role=str(row["role"]),
                content=str(row["content"]),
                matched_unit_ids=units,
                created_at=str(row.get("created_at", "")),
                metadata=meta,
            )
        # Tuple format: (id, session_id, role, content, matched_unit_ids, created_at, metadata)
        units = []
        if len(row) > 4 and row[4]:
            try:
                units = json.loads(row[4])
            except Exception:
                units = []
        meta = {}
        if len(row) > 6 and row[6]:
            try:
                meta = json.loads(row[6])
            except Exception:
                meta = {}
        return cls(
            id=str(row[0]),
            session_id=str(row[1]),
            role=str(row[2]),
            content=str(row[3]),
            matched_unit_ids=units,
            created_at=str(row[5]) if len(row) > 5 else "",
            metadata=meta,
        )


@dataclass
class CaseStudy:
    id: str
    domain: str  # 'HR', 'OPS', 'SALES', 'LEADERSHIP', 'FINANCE'
    title: str
    context_description: str
    decision_script: dict[str, Any] = field(default_factory=dict)
    lessons_learned: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: dict[str, Any] | tuple[Any, ...]) -> CaseStudy:
        if isinstance(row, dict):
            script = row.get("decision_script", {})
            if isinstance(script, str):
                try:
                    script = json.loads(script)
                except Exception:
                    script = {}
            lessons = row.get("lessons_learned", [])
            if isinstance(lessons, str):
                try:
                    lessons = json.loads(lessons)
                except Exception:
                    lessons = []
            tags = row.get("tags", [])
            if isinstance(tags, str):
                try:
                    tags = json.loads(tags)
                except Exception:
                    tags = []
            return cls(
                id=str(row["id"]),
                domain=str(row.get("domain", "GENERAL")),
                title=str(row["title"]),
                context_description=str(row.get("context_description", "")),
                decision_script=script,
                lessons_learned=lessons,
                created_at=str(row.get("created_at", "")),
                tags=tags,
            )
        # Tuple format: (id, domain, title, context_description, decision_script, lessons_learned, created_at, tags)
        script = {}
        if len(row) > 4 and row[4]:
            try:
                script = json.loads(row[4])
            except Exception:
                script = {}
        lessons = []
        if len(row) > 5 and row[5]:
            try:
                lessons = json.loads(row[5])
            except Exception:
                lessons = []
        tags = []
        if len(row) > 7 and row[7]:
            try:
                tags = json.loads(row[7])
            except Exception:
                tags = []
        return cls(
            id=str(row[0]),
            domain=str(row[1]) if len(row) > 1 else "GENERAL",
            title=str(row[2]) if len(row) > 2 else "",
            context_description=str(row[3]) if len(row) > 3 else "",
            decision_script=script,
            lessons_learned=lessons,
            created_at=str(row[6]) if len(row) > 6 else "",
            tags=tags,
        )
