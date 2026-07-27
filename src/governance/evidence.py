"""Lightweight evidence records for issue closure and assurance."""

from __future__ import annotations

from datetime import date

from src.governance.models import EvidenceRecord, EvidenceType, GovernanceError


def create_evidence(
    evidence_id: str,
    issue_id: str,
    evidence_type: EvidenceType,
    description: str,
    created_by: str,
    reference: str,
    created_date: date | None = None,
) -> EvidenceRecord:
    if not issue_id or not created_by or not reference:
        raise GovernanceError("Evidence requires issue ID, creator and reference.")
    return EvidenceRecord(
        evidence_id=evidence_id,
        issue_id=issue_id,
        evidence_type=evidence_type,
        description=description,
        created_date=created_date or date(2026, 7, 27),
        created_by=created_by,
        reference=reference,
        validation_status="Submitted",
    )


def evidence_to_frame(records: list[EvidenceRecord]):
    import pandas as pd

    return pd.DataFrame([record.__dict__ for record in records])
