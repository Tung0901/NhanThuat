"""Application service for operational case files."""

from __future__ import annotations

import uuid
from dataclasses import replace
from typing import Any

from nhan_thuat.casework.models import CaseArtifact, CaseFile, utcnow_iso
from nhan_thuat.casework.repository import CaseFileRepository


class CaseFileService:
    def __init__(self, repository: CaseFileRepository) -> None:
        self.repository = repository

    def create(
        self,
        *,
        title: str,
        situation_statement: str,
        objective: str,
        owner_user_id: str,
        org_id: str,
        **fields: Any,
    ) -> CaseFile:
        now = utcnow_iso()
        case = CaseFile(
            schema_version="case-file.v1", case_id=self.repository.new_id(), revision=1,
            title=title, situation_statement=situation_statement, objective=objective,
            status="open", owner_user_id=owner_user_id, org_id=org_id,
            created_at=now, updated_at=now, **fields,
        )
        return self.repository.create(case)

    def revise(self, case: CaseFile, expected_revision: int, **changes: Any) -> CaseFile | None:
        revised = replace(case, **changes, updated_at=utcnow_iso())
        return self.repository.update(revised, expected_revision)

    def add_artifact(self, case: CaseFile, **fields: Any) -> CaseArtifact:
        artifact = CaseArtifact(
            artifact_id=f"ART-{uuid.uuid4().hex[:12].upper()}",
            case_id=case.case_id, case_revision=case.revision, **fields,
        )
        return self.repository.add_artifact(artifact)
