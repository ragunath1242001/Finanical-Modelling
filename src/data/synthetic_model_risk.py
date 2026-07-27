"""Deterministic synthetic model-risk datasets."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from src.model_risk.models import (
    ApprovalDecision,
    ApprovalDecisionType,
    DevelopmentEvidence,
    FindingSeverity,
    FindingStatus,
    LifecycleStatus,
    Limitation,
    ModelFamily,
    ModelRecord,
    ModelTier,
    UseRestriction,
    ValidationAssessment,
    ValidationFinding,
    ValidationOutcome,
    Rating,
)


AS_OF_DATE = date(2026, 7, 27)


def synthetic_model_inventory() -> list[ModelRecord]:
    return [
        ModelRecord("PD-LOGIT-001", "Retail PD logistic model", "1.0", ModelFamily.PD, "Binary classification", "Estimate borrower default probability for credit risk learning.", "Credit Risk Model Owner", "Model Developer A", "Independent Validator A", "Credit Risk", "Synthetic Bank EU", "EU", "IFRS 9, IRB and stress-testing input", 9.0, ModelTier.TIER_1, LifecycleStatus.UNDER_MONITORING, date(2025, 1, 15), date(2026, 1, 20), date(2026, 12, 31), "Monthly", ["customers", "loans"], ["pd", "risk_grade"], ["Loan Origination System"], ["IFRS 9 ECL Engine", "Stress Testing"], ["FINREP", "COREP"], ["MRF-001"], ["Synthetic data only"], [], ApprovalDecisionType.APPROVED),
        ModelRecord("PD-GBM-CHAL-002", "Gradient boosting PD challenger", "0.9", ModelFamily.PD, "Binary classification", "Compare challenger against champion PD model.", "Credit Risk Model Owner", "Model Developer B", "Independent Validator A", "Credit Risk", "Synthetic Bank EU", "EU", "Challenger evidence only", 7.0, ModelTier.TIER_2, LifecycleStatus.PENDING_VALIDATION, date(2026, 4, 1), date(2026, 5, 1), date(2026, 9, 30), "Monthly", ["customers", "loans"], ["pd"], ["Credit Risk Data Mart"], ["Model Risk"], ["Model card"], [], ["Challenger model only"], ["challenger model only"], ApprovalDecisionType.DEFERRED),
        ModelRecord("LGD-COLL-001", "Collateral LGD model", "1.0", ModelFamily.LGD, "Analytical model", "Estimate loss severity using collateral and recovery assumptions.", "LGD Model Owner", "Model Developer C", "Independent Validator B", "Credit Risk", "Synthetic Bank EU", "EU", "IFRS 9 and IRB input", 8.0, ModelTier.TIER_1, LifecycleStatus.PERFORMANCE_CONCERN, date(2025, 3, 1), date(2025, 8, 1), date(2026, 6, 30), "Monthly", ["loans", "collateral"], ["lgd"], ["Collateral System"], ["IFRS 9 ECL Engine", "IRB"], ["FINREP", "COREP"], ["DQ-010"], ["Stale collateral sensitivity"], ["restricted portfolio segment"], ApprovalDecisionType.CONDITIONALLY_APPROVED),
        ModelRecord("FRD-GBM-001", "Fraud alert classifier", "1.0", ModelFamily.FRAUD, "Binary classification", "Rank synthetic transactions for fraud alert review.", "Financial Crime Owner", "Model Developer D", "Independent Validator C", "Financial Crime", "Synthetic Bank EU", "EU", "Operational monitoring", 6.0, ModelTier.TIER_2, LifecycleStatus.USE_RESTRICTED, date(2025, 7, 1), date(2026, 1, 1), date(2026, 8, 31), "Weekly", ["transactions"], ["fraud_probability"], ["Transaction Monitoring"], ["Fraud Alert Queue"], ["Management dashboard"], ["MRF-002"], ["High false-positive rate"], ["manual override required"], ApprovalDecisionType.CONDITIONALLY_APPROVED),
        ModelRecord("FIN-FCST-001", "Finance baseline forecast", "1.0", ModelFamily.FORECASTING, "Time-series regression", "Forecast balances, provisions and alert volumes.", "Finance Planning Owner", "Model Developer E", "Independent Validator D", "Finance", "Synthetic Bank EU", "EU", "Planning and management information", 4.0, ModelTier.TIER_3, LifecycleStatus.UNDER_MONITORING, date(2025, 10, 1), date(2026, 2, 1), date(2027, 2, 1), "Monthly", ["financials"], ["forecast_balance", "forecast_provision"], ["Finance Data Mart"], ["Executive Overview"], ["Planning pack"], [], ["Simple trend model"], [], ApprovalDecisionType.APPROVED),
        ModelRecord("AML-RULE-001", "AML typology rule set", "1.0", ModelFamily.AML, "Rule-based monitoring", "Flag synthetic AML typologies for educational investigation.", "Financial Crime Owner", "Rule Developer", "Independent Compliance Reviewer", "Financial Crime", "Synthetic Bank EU", "EU", "AML educational monitoring", 5.0, ModelTier.TIER_2, LifecycleStatus.IN_PRODUCTION, date(2025, 6, 1), date(2026, 3, 1), date(2027, 3, 1), "Monthly", ["transactions"], ["aml_alert"], ["Transaction Monitoring"], ["AML Queue"], ["Financial crime report"], [], ["Rules are simplified"], [], ApprovalDecisionType.APPROVED),
        ModelRecord("PD-LOGIT-OLD", "Retail PD logistic model", "0.8", ModelFamily.PD, "Binary classification", "Retired previous PD model version.", "Credit Risk Model Owner", "Model Developer A", "Independent Validator A", "Credit Risk", "Synthetic Bank EU", "EU", "Retired historical version", 8.0, ModelTier.TIER_1, LifecycleStatus.RETIRED, date(2024, 1, 1), date(2024, 10, 1), date(2025, 10, 1), "Monthly", ["customers", "loans"], ["pd"], ["Loan Origination System"], ["Retired"], ["Model archive"], [], ["Retired after champion update"], [], ApprovalDecisionType.APPROVED, retirement_date=date(2025, 1, 15)),
    ]


def synthetic_development_evidence() -> list[DevelopmentEvidence]:
    return [
        DevelopmentEvidence("PD-LOGIT-001", "1.0", "Logistic regression with train/test split", "Estimate one-year default probability", "Synthetic retail and SME borrowers", "Synthetic default flag", "2024-2025", ["income", "credit_score", "debt_to_income", "ltv", "days_past_due"], ["Post-default fields"], "Median imputation", "Winsorised educational examples", ["standard scaling"], "Business and predictive relevance", "LogisticRegression", {"class_weight": "balanced"}, "Calibration curve reviewed", "Retail/SME combined", ["Synthetic data"], ["Not production underwriting"], {"auc": 0.79, "brier_score": 0.11}, {"psi": 0.08}, {"top_feature": "days_past_due"}, ["unit tests", "reproducible seed"], "Developer sign-off complete"),
        DevelopmentEvidence("PD-GBM-CHAL-002", "0.9", "Gradient boosting challenger", "Improve ranking performance", "Same champion evaluation population", "Synthetic default flag", "2024-2025", ["income", "credit_score", "debt_to_income", "ltv", "days_past_due"], ["Post-default fields"], "Median imputation", "Tree robustness", ["tree splits"], "Predictive contribution", "GradientBoostingClassifier", {"random_state": 7}, "Calibration weaker than champion", "Retail/SME combined", ["Higher complexity"], ["Challenger only"], {"auc": 0.83, "brier_score": 0.15}, {"psi": 0.16}, {"top_feature": "days_past_due"}, ["parallel-run checks"], "Developer sign-off complete"),
    ]


def synthetic_validation_assessments() -> list[ValidationAssessment]:
    return [
        ValidationAssessment("PD-LOGIT-001", "1.0", "Calibration", Rating.RED, ValidationOutcome.PASS_WITH_CONDITIONS, "Observed default rate above predicted in upper bands.", "Calibration deterioration", FindingSeverity.HIGH, "Apply use limitation and revalidate calibration.", "Conditionally acceptable with monitoring escalation."),
        ValidationAssessment("PD-LOGIT-001", "1.0", "Discrimination", Rating.GREEN, ValidationOutcome.PASS, "AUC and Gini within educational tolerance.", "", FindingSeverity.LOW, "Continue monthly monitoring.", "Acceptable."),
        ValidationAssessment("LGD-COLL-001", "1.0", "Data quality", Rating.RED, ValidationOutcome.FAIL, "Stale collateral valuations detected.", "Collateral data freshness breach", FindingSeverity.HIGH, "Refresh collateral values and rerun LGD sensitivity.", "Not acceptable until remediation."),
        ValidationAssessment("FRD-GBM-001", "1.0", "Performance", Rating.AMBER, ValidationOutcome.PASS_WITH_CONDITIONS, "High false-positive rate.", "Alert burden high", FindingSeverity.HIGH, "Manual review and threshold recalibration.", "Conditional use."),
    ]


def synthetic_findings() -> list[ValidationFinding]:
    return [
        ValidationFinding("MRF-001", "PD-LOGIT-001", "1.0", "Calibration", "PD calibration deterioration", "Upper score bands under-predict observed default rate.", FindingSeverity.HIGH, "Recalibrate and run independent validation.", "Credit Risk Model Owner", AS_OF_DATE + timedelta(days=30), FindingStatus.OPEN, linked_governance_issue="ISS-MRF-001"),
        ValidationFinding("MRF-002", "FRD-GBM-001", "1.0", "Performance", "Fraud false-positive rate high", "Alert queue burden exceeds operational tolerance.", FindingSeverity.HIGH, "Tune threshold and validate precision/recall tradeoff.", "Financial Crime Owner", AS_OF_DATE + timedelta(days=45), FindingStatus.IN_REMEDIATION, linked_governance_issue="ISS-MRF-002"),
        ValidationFinding("MRF-003", "LGD-COLL-001", "1.0", "Data quality", "Stale collateral values", "LGD inputs depend on collateral valuations older than policy threshold.", FindingSeverity.HIGH, "Refresh collateral data before unrestricted use.", "LGD Model Owner", AS_OF_DATE - timedelta(days=5), FindingStatus.OPEN, linked_governance_issue="ISS-DQ-010"),
    ]


def synthetic_approvals() -> list[ApprovalDecision]:
    return [
        ApprovalDecision("APP-PD-001", "PD-LOGIT-001", "1.0", ApprovalDecisionType.CONDITIONALLY_APPROVED, date(2026, 1, 25), "Model Risk Committee", ["Monthly calibration monitoring"], ["manual override required for high-risk segments"], date(2026, 10, 31), ["Recalibration evidence"], date(2026, 9, 30)),
        ApprovalDecision("APP-LGD-001", "LGD-COLL-001", "1.0", ApprovalDecisionType.CONDITIONALLY_APPROVED, date(2025, 8, 15), "Model Risk Committee", ["Collateral refresh"], ["restricted portfolio segment"], date(2026, 6, 30), ["Refresh stale valuations"], date(2026, 7, 31)),
        ApprovalDecision("APP-FRD-001", "FRD-GBM-001", "1.0", ApprovalDecisionType.CONDITIONALLY_APPROVED, date(2026, 2, 1), "Financial Crime Governance", ["Manual review"], ["manual override required"], date(2026, 8, 31), ["Threshold recalibration"], date(2026, 8, 15)),
        ApprovalDecision("APP-FCST-001", "FIN-FCST-001", "1.0", ApprovalDecisionType.APPROVED, date(2026, 2, 10), "Finance Model Owner", [], [], None, [], date(2027, 2, 1)),
    ]


def synthetic_restrictions() -> list[UseRestriction]:
    return [
        UseRestriction("RES-PD-001", "PD-LOGIT-001", "1.0", "Manual override required", "Calibration deterioration in upper risk bands.", AS_OF_DATE, date(2026, 10, 31), "Model Risk Manager", "MRF-001", "ISS-MRF-001", True),
        UseRestriction("RES-LGD-001", "LGD-COLL-001", "1.0", "Restricted portfolio segment", "Stale collateral inputs affect secured exposures.", AS_OF_DATE, date(2026, 9, 30), "Model Risk Manager", "MRF-003", "ISS-DQ-010", True),
        UseRestriction("RES-CHAL-001", "PD-GBM-CHAL-002", "0.9", "Challenger model only", "Better AUC but weaker calibration and stability.", AS_OF_DATE, None, "Independent Validator", "", "", True),
    ]


def synthetic_limitations() -> list[Limitation]:
    return [
        Limitation("LIM-PD-001", "PD-LOGIT-001", "1.0", "Synthetic data only and calibration deterioration in high-risk bands.", "calibration", FindingSeverity.HIGH, "High-risk borrowers", "IFRS 9 ECL uncertainty", "Manual override and monthly monitoring", "Credit Risk Model Owner", date(2026, 10, 31), "Open", "MRF-001", "ISS-MRF-001"),
        Limitation("LIM-LGD-001", "LGD-COLL-001", "1.0", "Collateral valuations may be stale.", "data", FindingSeverity.HIGH, "Secured exposures", "LGD may be understated", "Collateral refresh control", "LGD Model Owner", date(2026, 6, 30), "Expired", "MRF-003", "ISS-DQ-010"),
    ]


def synthetic_monitoring_history() -> pd.DataFrame:
    months = pd.date_range("2026-01-31", periods=7, freq="ME")
    return pd.DataFrame(
        {
            "date": months,
            "model_id": ["PD-LOGIT-001"] * 7,
            "auc": [0.80, 0.79, 0.78, 0.77, 0.75, 0.73, 0.71],
            "brier_score": [0.10, 0.105, 0.11, 0.12, 0.13, 0.15, 0.17],
            "calibration_error": [0.02, 0.025, 0.03, 0.045, 0.06, 0.08, 0.10],
            "psi": [0.04, 0.05, 0.08, 0.12, 0.16, 0.22, 0.31],
            "missing_income_rate": [0.03, 0.04, 0.05, 0.08, 0.12, 0.18, 0.30],
            "override_rate": [0.02, 0.02, 0.03, 0.04, 0.06, 0.07, 0.09],
        }
    )


def synthetic_score_samples(seed: int = 7) -> tuple[pd.Series, pd.Series]:
    rng = np.random.default_rng(seed)
    reference = pd.Series(rng.beta(2, 18, size=500))
    current = pd.Series(rng.beta(2.8, 13, size=500))
    return reference, current


def synthetic_champion_challenger() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"model_id": "PD-LOGIT-001", "role": "Champion", "auc": 0.79, "brier_score": 0.11, "psi": 0.08, "complexity_score": 2, "explainability_score": 9, "operational_cost": 3},
            {"model_id": "PD-GBM-CHAL-002", "role": "Challenger", "auc": 0.83, "brier_score": 0.15, "psi": 0.16, "complexity_score": 7, "explainability_score": 5, "operational_cost": 6},
        ]
    )
