"""Model inventory utilities."""

from __future__ import annotations

import pandas as pd

from src.data.synthetic_model_risk import synthetic_model_inventory
from src.model_risk.models import ModelRecord, ModelRiskError


def validate_inventory(records: list[ModelRecord]) -> None:
    keys = [(record.model_id, record.model_version) for record in records]
    if len(keys) != len(set(keys)):
        raise ModelRiskError("Model ID and version combinations must be unique.")
    for record in records:
        if not record.owner or not record.validator:
            raise ModelRiskError("Every model requires owner and validator.")
        if record.developer == record.validator:
            raise ModelRiskError("Independent validator cannot be the same as developer.")


def get_inventory() -> list[ModelRecord]:
    records = synthetic_model_inventory()
    validate_inventory(records)
    return records


def inventory_to_frame(records: list[ModelRecord] | None = None) -> pd.DataFrame:
    rows = []
    for record in records or get_inventory():
        rows.append(
            {
                "model_id": record.model_id,
                "model": record.model_name,
                "version": record.model_version,
                "family": record.model_family.value,
                "type": record.model_type,
                "tier": record.model_tier.value,
                "owner": record.owner,
                "status": record.lifecycle_status.value,
                "approval": record.approval_status.value,
                "last_validation": record.last_validation_date.isoformat(),
                "next_validation": record.next_validation_date.isoformat(),
                "monitoring_frequency": record.monitoring_frequency,
                "open_findings": len(record.open_issues),
                "limitations": "; ".join(record.limitations),
                "use_restrictions": "; ".join(record.use_restrictions),
                "affected_reports": ", ".join(record.affected_reports),
            }
        )
    return pd.DataFrame(rows)


def model_by_id(model_id: str, records: list[ModelRecord] | None = None) -> ModelRecord:
    for record in records or get_inventory():
        if record.model_id == model_id:
            return record
    raise ModelRiskError(f"Unknown model ID: {model_id}")
