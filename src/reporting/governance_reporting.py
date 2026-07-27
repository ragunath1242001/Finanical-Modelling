"""Governance reporting summaries for executive and regulatory pages."""

from __future__ import annotations

import pandas as pd

from src.governance.models import ControlExecutionResult, ControlStatus, GovernanceIssue, IssueStatus, Severity
from src.governance.reconciliation import ReconciliationResult
from src.reporting.model_risk_reporting import model_risk_readiness_label


def governance_kpis(results: list[ControlExecutionResult], issues: list[GovernanceIssue], reconciliation: ReconciliationResult) -> dict[str, float | int | str]:
    failed_controls = [result for result in results if result.status == ControlStatus.FAIL]
    open_issues = [issue for issue in issues if issue.status != IssueStatus.CLOSED]
    high_issues = [issue for issue in open_issues if issue.severity in {Severity.HIGH, Severity.CRITICAL}]
    overdue = [issue for issue in open_issues if issue.status == IssueStatus.OVERDUE]
    pending_2lod = [issue for issue in open_issues if issue.status == IssueStatus.PENDING_2LOD_REVIEW]
    ecl_impact = sum(issue.financial_impact for issue in open_issues)
    return {
        "controls_executed": len(results),
        "controls_failed": len(failed_controls),
        "records_tested": sum(result.records_tested for result in results),
        "failed_records": sum(result.records_failed for result in results),
        "open_issues": len(open_issues),
        "high_or_critical_issues": len(high_issues),
        "overdue_issues": len(overdue),
        "pending_2lod_closures": len(pending_2lod),
        "risk_finance_difference": reconciliation.summary.total_difference,
        "models_affected": len({issue.affected_model for issue in open_issues}),
        "reports_affected": len({issue.affected_report for issue in open_issues}),
        "illustrative_ecl_impact": ecl_impact,
        "illustrative_cet1_impact": -0.75 * ecl_impact,
        "reconciliation_status": reconciliation.summary.status,
    }


def reporting_readiness(results: list[ControlExecutionResult], issues: list[GovernanceIssue], reconciliation: ReconciliationResult) -> dict[str, str]:
    critical_open = any(issue.status != IssueStatus.CLOSED and issue.severity == Severity.CRITICAL for issue in issues)
    failed_material = any(result.status == ControlStatus.FAIL and result.severity in {Severity.HIGH, Severity.CRITICAL} for result in results)
    if critical_open or reconciliation.summary.material_differences > 0:
        status = "Under review"
    elif failed_material:
        status = "Ready with limitations"
    else:
        status = "Ready"
    if critical_open:
        sign_off = "Not ready"
    elif failed_material or reconciliation.summary.explanation_required:
        sign_off = "Ready with limitations"
    else:
        sign_off = "Ready"
    return {
        "reconciliation_status": reconciliation.summary.status,
        "report_production_readiness": status,
        "sign_off_status": sign_off,
        "model_risk_readiness": model_risk_readiness_label(),
        "open_control_failures": str(sum(result.status == ControlStatus.FAIL for result in results)),
        "affected_data_elements": ", ".join(sorted({element for result in results if result.status == ControlStatus.FAIL for element in result.affected_data_elements})),
    }


def executive_governance_narrative(kpis: dict[str, float | int | str]) -> str:
    issue_count = int(kpis["open_issues"])
    high = int(kpis["high_or_critical_issues"])
    pending = int(kpis["pending_2lod_closures"])
    if issue_count == 0:
        return "No open data-quality issues are currently blocking the educational executive view."
    return (
        f"{high} high or critical data-quality issues remain open across {issue_count} total issues. "
        f"Failed controls affect {kpis['models_affected']} model area(s) and {kpis['reports_affected']} report area(s). "
        f"{pending} remediation package(s) are awaiting 2LOD review. "
        "The financial impact is an illustrative sensitivity, not a definitive accounting adjustment."
    )


def governance_kpis_frame(kpis: dict[str, float | int | str]) -> pd.DataFrame:
    return pd.DataFrame([{"metric": key, "value": value} for key, value in kpis.items()])
