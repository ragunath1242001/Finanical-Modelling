"""Deterministic synthetic governance datasets with intentional defects."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd


REFERENCE_DATE = date(2026, 7, 27)


def clean_portfolio() -> pd.DataFrame:
    rows = []
    for idx in range(12):
        rows.append(
            {
                "customer_id": f"C{idx:05d}",
                "account_id": f"A{idx:05d}",
                "facility_id": f"F{idx:05d}",
                "income": 55_000 + idx * 1_000,
                "pd": 0.01 + idx * 0.001,
                "lgd": 0.25 + (idx % 4) * 0.05,
                "ead": 50_000 + idx * 2_000,
                "risk_grade": ["A", "B", "C", "D"][idx % 4],
                "model_version": "PD-v1.0",
                "source_system": "Loan Origination System",
                "collateral_valuation_date": REFERENCE_DATE - timedelta(days=80),
                "origination_pd": 0.009 + idx * 0.001,
                "ifrs9_stage": [1, 1, 2, 1][idx % 4],
                "scenario_weight_total": 1.0,
                "lineage_link": f"LIN-{idx:05d}",
                "reporting_date": REFERENCE_DATE,
                "issue_owner": "1LOD Data Steward",
                "remediation_due_date": REFERENCE_DATE + timedelta(days=20),
                "issue_status": "Open",
                "closure_evidence": "N/A",
                "two_lod_conclusion": "N/A",
                "product": "Mortgage" if idx % 2 == 0 else "SME",
                "currency": "EUR",
                "legal_entity": "Synthetic Bank EU",
            }
        )
    return pd.DataFrame(rows)


def defective_portfolio() -> pd.DataFrame:
    frame = clean_portfolio()
    frame.loc[[0, 1, 2, 3], "income"] = pd.NA
    frame.loc[4, "customer_id"] = pd.NA
    frame.loc[5, "customer_id"] = frame.loc[6, "customer_id"]
    frame.loc[6, "pd"] = 1.25
    frame.loc[7, "pd"] = -0.02
    frame.loc[8, "lgd"] = 1.4
    frame.loc[9, "ead"] = -5000
    frame.loc[10, "risk_grade"] = "Z"
    frame.loc[11, "model_version"] = ""
    frame.loc[0, "source_system"] = ""
    frame.loc[1, "collateral_valuation_date"] = REFERENCE_DATE - timedelta(days=520)
    frame.loc[2, "origination_pd"] = pd.NA
    frame.loc[3, "ifrs9_stage"] = 5
    frame.loc[4, "scenario_weight_total"] = 0.9
    frame.loc[5, "lineage_link"] = ""
    frame.loc[6, "reporting_date"] = REFERENCE_DATE - timedelta(days=3)
    frame.loc[7, "issue_owner"] = ""
    frame.loc[8, "remediation_due_date"] = REFERENCE_DATE - timedelta(days=10)
    frame.loc[9, "issue_status"] = "Closed"
    frame.loc[9, "closure_evidence"] = ""
    frame.loc[10, "issue_status"] = "Closed"
    frame.loc[10, "two_lod_conclusion"] = "Rejected"
    return frame


def risk_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"customer_id": "C00001", "account_id": "A00001", "facility_id": "F00001", "reporting_date": REFERENCE_DATE, "exposure": 100_000.0, "provision": 900.0, "ifrs9_stage": 1, "currency": "EUR", "product": "Mortgage", "legal_entity": "Synthetic Bank EU", "model_version": "PD-v1.0"},
            {"customer_id": "C00002", "account_id": "A00002", "facility_id": "F00002", "reporting_date": REFERENCE_DATE, "exposure": 80_000.0, "provision": 1_800.0, "ifrs9_stage": 2, "currency": "EUR", "product": "SME", "legal_entity": "Synthetic Bank EU", "model_version": "PD-v1.0"},
            {"customer_id": "C00003", "account_id": "A00003", "facility_id": "F00003", "reporting_date": REFERENCE_DATE, "exposure": 60_000.0, "provision": 5_500.0, "ifrs9_stage": 3, "currency": "EUR", "product": "Personal", "legal_entity": "Synthetic Bank EU", "model_version": "PD-v1.0"},
            {"customer_id": "C00004", "account_id": "A00004", "facility_id": "F00004", "reporting_date": REFERENCE_DATE, "exposure": 40_000.0, "provision": 600.0, "ifrs9_stage": 1, "currency": "EUR", "product": "Credit Card", "legal_entity": "Synthetic Bank EU", "model_version": "PD-v1.0"},
        ]
    )


def finance_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"customer_id": "C00001", "account_id": "A00001", "facility_id": "F00001", "reporting_date": REFERENCE_DATE, "exposure": 100_100.0, "provision": 900.0, "ifrs9_stage": 1, "currency": "EUR", "product": "Mortgage", "legal_entity": "Synthetic Bank EU", "model_version": "PD-v1.0"},
            {"customer_id": "C00002", "account_id": "A00002", "facility_id": "F00002", "reporting_date": REFERENCE_DATE, "exposure": 88_500.0, "provision": 1_600.0, "ifrs9_stage": 2, "currency": "EUR", "product": "SME", "legal_entity": "Synthetic Bank EU", "model_version": "PD-v1.0"},
            {"customer_id": "C00005", "account_id": "A00005", "facility_id": "F00005", "reporting_date": REFERENCE_DATE, "exposure": 35_000.0, "provision": 700.0, "ifrs9_stage": 1, "currency": "EUR", "product": "Mortgage", "legal_entity": "Synthetic Bank EU", "model_version": "PD-v1.0"},
            {"customer_id": "C00004", "account_id": "A00004", "facility_id": "F00004", "reporting_date": REFERENCE_DATE, "exposure": 40_000.0, "provision": 600.0, "ifrs9_stage": 1, "currency": "EUR", "product": "Credit Card", "legal_entity": "Synthetic Bank EU", "model_version": "PD-v1.0"},
        ]
    )


def intentional_defects() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("Missing income", "Four of twelve borrowers have missing income, approximating a 33% defect rate."),
            ("Duplicate customer ID", "One customer identifier is repeated in the defective portfolio."),
            ("Invalid PD/LGD/EAD", "Records include PD below 0, PD above 1, LGD above 1, and negative EAD."),
            ("Stale collateral", "One collateral valuation is older than the control threshold."),
            ("Reconciliation", "Risk and Finance exposure views contain both value differences and unmatched records."),
        ],
        columns=["defect", "description"],
    )
