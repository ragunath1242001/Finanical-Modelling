"""Application data loading and portfolio-level calculation context."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from src.data.loaders import load_customers, load_financials, load_loans, load_transactions
from src.financial_crime.aml import aml_alerts
from src.financial_crime.fraud import alert_queue
from src.governance.data_quality import run_quality_checks
from src.reporting.downloads import pdf_report_bytes
from src.reporting.portfolio import apply_portfolio_shocks, portfolio_expected_loss, portfolio_risk_inputs
from src.risk.basel import capital_after_provision, capital_ratios, rwa
from src.risk.stress_testing import SCENARIOS, stress_ecl


BASE_CET1 = 8_500_000.0
AT1 = 750_000.0
TIER2 = 1_100_000.0


FIELD_DEFINITIONS = {
    "customers": {
        "customer_id": "Synthetic customer identifier used to join customers, loans, and transactions.",
        "age": "Customer age.",
        "income": "Annual income; includes missing values for data quality testing.",
        "employment_status": "Employment category used in PD modelling and risk segmentation.",
        "credit_score": "Synthetic credit score used in PD, explainability, and model development.",
        "debt_to_income": "Debt-to-income ratio used as an affordability and credit risk driver.",
        "country": "Customer country code for portfolio segmentation.",
        "customer_risk": "Simple low/medium/high risk label for segmentation.",
    },
    "loans": {
        "loan_id": "Synthetic loan identifier.",
        "customer_id": "Customer join key.",
        "product_type": "Loan product such as mortgage, personal loan, credit card, or SME loan.",
        "loan_amount": "Original loan amount; includes negative records for quality checks.",
        "outstanding_balance": "Current balance before EAD conversion.",
        "ltv": "Loan-to-value ratio used in LGD and secured lending analysis.",
        "days_past_due": "Delinquency measure used for IFRS 9 staging and default identification.",
        "default_flag": "Synthetic default marker used for model development and validation.",
        "pd": "Probability of default used across ECL, stress testing, IRB, and XVA-style thinking.",
        "lgd": "Loss given default used in expected loss and provision calculations.",
        "ead": "Exposure at default used in ECL, capital, and concentration analysis.",
        "last_update_days": "Data freshness indicator used in governance checks.",
    },
    "transactions": {
        "transaction_id": "Synthetic transaction identifier.",
        "customer_id": "Customer join key.",
        "amount": "Transaction amount used by fraud and AML rules.",
        "merchant_category": "Merchant segment used for fraud indicators.",
        "hour": "Transaction hour used for behaviour context.",
        "country_risk": "Standard or high country risk flag for AML screening.",
        "device_mismatch": "Fraud signal showing whether the device differs from normal behaviour.",
        "velocity_24h": "Number of recent transactions used for velocity risk.",
        "round_amount": "AML indicator for unusually round amounts.",
        "rapid_in_out": "AML indicator for quick movement of funds.",
        "fraud_label": "Synthetic fraud outcome label for testing alert logic.",
    },
    "financials": {
        "month": "Monthly reporting period.",
        "loan_balances": "Portfolio loan balance trend for forecasting and FINREP-style analysis.",
        "deposit_balances": "Deposit trend used for balance sheet context.",
        "net_interest_income": "Monthly NII used in forecasting.",
        "provisions": "Monthly provision amount used in financial trend analysis.",
        "fraud_aml_alerts": "Monthly financial crime alert count.",
    },
}


@dataclass(frozen=True)
class AppData:
    customers: pd.DataFrame
    loans_raw: pd.DataFrame
    transactions: pd.DataFrame
    financials: pd.DataFrame


@dataclass(frozen=True)
class PortfolioContext:
    data: AppData
    scenario: str
    loans: pd.DataFrame
    portfolio_pd: float
    portfolio_lgd: float
    portfolio_ead: float
    portfolio_ecl: float
    base_rwa: float
    base_cet1: float
    at1: float
    tier2: float
    stressed: dict[str, float]
    post_cet1: float
    ratios: dict[str, float]
    liq_lcr: float
    liq_nsfr: float
    quality_table: pd.DataFrame
    quality_score: float
    fraud_scored: pd.DataFrame
    aml_scored: pd.DataFrame


@st.cache_data
def load_app_data() -> AppData:
    return AppData(load_customers(), load_loans(), load_transactions(), load_financials())


def build_portfolio_context(data: AppData, pd_shock: float, lgd_shock: float, scenario: str) -> PortfolioContext:
    portfolio_pd, portfolio_lgd, portfolio_ead = portfolio_risk_inputs(data.loans_raw)
    loans = apply_portfolio_shocks(data.loans_raw, pd_shock, lgd_shock)
    portfolio_ecl = portfolio_expected_loss(loans)

    base_rwa = rwa(portfolio_ead, 0.55)
    stressed = stress_ecl(
        portfolio_pd,
        portfolio_lgd,
        portfolio_ead,
        SCENARIOS[scenario]["pd_multiplier"],
        SCENARIOS[scenario]["lgd_multiplier"],
    )
    post_cet1 = capital_after_provision(BASE_CET1, stressed["provision_increase"])
    ratios = capital_ratios(post_cet1, AT1, TIER2, base_rwa)
    quality_table, quality_score = run_quality_checks(data.loans_raw, data.customers)

    return PortfolioContext(
        data=data,
        scenario=scenario,
        loans=loans,
        portfolio_pd=portfolio_pd,
        portfolio_lgd=portfolio_lgd,
        portfolio_ead=portfolio_ead,
        portfolio_ecl=portfolio_ecl,
        base_rwa=base_rwa,
        base_cet1=BASE_CET1,
        at1=AT1,
        tier2=TIER2,
        stressed=stressed,
        post_cet1=post_cet1,
        ratios=ratios,
        liq_lcr=18_000_000 / 14_500_000,
        liq_nsfr=74_000_000 / 71_000_000,
        quality_table=quality_table,
        quality_score=quality_score,
        fraud_scored=alert_queue(data.transactions, 0.35),
        aml_scored=aml_alerts(data.transactions),
    )


def dataset_summary(data: AppData) -> pd.DataFrame:
    frames = {
        "Customers": data.customers,
        "Loans": data.loans_raw,
        "Transactions": data.transactions,
        "Financials": data.financials,
    }
    return pd.DataFrame(
        [
            {
                "dataset": name,
                "rows": len(frame),
                "fields": len(frame.columns),
                "missing_values": int(frame.isna().sum().sum()),
                "duplicate_rows": int(frame.duplicated().sum()),
            }
            for name, frame in frames.items()
        ]
    )


def field_inventory(data: AppData) -> pd.DataFrame:
    frames = {
        "customers": data.customers,
        "loans": data.loans_raw,
        "transactions": data.transactions,
        "financials": data.financials,
    }
    rows = []
    for dataset, frame in frames.items():
        for column in frame.columns:
            rows.append(
                {
                    "dataset": dataset,
                    "field": column,
                    "type": str(frame[column].dtype),
                    "missing": int(frame[column].isna().sum()),
                    "definition": FIELD_DEFINITIONS.get(dataset, {}).get(column, "Synthetic project field."),
                }
            )
    return pd.DataFrame(rows)


def data_dictionary_pdf(data: AppData) -> bytes:
    inventory = field_inventory(data)
    sections = {
        "Portfolio Narrative": (
            "The synthetic bank portfolio represents a small European-style retail and SME banking book. "
            "Customers hold loans, generate transactions, and feed financial trends. The data intentionally includes missing values, "
            "stale records, duplicate identifiers, invalid loan amounts, exposure mismatches, and suspicious transaction patterns so the app can demonstrate risk analytics and governance controls."
        ),
        "Dataset Summary": "\n".join(
            f"- {row.dataset}: {row.rows} rows, {row.fields} fields, {row.missing_values} missing values, {row.duplicate_rows} duplicate rows"
            for row in dataset_summary(data).itertuples(index=False)
        ),
        "Field Inventory": "\n".join(
            f"- {row.dataset}.{row.field} ({row.type}): {row.definition}; missing values: {row.missing}"
            for row in inventory.itertuples(index=False)
        ),
        "How To Use The Data": (
            "Start with customers and loans to understand borrower risk. Use transactions for fraud and AML monitoring. "
            "Use financial trends for forecasting and reporting context. Then use governance checks to see how data quality affects confidence in risk outputs."
        ),
    }
    return pdf_report_bytes("Data Dictionary and Portfolio Narrative", sections)
