from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import DATA_DIR
from src.risk.lgd_ead import calculate_ead, calculate_lgd


def generate_customers(n: int = 750, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    customers = pd.DataFrame(
        {
            "customer_id": [f"C{i:05d}" for i in range(n)],
            "age": rng.integers(19, 78, n),
            "income": rng.normal(52000, 21000, n).clip(9000, 180000),
            "employment_status": rng.choice(["employed", "self-employed", "student", "unemployed"], n, p=[0.66, 0.18, 0.08, 0.08]),
            "credit_score": rng.normal(665, 82, n).clip(300, 850),
            "debt_to_income": rng.beta(2.1, 5.2, n).clip(0.02, 0.95),
            "country": rng.choice(["DE", "FR", "NL", "ES", "IT", "IE"], n),
            "customer_risk": rng.choice(["low", "medium", "high"], n, p=[0.58, 0.31, 0.11]),
        }
    )
    missing_income = rng.choice(customers.index, size=max(8, n // 30), replace=False)
    customers.loc[missing_income, "income"] = np.nan
    customers.loc[n - 2, "customer_id"] = customers.loc[0, "customer_id"]
    return customers


def _pd_formula(score: pd.Series, dti: pd.Series, dpd: pd.Series, unemployment: pd.Series) -> pd.Series:
    raw = -4.2 + (700 - score) / 95 + dti * 2.4 + (dpd > 0) * 0.7 + (dpd >= 30) * 0.9 + unemployment * 1.0
    return 1 / (1 + np.exp(-raw))


def generate_loans(customers: pd.DataFrame, seed: int = 43) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n = len(customers)
    product = rng.choice(["mortgage", "personal loan", "credit card", "SME loan"], n, p=[0.32, 0.28, 0.25, 0.15])
    loan_amount = rng.lognormal(10.8, 0.72, n).clip(1000, 600000)
    outstanding = loan_amount * rng.uniform(0.22, 1.0, n)
    ltv = rng.normal(0.67, 0.19, n).clip(0.05, 1.35)
    dpd = rng.choice([0, 5, 15, 31, 61, 95, 130], n, p=[0.72, 0.09, 0.07, 0.05, 0.035, 0.025, 0.01])
    unemployed = (customers["employment_status"].eq("unemployed")).astype(float)
    pd_values = _pd_formula(customers["credit_score"], customers["debt_to_income"], pd.Series(dpd), unemployed).clip(0.002, 0.85)
    default_flag = (dpd >= 90) | (rng.random(n) < pd_values * 0.12)
    loans = pd.DataFrame(
        {
            "loan_id": [f"L{i:05d}" for i in range(n)],
            "customer_id": customers["customer_id"].to_numpy(),
            "product_type": product,
            "loan_amount": loan_amount.round(2),
            "outstanding_balance": outstanding.round(2),
            "ltv": ltv.round(3),
            "days_past_due": dpd,
            "default_flag": default_flag,
            "pd": pd_values.round(5),
            "lgd": [calculate_lgd(p, v) for p, v in zip(product, ltv)],
            "ead": [calculate_ead(p, b, a) for p, b, a in zip(product, outstanding, loan_amount)],
            "last_update_days": rng.integers(0, 75, n),
        }
    )
    loans.loc[rng.choice(loans.index, size=max(5, n // 50), replace=False), "pd"] = np.nan
    loans.loc[rng.choice(loans.index, size=3, replace=False), "loan_amount"] = -1000
    return loans


def generate_transactions(customers: pd.DataFrame, n: int = 2500, seed: int = 44) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    amount = rng.lognormal(4.3, 1.1, n).round(2)
    high_risk_country = rng.choice([False, True], n, p=[0.88, 0.12])
    device_mismatch = rng.choice([False, True], n, p=[0.9, 0.1])
    velocity = rng.poisson(2.2, n)
    fraud_prob = np.clip(0.015 + (amount > 1200) * 0.06 + device_mismatch * 0.18 + (velocity > 5) * 0.10, 0, 0.8)
    return pd.DataFrame(
        {
            "transaction_id": [f"T{i:06d}" for i in range(n)],
            "customer_id": rng.choice(customers["customer_id"], n),
            "amount": amount,
            "merchant_category": rng.choice(["groceries", "travel", "electronics", "cash", "crypto", "utilities"], n),
            "hour": rng.integers(0, 24, n),
            "country_risk": np.where(high_risk_country, "high", "standard"),
            "device_mismatch": device_mismatch,
            "velocity_24h": velocity,
            "round_amount": amount % 100 == 0,
            "rapid_in_out": rng.choice([False, True], n, p=[0.93, 0.07]),
            "fraud_label": rng.random(n) < fraud_prob,
        }
    )


def generate_financials(seed: int = 45) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    months = pd.date_range("2024-01-31", periods=30, freq="ME")
    base_loans = 92_000_000 + np.cumsum(rng.normal(550_000, 650_000, len(months)))
    return pd.DataFrame(
        {
            "month": months,
            "loan_balances": base_loans,
            "deposit_balances": base_loans * rng.uniform(0.78, 0.92, len(months)),
            "net_interest_income": base_loans * rng.uniform(0.0024, 0.0032, len(months)),
            "provisions": base_loans * rng.uniform(0.0007, 0.0015, len(months)),
            "fraud_aml_alerts": rng.integers(60, 145, len(months)),
        }
    )


def main() -> None:
    customers = generate_customers()
    loans = generate_loans(customers)
    transactions = generate_transactions(customers)
    financials = generate_financials()
    customers.to_csv(DATA_DIR / "customers.csv", index=False)
    loans.to_csv(DATA_DIR / "loans.csv", index=False)
    transactions.to_csv(DATA_DIR / "transactions.csv", index=False)
    financials.to_csv(DATA_DIR / "financials.csv", index=False)
    print(f"Synthetic data written to {DATA_DIR}")


if __name__ == "__main__":
    main()
