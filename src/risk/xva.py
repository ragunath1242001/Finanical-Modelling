from __future__ import annotations

import pandas as pd


def exposure_profile(notional: float, maturity_years: int, volatility: float, collateral_coverage: float) -> pd.DataFrame:
    rows = []
    for year in range(1, maturity_years + 1):
        decay = max(0.15, 1 - year / (maturity_years + 1))
        expected_positive_exposure = notional * volatility * decay * (1 - collateral_coverage)
        rows.append({"year": year, "expected_positive_exposure": expected_positive_exposure})
    return pd.DataFrame(rows)


def cva(profile: pd.DataFrame, annual_pd: float, lgd: float, discount_rate: float) -> float:
    total = 0.0
    survival = 1.0
    for _, row in profile.iterrows():
        year = int(row["year"])
        marginal_pd = survival * annual_pd
        discount = 1 / ((1 + discount_rate) ** year)
        total += row["expected_positive_exposure"] * marginal_pd * lgd * discount
        survival *= 1 - annual_pd
    return round(total, 6)


def dva(profile: pd.DataFrame, own_annual_pd: float, own_lgd: float, discount_rate: float) -> float:
    return cva(profile, own_annual_pd, own_lgd, discount_rate)


def fva(profile: pd.DataFrame, funding_spread: float, discount_rate: float) -> float:
    total = 0.0
    for _, row in profile.iterrows():
        year = int(row["year"])
        discount = 1 / ((1 + discount_rate) ** year)
        total += row["expected_positive_exposure"] * funding_spread * discount
    return round(total, 6)


def mva(initial_margin: float, margin_funding_spread: float, maturity_years: int, discount_rate: float) -> float:
    total = 0.0
    for year in range(1, maturity_years + 1):
        discount = 1 / ((1 + discount_rate) ** year)
        total += initial_margin * margin_funding_spread * discount
    return round(total, 6)


def xva_summary(
    notional: float,
    maturity_years: int,
    volatility: float,
    collateral_coverage: float,
    counterparty_pd: float,
    counterparty_lgd: float,
    own_pd: float,
    funding_spread: float,
    initial_margin: float,
    margin_funding_spread: float,
    discount_rate: float,
) -> tuple[pd.DataFrame, dict[str, float]]:
    profile = exposure_profile(notional, maturity_years, volatility, collateral_coverage)
    cva_value = cva(profile, counterparty_pd, counterparty_lgd, discount_rate)
    dva_value = dva(profile, own_pd, counterparty_lgd, discount_rate)
    fva_value = fva(profile, funding_spread, discount_rate)
    mva_value = mva(initial_margin, margin_funding_spread, maturity_years, discount_rate)
    return profile, {
        "CVA": cva_value,
        "DVA": dva_value,
        "FVA": fva_value,
        "MVA": mva_value,
        "Total XVA cost": cva_value + fva_value + mva_value - dva_value,
    }
