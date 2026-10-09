"""SQLite repository for live case files and their derived artifacts."""

from __future__ import annotations

import json
import uuid
from typing import Any

from nhan_thuat.casework.models import CaseArtifact, CaseFile, claim_from_dict
from nhan_thuat.storage.db import DatabaseManager


class CaseFileRepository:
    """Persistence boundary that keeps ownership and revision data explicit."""

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def create(self, case: CaseFile) -> CaseFile:
        with self.db.connection() as conn:
            conn.execute(
                """INSERT INTO case_files
                (case_id, schema_version, revision, title, situation_statement, objective,
                 status, owner_user_id, org_id, sensitivity, domain_tags, stakeholders,
                 known_facts, assumptions, unknowns, constraints, risk_if_wrong,
                 observation_signals, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                self._case_params(case),
            )
        return case

    def get(self, case_id: str, owner_user_id: str | None = None) -> CaseFile | None:
        with self.db.connection() as conn:
            query = "SELECT * FROM case_files WHERE case_id = ?"
            params: list[Any] = [case_id]
            if owner_user_id is not None:
                query += " AND owner_user_id = ?"
                params.append(owner_user_id)
            row = conn.execute(query, params).fetchone()
        return self._case_from_row(dict(row)) if row else None

    def list(self, owner_user_id: str, org_id: str, limit: int = 50) -> list[CaseFile]:
        with self.db.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM case_files WHERE owner_user_id = ? AND org_id = "
                "? ORDER BY updated_at DESC LIMIT ?",
                (owner_user_id, org_id, limit),
            ).fetchall()
        return [self._case_from_row(dict(row)) for row in rows]

    def update(self, case: CaseFile, expected_revision: int) -> CaseFile | None:
        next_revision = expected_revision + 1
        case.revision = next_revision
        with self.db.connection() as conn:
            cursor = conn.execute(
                """UPDATE case_files SET revision = ?, title = ?, situation_statement = ?,
                objective = ?, status = ?, sensitivity = ?, domain_tags = ?, stakeholders = ?,
                known_facts = ?, assumptions = ?, unknowns = ?, constraints = ?,
                risk_if_wrong = ?, observation_signals = ?, updated_at = ?
                WHERE case_id = ? AND owner_user_id = ? AND revision = ?""",
                (
                    case.revision, case.title, case.situation_statement, case.objective,
                    case.status, case.sensitivity, json.dumps(case.domain_tags, ensure_ascii=False),
                    json.dumps(case.stakeholders, ensure_ascii=False),
                    json.dumps([claim.to_dict() for claim in case.known_facts], ensure_ascii=False),
                    json.dumps([claim.to_dict() for claim in case.assumptions], ensure_ascii=False),
                    json.dumps(case.unknowns, ensure_ascii=False),
                    json.dumps(case.constraints, ensure_ascii=False), case.risk_if_wrong,
                    json.dumps(case.observation_signals, ensure_ascii=False), case.updated_at,
                    case.case_id, case.owner_user_id, expected_revision,
                ),
            )
            if cursor.rowcount != 1:
                return None
            conn.execute(
                "UPDATE case_artifacts SET stale = 1 WHERE case_id = ? AND case_revision < ?",
                (case.case_id, case.revision),
            )
        return case

    def add_artifact(self, artifact: CaseArtifact) -> CaseArtifact:
        with self.db.connection() as conn:
            conn.execute(
                """INSERT INTO case_artifacts
                (artifact_id, case_id, case_revision, artifact_type, source_module,
                 module_version, payload_schema_version, input_hash, summary, payload,
                 knowledge_refs, provenance, confidence, limitations, created_by, created_at, stale)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    artifact.artifact_id, artifact.case_id, artifact.case_revision,
                    artifact.artifact_type, artifact.source_module, artifact.module_version,
                    artifact.payload_schema_version, artifact.input_hash, artifact.summary,
                    json.dumps(artifact.payload, ensure_ascii=False),
                    json.dumps(artifact.knowledge_refs, ensure_ascii=False),
                    json.dumps(artifact.provenance, ensure_ascii=False), artifact.confidence,
                    json.dumps(artifact.limitations, ensure_ascii=False), artifact.created_by,
                    artifact.created_at, int(artifact.stale),
                ),
            )
        return artifact

    def list_artifacts(self, case_id: str, include_stale: bool = False) -> list[CaseArtifact]:
        query = "SELECT * FROM case_artifacts WHERE case_id = ?"
        params: tuple[Any, ...] = (case_id,)
        if not include_stale:
            query += " AND stale = 0"
        query += " ORDER BY created_at ASC"
        with self.db.connection() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._artifact_from_row(dict(row)) for row in rows]

    @staticmethod
    def _case_params(case: CaseFile) -> tuple[Any, ...]:
        return (
            case.case_id, case.schema_version, case.revision, case.title,
            case.situation_statement, case.objective, case.status, case.owner_user_id,
            case.org_id, case.sensitivity, json.dumps(case.domain_tags, ensure_ascii=False),
            json.dumps(case.stakeholders, ensure_ascii=False),
            json.dumps([claim.to_dict() for claim in case.known_facts], ensure_ascii=False),
            json.dumps([claim.to_dict() for claim in case.assumptions], ensure_ascii=False),
            json.dumps(case.unknowns, ensure_ascii=False), json.dumps(case.constraints, ensure_ascii=False),
            case.risk_if_wrong, json.dumps(case.observation_signals, ensure_ascii=False),
            case.created_at, case.updated_at,
        )

    @staticmethod
    def _case_from_row(row: dict[str, Any]) -> CaseFile:
        decode = lambda key, default: json.loads(row[key]) if row.get(key) else default
        return CaseFile(
            schema_version=str(row["schema_version"]), case_id=str(row["case_id"]),
            revision=int(row["revision"]), title=str(row["title"]),
            situation_statement=str(row["situation_statement"]), objective=str(row["objective"]),
            status=str(row["status"]), owner_user_id=str(row["owner_user_id"]),
            org_id=str(row["org_id"]), sensitivity=str(row["sensitivity"]),
            domain_tags=decode("domain_tags", []), stakeholders=decode("stakeholders", []),
            known_facts=[claim_from_dict(item) for item in decode("known_facts", [])],
            assumptions=[claim_from_dict(item) for item in decode("assumptions", [])],
            unknowns=decode("unknowns", []), constraints=decode("constraints", []),
            risk_if_wrong=str(row["risk_if_wrong"]), observation_signals=decode("observation_signals", []),
            created_at=str(row["created_at"]), updated_at=str(row["updated_at"]),
        )

    @staticmethod
    def _artifact_from_row(row: dict[str, Any]) -> CaseArtifact:
        decode = lambda key, default: json.loads(row[key]) if row.get(key) else default
        return CaseArtifact(
            artifact_id=str(row["artifact_id"]), case_id=str(row["case_id"]),
            case_revision=int(row["case_revision"]), artifact_type=str(row["artifact_type"]),
            source_module=str(row["source_module"]), module_version=str(row["module_version"]),
            payload_schema_version=str(row["payload_schema_version"]), input_hash=str(row["input_hash"]),
            summary=str(row["summary"]), payload=decode("payload", {}),
            knowledge_refs=decode("knowledge_refs", []), provenance=decode("provenance", {}),
            confidence=row["confidence"], limitations=decode("limitations", []),
            created_by=str(row["created_by"]), created_at=str(row["created_at"]),
            stale=bool(row["stale"]),
        )

    @staticmethod
    def new_id() -> str:
        return f"CF-{uuid.uuid4().hex[:12].upper()}"
