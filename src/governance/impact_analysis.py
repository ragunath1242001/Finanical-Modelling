"""Downstream impact analysis for data-quality failures."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.risk.capital_bridge import CapitalBridgeInput, capital_movement_bridge
from src.risk.expected_loss import point_in_time_expected_loss


@dataclass(frozen=True)
class DownstreamImpact:
    affected_data_elements: list[str]
    affected_models: list[str]
    affected_reports: list[str]
    likely_directional_impact: str
    estimated_materiality: float
    limitations: str


IMPACT_MAP = {
    "DQ-001": DownstreamImpact(["income"], ["PD model", "IFRS 9 ECL", "IRB", "stress testing"], ["FINREP provisions", "COREP capital"], "Missing income creates PD uncertainty and may understate or overstate ECL depending on imputation.", 0.0, "True borrower affordability cannot be known from missing data."),
    "DQ-004": DownstreamImpact(["pd"], ["Expected loss", "IFRS 9 staging", "stress testing"], ["FINREP provisions", "COREP capital"], "Invalid PD can make ECL and capital outputs unusable until remediated.", 0.0, "Impact calculated only after explicit remediation assumptions."),
    "DQ-005": DownstreamImpact(["lgd"], ["LGD", "IFRS 9 ECL", "IRB"], ["FINREP provisions", "COREP capital"], "Invalid LGD can distort loss severity and RWA comparisons.", 0.0, "Collateral and recovery data are simplified."),
    "DQ-006": DownstreamImpact(["ead"], ["EAD", "Expected loss", "Basel RWA"], ["COREP exposure", "FINREP assets"], "Negative exposure is blocked from financial engines and reporting readiness.", 0.0, "Assumes remediation sets exposure to a validated non-negative amount."),
    "DQ-010": DownstreamImpact(["collateral_valuation_date", "lgd"], ["LGD", "downturn LGD", "IFRS 9 ECL"], ["FINREP provisions", "COREP capital"], "Stale collateral can understate downturn LGD if property values declined.", 0.0, "Does not estimate market-value truth."),
    "DQ-014": DownstreamImpact(["ead", "exposure"], ["EAD", "Expected loss"], ["FINREP assets", "COREP exposure"], "Risk-versus-Finance mismatch creates reporting uncertainty and sign-off limitations.", 0.0, "Timing and mapping differences require owner explanation."),
}


def impact_for_control(control_id: str, records_failed: int, frame: pd.DataFrame) -> DownstreamImpact:
    base = IMPACT_MAP.get(
        control_id,
        DownstreamImpact(["portfolio data"], ["Risk aggregation"], ["Executive risk report"], "Control failure lowers confidence in risk reporting.", 0.0, "Impact is qualitative unless a sensitivity is available."),
    )
    return DownstreamImpact(
        affected_data_elements=base.affected_data_elements,
        affected_models=base.affected_models,
        affected_reports=base.affected_reports,
        likely_directional_impact=base.likely_directional_impact,
        estimated_materiality=float(records_failed),
        limitations=base.limitations,
    )


def missing_income_sensitivity(frame: pd.DataFrame, cet1: float, rwa: float) -> dict[str, float | str]:
    required = {"income", "pd", "lgd", "ead"}
    if not required.issubset(frame.columns):
        return {"label": "Illustrative sensitivity impact, not a definitive financial adjustment.", "missing_income_rate": 0.0, "base_ecl": 0.0, "conservative_ecl": 0.0, "incremental_ecl": 0.0, "cet1_impact": 0.0, "cet1_ratio_impact": 0.0}
    valid = frame.dropna(subset=["pd", "lgd", "ead"]).copy()
    valid = valid[(valid["pd"].between(0, 1)) & (valid["lgd"].between(0, 1)) & (valid["ead"] >= 0)]
    base_ecl = sum(point_in_time_expected_loss(float(r.pd), float(r.lgd), float(r.ead)).expected_loss for r in valid.itertuples())
    conservative = valid.copy()
    missing_mask = conservative["income"].isna()
    conservative.loc[missing_mask, "pd"] = (conservative.loc[missing_mask, "pd"] * 1.25).clip(upper=1.0)
    conservative_ecl = sum(point_in_time_expected_loss(float(r.pd), float(r.lgd), float(r.ead)).expected_loss for r in conservative.itertuples())
    incremental = conservative_ecl - base_ecl
    capital = capital_movement_bridge(
        CapitalBridgeInput(opening_cet1=cet1, profit_before_impairment=0.0, incremental_impairment=incremental, tax_rate=0.25)
    )
    return {
        "label": "Illustrative sensitivity impact, not a definitive financial adjustment.",
        "missing_income_rate": float(frame["income"].isna().mean()),
        "base_ecl": float(base_ecl),
        "conservative_ecl": float(conservative_ecl),
        "incremental_ecl": float(incremental),
        "cet1_impact": float(capital.closing_cet1 - cet1),
        "cet1_ratio_impact": float((capital.closing_cet1 - cet1) / rwa) if rwa else 0.0,
    }
