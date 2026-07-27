"""Compatibility wrappers for model-risk tables."""

from __future__ import annotations

import pandas as pd

from src.model_risk.inventory import inventory_to_frame
from src.model_risk.validation import findings_frame


def model_inventory() -> pd.DataFrame:
    table = inventory_to_frame()
    return table.rename(
        columns={
            "model": "model",
            "version": "version",
            "owner": "owner",
            "status": "validation_status",
            "approval": "approval_status",
            "limitations": "known_limitations",
        }
    )[["model", "version", "owner", "validation_status", "approval_status", "monitoring_frequency", "known_limitations"]].rename(columns={"monitoring_frequency": "monitoring_metrics"})


def validation_findings() -> pd.DataFrame:
    table = findings_frame()
    return table[["finding_id", "severity", "title", "status"]].rename(columns={"title": "finding"})
