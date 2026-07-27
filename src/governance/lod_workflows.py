"""1LOD/2LOD/3LOD educational workflow engine."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from src.governance.audit import make_audit_event
from src.governance.issues import closure_requirements_met, validate_issue
from src.governance.models import (
    ActionType,
    AuditEvent,
    GovernanceError,
    GovernanceIssue,
    IssueStatus,
    LODRole,
    Severity,
    WorkflowAction,
)


ROLE_DEFINITIONS = {
    LODRole.FIRST_LINE_DATA_STEWARD: "Owns and manages data-quality remediation in the business process.",
    LODRole.FIRST_LINE_MODEL_OWNER: "Owns model operation and assesses model-input or output impact.",
    LODRole.SECOND_LINE_DATA_GOVERNANCE: "Provides independent oversight and challenge of data controls and closure evidence.",
    LODRole.SECOND_LINE_MODEL_RISK: "Challenges model impact, parameter reliability and use restrictions.",
    LODRole.THIRD_LINE_INTERNAL_AUDIT: "Provides independent assurance over governance, risk management and internal controls.",
    LODRole.EXECUTIVE_COMMITTEE: "Reviews material issues, overdue remediation and reporting readiness.",
}


ALLOWED_TRANSITIONS = {
    IssueStatus.OPEN: {IssueStatus.ACKNOWLEDGED},
    IssueStatus.ACKNOWLEDGED: {IssueStatus.UNDER_INVESTIGATION},
    IssueStatus.UNDER_INVESTIGATION: {IssueStatus.IMPACT_ASSESSMENT},
    IssueStatus.IMPACT_ASSESSMENT: {IssueStatus.REMEDIATION_PLANNED},
    IssueStatus.REMEDIATION_PLANNED: {IssueStatus.IN_PROGRESS},
    IssueStatus.IN_PROGRESS: {IssueStatus.PENDING_2LOD_REVIEW},
    IssueStatus.PENDING_2LOD_REVIEW: {IssueStatus.CLOSED, IssueStatus.REJECTED_BY_2LOD},
    IssueStatus.REJECTED_BY_2LOD: {IssueStatus.IN_PROGRESS},
    IssueStatus.CLOSED: {IssueStatus.AUDIT_REVIEW},
    IssueStatus.OVERDUE: {IssueStatus.IN_PROGRESS},
    IssueStatus.AUDIT_REVIEW: set(),
}


FIRST_LINE_ROLES = {LODRole.FIRST_LINE_DATA_STEWARD, LODRole.FIRST_LINE_MODEL_OWNER}
SECOND_LINE_ROLES = {LODRole.SECOND_LINE_DATA_GOVERNANCE, LODRole.SECOND_LINE_MODEL_RISK}
THIRD_LINE_ROLES = {LODRole.THIRD_LINE_INTERNAL_AUDIT}


def _action_for_transition(new_status: IssueStatus) -> ActionType:
    return {
        IssueStatus.ACKNOWLEDGED: ActionType.ACKNOWLEDGE,
        IssueStatus.UNDER_INVESTIGATION: ActionType.INVESTIGATE,
        IssueStatus.IMPACT_ASSESSMENT: ActionType.ASSESS_IMPACT,
        IssueStatus.REMEDIATION_PLANNED: ActionType.PLAN_REMEDIATION,
        IssueStatus.IN_PROGRESS: ActionType.UPDATE_PROGRESS,
        IssueStatus.PENDING_2LOD_REVIEW: ActionType.SUBMIT_2LOD,
        IssueStatus.CLOSED: ActionType.ACCEPT_CLOSURE,
        IssueStatus.REJECTED_BY_2LOD: ActionType.REJECT_CLOSURE,
        IssueStatus.AUDIT_REVIEW: ActionType.AUDIT_OBSERVATION,
    }.get(new_status, ActionType.UPDATE_PROGRESS)


def transition_issue(
    issue: GovernanceIssue,
    new_status: IssueStatus,
    actor_role: LODRole,
    actor_name: str = "Synthetic role user",
    comment: str = "",
    evidence_reference: str = "",
    timestamp: datetime | None = None,
) -> tuple[GovernanceIssue, WorkflowAction, AuditEvent]:
    validate_issue(issue)
    if new_status not in ALLOWED_TRANSITIONS[issue.status]:
        raise GovernanceError(f"Invalid transition from {issue.status.value} to {new_status.value}.")
    if issue.status == IssueStatus.OPEN and new_status == IssueStatus.CLOSED:
        raise GovernanceError("Open issues cannot move directly to Closed.")
    if new_status == IssueStatus.PENDING_2LOD_REVIEW and not issue.remediation_plan:
        raise GovernanceError("Pending 2LOD Review requires a remediation plan.")
    if new_status == IssueStatus.CLOSED:
        if actor_role not in SECOND_LINE_ROLES:
            raise GovernanceError("Only 2LOD can provide final closure approval for material issues.")
        issue.two_lod_approved = True
        issue.two_lod_conclusion = comment or "Closure accepted by 2LOD."
        ok, missing = closure_requirements_met(issue, material_requires_2lod=True)
        if not ok:
            raise GovernanceError("Closed issue requires " + ", ".join(missing) + ".")
    if new_status == IssueStatus.REJECTED_BY_2LOD and actor_role not in SECOND_LINE_ROLES:
        raise GovernanceError("Only 2LOD can reject a closure submission.")
    if new_status == IssueStatus.AUDIT_REVIEW and actor_role not in THIRD_LINE_ROLES:
        raise GovernanceError("Only 3LOD can move an issue into Audit Review.")

    previous = issue.status
    issue.status = new_status
    timestamp = timestamp or datetime.now(timezone.utc)
    action = WorkflowAction(
        action_id=f"ACT-{issue.issue_id}-{timestamp.strftime('%Y%m%d%H%M%S')}",
        issue_id=issue.issue_id,
        actor_role=actor_role,
        actor_name=actor_name,
        action_type=_action_for_transition(new_status),
        timestamp=timestamp,
        comment=comment,
        previous_status=previous,
        new_status=new_status,
        evidence_reference=evidence_reference,
    )
    audit_event = make_audit_event(
        event_id=action.action_id,
        user_role=actor_role.value,
        module="BCBS 239 Governance",
        object_type="GovernanceIssue",
        object_id=issue.issue_id,
        action=action.action_type.value,
        previous_value=previous.value,
        new_value=new_status.value,
        reason=comment,
        approval_status="Accepted" if new_status == IssueStatus.CLOSED else "",
        timestamp=timestamp,
    )
    return issue, action, audit_event


def submit_closure_package(issue: GovernanceIssue) -> GovernanceIssue:
    issue.root_cause = issue.root_cause or "Source-system feed did not enforce mandatory field validation."
    issue.affected_population = issue.affected_population or "Failed population identified by control sample."
    issue.remediation_plan = issue.remediation_plan or "Correct source records, add preventive validation and rerun the control."
    issue.preventive_control = issue.preventive_control or "Mandatory-field and range check before reporting load."
    issue.closure_evidence = issue.closure_evidence or ["EV-ROOT-CAUSE", "EV-CONTROL-RERUN"]
    return issue


def role_dashboard(issues: list[GovernanceIssue], role: LODRole) -> pd.DataFrame:
    rows = []
    for issue in issues:
        rows.append(
            {
                "role": role.value,
                "issue_id": issue.issue_id,
                "title": issue.title,
                "severity": issue.severity.value,
                "status": issue.status.value,
                "focus": ROLE_DEFINITIONS[role],
                "next_action": _next_action_for_role(issue, role),
            }
        )
    return pd.DataFrame(rows)


def _next_action_for_role(issue: GovernanceIssue, role: LODRole) -> str:
    if role in FIRST_LINE_ROLES:
        return "Investigate, document root cause, assess impact, remediate and submit evidence."
    if role in SECOND_LINE_ROLES:
        return "Challenge severity, impact assessment, remediation design and closure evidence."
    if role in THIRD_LINE_ROLES:
        return "Inspect evidence, audit trail and control effectiveness."
    return "Review material issues, overdue actions, financial impact and reporting readiness."


def issue_queue() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["DQ-101", "Missing income affects PD model", "1LOD Data Steward", "Impact Assessment", "Pending 2LOD challenge"],
            ["REC-204", "Risk/finance exposure mismatch", "1LOD Finance Owner", "Root cause analysis", "Open"],
            ["MRM-077", "Missing model version affects traceability", "Model Owner", "Remediation plan submitted", "2LOD review"],
        ],
        columns=["issue_id", "issue", "owner", "1lod_status", "2lod_status"],
    )
