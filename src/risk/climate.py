from __future__ import annotations

import pandas as pd


SECTOR_TRANSITION_MULTIPLIERS = {
    "Real estate": 1.10,
    "Manufacturing": 1.20,
    "Energy": 1.45,
    "Transport": 1.35,
    "Technology": 1.03,
    "Services": 1.08,
}

PHYSICAL_RISK_MULTIPLIERS = {
    "Low": 1.00,
    "Medium": 1.12,
    "High": 1.30,
}


def climate_pd_multiplier(sector: str, physical_risk: str, carbon_price_eur: float, disorderly_transition: bool) -> float:
    transition = SECTOR_TRANSITION_MULTIPLIERS.get(sector, 1.1)
    physical = PHYSICAL_RISK_MULTIPLIERS.get(physical_risk, 1.0)
    carbon_addon = 1 + min(max(carbon_price_eur, 0), 250) / 1000
    disorderly = 1.25 if disorderly_transition else 1.0
    return round(transition * physical * carbon_addon * disorderly, 4)


def climate_adjusted_credit_risk(
    pd: float,
    lgd: float,
    ead: float,
    sector: str,
    physical_risk: str,
    carbon_price_eur: float,
    collateral_value_decline: float,
    disorderly_transition: bool,
) -> dict[str, float]:
    multiplier = climate_pd_multiplier(sector, physical_risk, carbon_price_eur, disorderly_transition)
    adjusted_pd = min(pd * multiplier, 1.0)
    adjusted_lgd = min(lgd + max(0.0, collateral_value_decline) * 0.35, 1.0)
    baseline_ecl = pd * lgd * ead
    climate_ecl = adjusted_pd * adjusted_lgd * ead
    return {
        "pd_multiplier": multiplier,
        "adjusted_pd": adjusted_pd,
        "adjusted_lgd": adjusted_lgd,
        "baseline_ecl": baseline_ecl,
        "climate_ecl": climate_ecl,
        "ecl_increase": max(0.0, climate_ecl - baseline_ecl),
    }


def climate_portfolio_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["Energy", "High", 18_000_000, 0.42],
            ["Transport", "Medium", 13_500_000, 0.31],
            ["Real estate", "High", 28_000_000, 0.27],
            ["Technology", "Low", 9_000_000, 0.08],
            ["Services", "Medium", 16_500_000, 0.15],
        ],
        columns=["sector", "physical_risk", "exposure", "financed_emissions_intensity"],
    )
