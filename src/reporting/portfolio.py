"""Reusable portfolio-level calculation helpers used by reporting pages."""

from __future__ import annotations

import pandas as pd

from src.risk.ifrs9 import assign_stage


def portfolio_risk_inputs(loans: pd.DataFrame) -> tuple[float, float, float]:
    portfolio_pd = float(loans["pd"].fillna(loans["pd"].median()).mean())
    portfolio_lgd = float(loans["lgd"].mean())
    portfolio_ead = float(loans["ead"].sum())
    return portfolio_pd, portfolio_lgd, portfolio_ead


def apply_portfolio_shocks(loans_raw: pd.DataFrame, pd_shock: float, lgd_shock: float) -> pd.DataFrame:
    loans = loans_raw.copy()
    adjusted_pd = (loans["pd"].fillna(loans["pd"].median()) * (1 + pd_shock)).clip(0, 1)
    adjusted_lgd = (loans["lgd"] * (1 + lgd_shock)).clip(0, 1)
    loans["adjusted_pd"] = adjusted_pd
    loans["adjusted_lgd"] = adjusted_lgd
    loans["expected_loss"] = loans["adjusted_pd"] * loans["adjusted_lgd"] * loans["ead"]
    return loans


def portfolio_expected_loss(loans: pd.DataFrame) -> float:
    return float(loans["expected_loss"].sum())


def product_expected_loss(loans: pd.DataFrame) -> pd.DataFrame:
    return loans.groupby("product_type", as_index=False)["expected_loss"].sum().sort_values("expected_loss", ascending=False)


def product_risk_summary(loans: pd.DataFrame) -> pd.DataFrame:
    return (
        loans.groupby("product_type", as_index=False)
        .agg(loans=("loan_id", "count"), ead=("ead", "sum"), expected_loss=("expected_loss", "sum"))
        .sort_values("expected_loss", ascending=False)
    )


def ifrs9_stage_mix(loans_raw: pd.DataFrame) -> pd.DataFrame:
    return (
        loans_raw.assign(
            stage=loans_raw.apply(
                lambda row: f"Stage {assign_stage(int(row['days_past_due']), default_flag=bool(row['default_flag']))[0]}",
                axis=1,
            )
        )["stage"]
        .value_counts()
        .rename_axis("stage")
        .reset_index(name="loans")
    )


def fraud_alert_distribution(fraud_scored: pd.DataFrame) -> pd.DataFrame:
    return fraud_scored["risk_label"].value_counts().rename_axis("risk_label").reset_index(name="transactions")


def capital_impact_waterfall(base_cet1: float, provision_increase: float, revenue_shock: float, stressed_cet1: float) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "step": ["Opening CET1", "Provision increase", "Revenue shock", "Closing CET1"],
            "amount": [base_cet1, -provision_increase, base_cet1 * revenue_shock, stressed_cet1 + base_cet1 * revenue_shock],
        }
    )


def crr3_rwa_stack(binding_credit_rwa: float, market_rwa: float, cva_rwa: float, operational_rwa: float) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "component": ["Binding credit RWA", "Market RWA", "CVA RWA", "Operational RWA"],
            "amount": [binding_credit_rwa, market_rwa, cva_rwa, operational_rwa],
        }
    )
