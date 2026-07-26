from __future__ import annotations

import pandas as pd


CASE_STUDIES = {
    "Unemployment shock drives credit deterioration": {
        "description": "A macro shock increases borrower stress, raising PD, IFRS 9 provisions, and capital pressure.",
        "pd_multiplier": 1.55,
        "lgd_multiplier": 1.10,
        "data_quality_penalty": 0.00,
        "operational_loss": 0.0,
    },
    "Data quality issue causes IFRS 9 misstatement": {
        "description": "Missing PD and stale records reduce confidence in provisions and trigger BCBS 239 remediation.",
        "pd_multiplier": 1.15,
        "lgd_multiplier": 1.00,
        "data_quality_penalty": 0.12,
        "operational_loss": 0.0,
    },
    "Model drift alert triggers validation review": {
        "description": "PD distribution shifts, forcing model monitoring, validation challenge, and conservative overlay.",
        "pd_multiplier": 1.35,
        "lgd_multiplier": 1.05,
        "data_quality_penalty": 0.03,
        "operational_loss": 0.0,
    },
    "DORA incident affects reporting operations": {
        "description": "A critical ICT disruption creates operational loss and reporting-control pressure.",
        "pd_multiplier": 1.05,
        "lgd_multiplier": 1.00,
        "data_quality_penalty": 0.05,
        "operational_loss": 450_000.0,
    },
}


def run_case_study(
    loans: pd.DataFrame,
    case_name: str,
    cet1: float,
    rwa_amount: float,
    profit_before_provisions: float = 3_600_000.0,
) -> dict[str, float | str]:
    case = CASE_STUDIES[case_name]
    base_pd = loans["pd"].fillna(loans["pd"].median())
    base_lgd = loans["lgd"]
    ead = loans["ead"]
    baseline_ecl = float((base_pd * base_lgd * ead).sum())
    stressed_pd = (base_pd * float(case["pd_multiplier"])).clip(0, 1)
    stressed_lgd = (base_lgd * float(case["lgd_multiplier"])).clip(0, 1)
    stressed_ecl = float((stressed_pd * stressed_lgd * ead).sum())
    data_overlay = stressed_ecl * float(case["data_quality_penalty"])
    provision_increase = max(0.0, stressed_ecl + data_overlay - baseline_ecl)
    total_loss = provision_increase + float(case["operational_loss"])
    post_profit = profit_before_provisions - provision_increase - float(case["operational_loss"])
    post_cet1 = max(0.0, cet1 - total_loss)
    return {
        "case": case_name,
        "description": str(case["description"]),
        "baseline_ecl": baseline_ecl,
        "stressed_ecl": stressed_ecl,
        "data_quality_overlay": data_overlay,
        "provision_increase": provision_increase,
        "operational_loss": float(case["operational_loss"]),
        "post_profit": post_profit,
        "post_cet1": post_cet1,
        "opening_cet1_ratio": cet1 / rwa_amount,
        "post_cet1_ratio": post_cet1 / rwa_amount,
        "cet1_ratio_change_bps": ((post_cet1 / rwa_amount) - (cet1 / rwa_amount)) * 10_000,
    }


def case_study_steps(result: dict[str, float | str]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["Scenario trigger", result["description"]],
            ["Credit impact", f"Baseline ECL moves to EUR {result['stressed_ecl']:,.0f}."],
            ["Governance overlay", f"Data/model/control overlay adds EUR {result['data_quality_overlay']:,.0f}."],
            ["Provision impact", f"Provision increase is EUR {result['provision_increase']:,.0f}."],
            ["Capital impact", f"CET1 ratio changes by {result['cet1_ratio_change_bps']:,.0f} bps."],
            ["Management action", "Review capital plan, lending appetite, remediation ownership, and audit evidence."],
        ],
        columns=["step", "explanation"],
    )
