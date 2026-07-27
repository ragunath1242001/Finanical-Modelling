"""Governance issue creation and lifecycle validation."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from src.governance.models import (
    ControlExecutionResult,
    GovernanceError,
    GovernanceIssue,
    IssueStatus,
    Severity,
)


def issue_from_control_result(result: ControlExecutionResult) -> GovernanceIssue:
    if not result.owner:
        raise GovernanceError("A failed control must have an accountable issue owner.")
    due_days = 7 if result.severity in {Severity.CRITICAL, Severity.HIGH} else 30
    impact_value = float(result.records_failed) * 1_000.0
    return GovernanceIssue(
        issue_id=f"ISS-{result.control_id}",
        title=result.control_name,
        description=f"{result.records_failed} of {result.records_tested} records failed {result.control_name}.",
        source_control=result.control_id,
        severity=result.severity,
        status=IssueStatus.OPEN,
        detected_date=date(2026, 7, 27),
        due_date=date(2026, 7, 27) + timedelta(days=due_days),
        owner=result.owner,
        data_owner="Business Owner",
        data_steward="1LOD Data Steward",
        affected_model=result.downstream_impact.split(",")[0] if result.downstream_impact else "Risk aggregation",
        affected_report="COREP/FINREP-style reporting",
        financial_impact=impact_value,
        regulatory_impact="May limit confidence in educational regulatory reporting outputs.",
        affected_population=f"{result.records_failed} failed records",
    )


def validate_issue(issue: GovernanceIssue) -> None:
    if not issue.issue_id:
        raise GovernanceError("Issue ID is required.")
    if not issue.owner or not issue.data_owner or not issue.data_steward:
        raise GovernanceError("Issue requires owner, data owner and data steward.")
    if issue.due_date < issue.detected_date:
        raise GovernanceError("Issue due date cannot be before detected date.")


def is_overdue(issue: GovernanceIssue, as_of: date | None = None) -> bool:
    as_of = as_of or date(2026, 7, 27)
    return issue.status not in {IssueStatus.CLOSED} and issue.due_date < as_of


def closure_requirements_met(issue: GovernanceIssue, material_requires_2lod: bool = True) -> tuple[bool, list[str]]:
    missing = []
    if not issue.root_cause:
        missing.append("root cause")
    if not issue.affected_population:
        missing.append("affected population")
    if issue.financial_impact is None:
        missing.append("financial impact")
    if not issue.remediation_plan:
        missing.append("remediation plan")
    if not issue.preventive_control:
        missing.append("preventive control")
    if not issue.closure_evidence:
        missing.append("closure evidence")
    if material_requires_2lod and issue.severity in {Severity.HIGH, Severity.CRITICAL} and not issue.two_lod_approved:
        missing.append("2LOD approval")
    return not missing, missing


def issues_to_frame(issues: list[GovernanceIssue]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "issue_id": issue.issue_id,
                "title": issue.title,
                "severity": issue.severity.value,
                "status": issue.status.value,
                "owner": issue.owner,
                "data_owner": issue.data_owner,
                "data_steward": issue.data_steward,
                "due_date": issue.due_date.isoformat(),
                "affected_model": issue.affected_model,
                "affected_report": issue.affected_report,
                "financial_impact": issue.financial_impact,
                "regulatory_impact": issue.regulatory_impact,
                "root_cause": issue.root_cause,
                "remediation_plan": issue.remediation_plan,
                "closure_evidence": ", ".join(issue.closure_evidence),
                "2lod_conclusion": issue.two_lod_conclusion,
                "audit_status": issue.audit_status,
            }
            for issue in issues
        ]
    )
