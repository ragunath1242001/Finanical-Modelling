from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from src.data.synthetic_governance import clean_portfolio, defective_portfolio, finance_dataset, risk_dataset
from src.governance.audit import audit_events_chronological
from src.governance.data_quality import create_issues_for_failed_controls, execute_controls, results_to_frame
from src.governance.impact_analysis import missing_income_sensitivity
from src.governance.issues import closure_requirements_met, is_overdue
from src.governance.lineage import LINEAGE_STEPS, controls_for_node, downstream_lineage
from src.governance.lod_workflows import LODRole, ROLE_DEFINITIONS, submit_closure_package, transition_issue
from src.governance.models import GovernanceError, IssueStatus
from src.governance.reconciliation import ReconciliationConfig, classify_difference, reconcile_risk_finance
from src.reporting.governance_reporting import governance_kpis, reporting_readiness


def _result(results, control_id):
    return next(result for result in results if result.control_id == control_id)


def test_required_controls_detect_defects_and_clean_dataset_passes():
    defective_results = execute_controls(defective_portfolio())
    assert _result(defective_results, "DQ-001").records_failed == 4
    assert _result(defective_results, "DQ-003").records_failed == 2
    assert _result(defective_results, "DQ-004").records_failed == 2
    assert _result(defective_results, "DQ-006").records_failed == 1
    assert _result(defective_results, "DQ-010").records_failed == 1
    assert _result(defective_results, "DQ-013").records_failed == 1

    clean_results = execute_controls(clean_portfolio())
    assert results_to_frame(clean_results)["status"].eq("Pass").all()


def test_failed_material_controls_create_owned_issues():
    issues = create_issues_for_failed_controls(execute_controls(defective_portfolio()))
    assert issues
    assert all(issue.owner for issue in issues)
    assert any(issue.severity.value in {"High", "Critical"} for issue in issues)


def test_workflow_transitions_and_closure_rules():
    issue = submit_closure_package(create_issues_for_failed_controls(execute_controls(defective_portfolio()))[0])
    issue, action, event = transition_issue(issue, IssueStatus.ACKNOWLEDGED, LODRole.FIRST_LINE_DATA_STEWARD)
    assert action.previous_status == IssueStatus.OPEN
    assert issue.status == IssueStatus.ACKNOWLEDGED
    assert event.new_value == "Acknowledged"

    with pytest.raises(GovernanceError):
        issue.status = IssueStatus.OPEN
        transition_issue(issue, IssueStatus.CLOSED, LODRole.FIRST_LINE_DATA_STEWARD)

    issue.status = IssueStatus.PENDING_2LOD_REVIEW
    closed, _, _ = transition_issue(issue, IssueStatus.CLOSED, LODRole.SECOND_LINE_DATA_GOVERNANCE, comment="Accepted")
    assert closed.status == IssueStatus.CLOSED
    assert closed.two_lod_approved is True


def test_2lod_rejection_returns_to_remediation_and_1lod_cannot_approve():
    issue = submit_closure_package(create_issues_for_failed_controls(execute_controls(defective_portfolio()))[0])
    issue.status = IssueStatus.PENDING_2LOD_REVIEW
    rejected, _, _ = transition_issue(issue, IssueStatus.REJECTED_BY_2LOD, LODRole.SECOND_LINE_DATA_GOVERNANCE)
    assert rejected.status == IssueStatus.REJECTED_BY_2LOD
    remediating, _, _ = transition_issue(rejected, IssueStatus.IN_PROGRESS, LODRole.FIRST_LINE_DATA_STEWARD)
    assert remediating.status == IssueStatus.IN_PROGRESS
    remediating.status = IssueStatus.PENDING_2LOD_REVIEW
    with pytest.raises(GovernanceError):
        transition_issue(remediating, IssueStatus.CLOSED, LODRole.FIRST_LINE_DATA_STEWARD)


def test_closed_material_issue_requires_evidence_and_2lod_approval():
    issue = create_issues_for_failed_controls(execute_controls(defective_portfolio()))[0]
    ok, missing = closure_requirements_met(issue)
    assert ok is False
    assert "closure evidence" in missing
    assert "2LOD approval" in missing


def test_overdue_and_missing_owner_validation():
    issue = create_issues_for_failed_controls(execute_controls(defective_portfolio()))[0]
    issue.due_date = issue.detected_date - timedelta(days=1)
    assert is_overdue(issue, issue.detected_date)
    issue.owner = ""
    with pytest.raises(GovernanceError):
        transition_issue(issue, IssueStatus.ACKNOWLEDGED, LODRole.FIRST_LINE_DATA_STEWARD)


def test_audit_events_chronological():
    base = datetime(2026, 7, 27, tzinfo=timezone.utc)
    issue = submit_closure_package(create_issues_for_failed_controls(execute_controls(defective_portfolio()))[0])
    issue, _, event1 = transition_issue(issue, IssueStatus.ACKNOWLEDGED, LODRole.FIRST_LINE_DATA_STEWARD, timestamp=base)
    issue, _, event2 = transition_issue(issue, IssueStatus.UNDER_INVESTIGATION, LODRole.FIRST_LINE_DATA_STEWARD, timestamp=base + timedelta(minutes=1))
    assert audit_events_chronological([event1, event2])


def test_reconciliation_detects_material_and_unmatched_records():
    result = reconcile_risk_finance(risk_dataset(), finance_dataset())
    assert result.summary.matched_records == 3
    assert result.summary.unmatched_risk_records == 1
    assert result.summary.unmatched_finance_records == 1
    assert result.summary.material_differences >= 1
    assert result.summary.explanation_required is True
    assert round(result.summary.total_difference, 2) == round(result.details["difference"].sum(), 2)


def test_reconciliation_within_tolerance_and_classification():
    risk = pd.DataFrame([{"customer_id": "C1", "account_id": "A1", "facility_id": "F1", "reporting_date": "2026-07-27", "exposure": 100.0, "provision": 2.0}])
    finance = pd.DataFrame([{"customer_id": "C1", "account_id": "A1", "facility_id": "F1", "reporting_date": "2026-07-27", "exposure": 100.5, "provision": 2.0}])
    result = reconcile_risk_finance(risk, finance, ReconciliationConfig(tolerance=1.0))
    assert result.details["reconciliation_status"].eq("Matched").all()
    assert classify_difference(25_000, ReconciliationConfig()) == "Critical"


def test_impact_sensitivity_blocks_invalid_records_and_links_financial_chain():
    sensitivity = missing_income_sensitivity(defective_portfolio(), cet1=8_500_000, rwa=50_000_000)
    assert sensitivity["missing_income_rate"] > 0
    assert sensitivity["conservative_ecl"] >= sensitivity["base_ecl"]
    assert sensitivity["cet1_impact"] <= 0


def test_high_severity_issue_appears_in_executive_metrics():
    results = execute_controls(defective_portfolio())
    issues = create_issues_for_failed_controls(results)
    reconciliation = reconcile_risk_finance(risk_dataset(), finance_dataset())
    kpis = governance_kpis(results, issues, reconciliation)
    assert kpis["high_or_critical_issues"] > 0
    assert kpis["open_issues"] == len(issues)
    readiness = reporting_readiness(results, issues, reconciliation)
    assert readiness["sign_off_status"] in {"Ready with limitations", "Not ready"}


def test_lineage_and_role_catalogues_are_complete_for_ui():
    assert "IFRS 9 ECL Engine" in LINEAGE_STEPS
    assert controls_for_node("RDM")
    assert downstream_lineage("RDM")
    assert {role.value for role in LODRole} == set(ROLE_DEFINITIONS[role] and role.value for role in LODRole)
