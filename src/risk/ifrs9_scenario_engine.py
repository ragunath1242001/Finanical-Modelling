from __future__ import annotations

import pandas as pd

from src.risk.ifrs9 import assign_stage


DEFAULT_SCENARIOS = {
    "Upside": {"weight": 0.20, "pd_multiplier": 0.85, "lgd_multiplier": 0.95},
    "Baseline": {"weight": 0.55, "pd_multiplier": 1.00, "lgd_multiplier": 1.00},
    "Downside": {"weight": 0.25, "pd_multiplier": 1.65, "lgd_multiplier": 1.20},
}


def lifetime_pd(twelve_month_pd: float, stage: int, remaining_life_years: float = 4.0) -> float:
    if stage == 1:
        return min(twelve_month_pd, 1.0)
    return min(1 - (1 - twelve_month_pd) ** remaining_life_years, 1.0)


def scenario_weighted_ecl(
    loans: pd.DataFrame,
    scenarios: dict[str, dict[str, float]] | None = None,
    remaining_life_years: float = 4.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    scenarios = scenarios or DEFAULT_SCENARIOS
    rows = []
    loan_level = loans.copy()
    loan_level["base_stage"] = loan_level.apply(lambda row: assign_stage(int(row["days_past_due"]), default_flag=bool(row["default_flag"]))[0], axis=1)
    loan_level["weighted_ecl"] = 0.0
    for scenario_name, params in scenarios.items():
        pd_s = (loan_level["pd"].fillna(loan_level["pd"].median()) * params["pd_multiplier"]).clip(0, 1)
        lgd_s = (loan_level["lgd"] * params["lgd_multiplier"]).clip(0, 1)
        scenario_ecl = []
        for pd_value, lgd_value, ead, stage in zip(pd_s, lgd_s, loan_level["ead"], loan_level["base_stage"]):
            ecl_pd = lifetime_pd(float(pd_value), int(stage), remaining_life_years)
            scenario_ecl.append(ecl_pd * float(lgd_value) * float(ead))
        loan_level[f"{scenario_name.lower()}_ecl"] = scenario_ecl
        loan_level["weighted_ecl"] += params["weight"] * loan_level[f"{scenario_name.lower()}_ecl"]
        rows.append(
            {
                "scenario": scenario_name,
                "weight": params["weight"],
                "pd_multiplier": params["pd_multiplier"],
                "lgd_multiplier": params["lgd_multiplier"],
                "scenario_ecl": float(sum(scenario_ecl)),
            }
        )
    return loan_level, pd.DataFrame(rows)


def stage_migration_table(loans: pd.DataFrame, pd_multiplier: float = 1.0, stage2_pd_threshold: float = 0.08) -> pd.DataFrame:
    frame = loans.copy()
    frame["opening_stage"] = frame.apply(lambda row: assign_stage(int(row["days_past_due"]), default_flag=bool(row["default_flag"]))[0], axis=1)
    stressed_pd = frame["pd"].fillna(frame["pd"].median()) * pd_multiplier
    frame["closing_stage"] = frame["opening_stage"]
    frame.loc[(frame["opening_stage"] == 1) & (stressed_pd >= stage2_pd_threshold), "closing_stage"] = 2
    table = pd.crosstab(frame["opening_stage"], frame["closing_stage"])
    table.index = [f"Opening Stage {idx}" for idx in table.index]
    table.columns = [f"Closing Stage {col}" for col in table.columns]
    return table


def ecl_bridge(opening_ecl: float, new_lending: float, repayments: float, stage_migration: float, macro_overlay: float) -> pd.DataFrame:
    closing = opening_ecl + new_lending - repayments + stage_migration + macro_overlay
    return pd.DataFrame(
        [
            {"component": "Opening ECL", "amount": opening_ecl},
            {"component": "New lending", "amount": new_lending},
            {"component": "Repayments", "amount": -repayments},
            {"component": "Stage migration", "amount": stage_migration},
            {"component": "Macro overlay", "amount": macro_overlay},
            {"component": "Closing ECL", "amount": closing},
        ]
    )
