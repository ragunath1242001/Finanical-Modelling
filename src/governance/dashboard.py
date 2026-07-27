"""Reusable assembly of Phase 4 governance demo state."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.data.synthetic_governance import defective_portfolio, finance_dataset, risk_dataset
from src.governance.data_quality import create_issues_for_failed_controls, execute_controls
from src.governance.impact_analysis import missing_income_sensitivity
from src.governance.issues import issues_to_frame
from src.governance.models import GovernanceIssue
from src.governance.reconciliation import ReconciliationResult, reconcile_risk_finance
from src.reporting.governance_reporting import governance_kpis


@dataclass(frozen=True)
class GovernanceDashboardState:
    portfolio: pd.DataFrame
    control_results: list
    issues: list[GovernanceIssue]
    reconciliation: ReconciliationResult
    sensitivity: dict[str, float | str]
    kpis: dict[str, float | int | str]


def build_governance_dashboard_state(base_cet1: float, base_rwa: float) -> GovernanceDashboardState:
    portfolio = defective_portfolio()
    results = execute_controls(portfolio)
    issues = create_issues_for_failed_controls(results)
    reconciliation = reconcile_risk_finance(risk_dataset(), finance_dataset())
    sensitivity = missing_income_sensitivity(portfolio, base_cet1, base_rwa)
    kpis = governance_kpis(results, issues, reconciliation)
    return GovernanceDashboardState(portfolio, results, issues, reconciliation, sensitivity, kpis)


def issues_frame_for_state(state: GovernanceDashboardState) -> pd.DataFrame:
    return issues_to_frame(state.issues)
