"""Revalidation trigger utilities."""

from __future__ import annotations

from datetime import date, timedelta

from src.model_risk.models import FindingSeverity, ModelRecord, RevalidationTrigger


def scheduled_revalidation_due(record: ModelRecord, as_of: date | None = None) -> bool:
    as_of = as_of or date(2026, 7, 27)
    return record.next_validation_date <= as_of


def trigger_for_overdue_validation(record: ModelRecord, as_of: date | None = None) -> RevalidationTrigger | None:
    as_of = as_of or date(2026, 7, 27)
    if not scheduled_revalidation_due(record, as_of):
        return None
    return RevalidationTrigger(
        trigger_id=f"REV-{record.model_id}-SCHEDULE",
        model_id=record.model_id,
        trigger="Scheduled validation date reached",
        trigger_date=as_of,
        evidence=f"Next validation date was {record.next_validation_date.isoformat()}.",
        severity=FindingSeverity.HIGH,
        required_action="Start independent revalidation.",
        due_date=as_of + timedelta(days=30),
    )
