from __future__ import annotations

import pandas as pd


CONTROL_WEIGHTS = {
    "risk_management": 15,
    "data_governance": 15,
    "technical_documentation": 12,
    "logging_traceability": 12,
    "transparency_explainability": 14,
    "human_oversight": 12,
    "accuracy_robustness": 10,
    "post_market_monitoring": 10,
}


def ai_act_control_assessment(controls: dict[str, bool]) -> tuple[pd.DataFrame, float]:
    rows = []
    total = 0
    for control, weight in CONTROL_WEIGHTS.items():
        implemented = bool(controls.get(control, False))
        score = weight if implemented else 0
        total += score
        rows.append(
            {
                "control": control.replace("_", " ").title(),
                "weight": weight,
                "implemented": implemented,
                "score": score,
                "status": "Implemented" if implemented else "Gap",
            }
        )
    return pd.DataFrame(rows), float(total)


def ai_risk_tier(use_case: str, automated_decision: bool, affects_access_to_credit: bool) -> str:
    if affects_access_to_credit or use_case.lower() in {"credit scoring", "underwriting", "aml monitoring", "fraud detection"}:
        return "High-risk AI system"
    if automated_decision:
        return "Limited-risk AI system"
    return "Minimal-risk AI system"


def fairness_gap(approval_rate_group_a: float, approval_rate_group_b: float) -> dict[str, float | str]:
    gap = round(abs(approval_rate_group_a - approval_rate_group_b), 6)
    return {
        "approval_rate_group_a": approval_rate_group_a,
        "approval_rate_group_b": approval_rate_group_b,
        "absolute_gap": gap,
        "status": "Fairness review required" if gap >= 0.10 else "Within illustrative tolerance",
    }
