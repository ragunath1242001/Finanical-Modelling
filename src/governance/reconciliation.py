"""Risk-versus-Finance reconciliation engine."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.governance.models import GovernanceError


@dataclass(frozen=True)
class ReconciliationConfig:
    keys: tuple[str, ...] = ("customer_id", "account_id", "facility_id", "reporting_date")
    value_fields: tuple[str, ...] = ("exposure", "provision")
    tolerance: float = 1_000.0
    materiality_threshold: float = 5_000.0
    critical_threshold: float = 20_000.0


@dataclass(frozen=True)
class ReconciliationSummary:
    matched_records: int
    unmatched_risk_records: int
    unmatched_finance_records: int
    total_difference: float
    material_differences: int
    status: str
    explanation_required: bool


@dataclass(frozen=True)
class ReconciliationResult:
    details: pd.DataFrame
    unmatched_risk: pd.DataFrame
    unmatched_finance: pd.DataFrame
    summary: ReconciliationSummary


def classify_difference(abs_difference: float, config: ReconciliationConfig) -> str:
    if abs_difference <= config.tolerance:
        return "Immaterial"
    if abs_difference < config.materiality_threshold:
        return "Moderate"
    if abs_difference < config.critical_threshold:
        return "Material"
    return "Critical"


def reconcile_risk_finance(risk: pd.DataFrame, finance: pd.DataFrame, config: ReconciliationConfig | None = None) -> ReconciliationResult:
    config = config or ReconciliationConfig()
    missing_risk = set(config.keys + config.value_fields) - set(risk.columns)
    missing_finance = set(config.keys + config.value_fields) - set(finance.columns)
    if missing_risk or missing_finance:
        raise GovernanceError(f"Reconciliation missing columns. Risk: {missing_risk}; Finance: {missing_finance}.")
    merged = risk.merge(finance, on=list(config.keys), how="outer", suffixes=("_risk", "_finance"), indicator=True)
    matched = merged[merged["_merge"].eq("both")].copy()
    unmatched_risk = merged[merged["_merge"].eq("left_only")].copy()
    unmatched_finance = merged[merged["_merge"].eq("right_only")].copy()
    rows = []
    for row in matched.itertuples(index=False):
        base = {key: getattr(row, key) for key in config.keys}
        for field in config.value_fields:
            risk_value = float(getattr(row, f"{field}_risk"))
            finance_value = float(getattr(row, f"{field}_finance"))
            difference = risk_value - finance_value
            rows.append(
                {
                    **base,
                    "field": field,
                    "risk_value": risk_value,
                    "finance_value": finance_value,
                    "difference": difference,
                    "percentage_difference": difference / finance_value if finance_value else 0.0,
                    "materiality": classify_difference(abs(difference), config),
                    "reconciliation_status": "Matched" if abs(difference) <= config.tolerance else "Open",
                    "explanation_required": abs(difference) > config.tolerance,
                }
            )
    details = pd.DataFrame(rows)
    total_difference = float(details["difference"].sum()) if not details.empty else 0.0
    material_count = int(details["materiality"].isin(["Material", "Critical"]).sum()) if not details.empty else 0
    status = "Ready" if material_count == 0 and unmatched_risk.empty and unmatched_finance.empty else "Ready with limitations"
    if material_count or len(unmatched_risk) or len(unmatched_finance):
        status = "Under review"
    summary = ReconciliationSummary(
        matched_records=len(matched),
        unmatched_risk_records=len(unmatched_risk),
        unmatched_finance_records=len(unmatched_finance),
        total_difference=total_difference,
        material_differences=material_count,
        status=status,
        explanation_required=bool(material_count or len(unmatched_risk) or len(unmatched_finance)),
    )
    return ReconciliationResult(details, unmatched_risk, unmatched_finance, summary)


def reconcile_exposure(risk_exposure: float, finance_exposure: float, owner: str = "Finance/Risk Data Steward") -> pd.DataFrame:
    difference = finance_exposure - risk_exposure
    return pd.DataFrame(
        [
            {
                "risk_exposure": risk_exposure,
                "finance_exposure": finance_exposure,
                "difference": difference,
                "adjustment_reason": "Timing, write-off, or source-system mapping difference" if difference else "No adjustment",
                "owner": owner,
                "status": "Open" if abs(difference) > 1 else "Matched",
            }
        ]
    )
