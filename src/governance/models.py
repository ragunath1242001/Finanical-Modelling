"""Typed governance domain models for educational BCBS 239 workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum


class GovernanceError(ValueError):
    """Raised when a governance workflow or control input is invalid."""


class Severity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class QualityDimension(str, Enum):
    COMPLETENESS = "Completeness"
    ACCURACY = "Accuracy"
    CONSISTENCY = "Consistency"
    TIMELINESS = "Timeliness"
    VALIDITY = "Validity"
    UNIQUENESS = "Uniqueness"
    INTEGRITY = "Integrity"
    TRACEABILITY = "Traceability"


class ControlType(str, Enum):
    RECORD = "Record-level"
    AGGREGATE = "Aggregate"
    RECONCILIATION = "Reconciliation"
    METADATA = "Metadata"
    WORKFLOW = "Workflow"


class ControlStatus(str, Enum):
    PASS = "Pass"
    FAIL = "Fail"
    WARNING = "Warning"


class IssueStatus(str, Enum):
    OPEN = "Open"
    ACKNOWLEDGED = "Acknowledged"
    UNDER_INVESTIGATION = "Under Investigation"
    IMPACT_ASSESSMENT = "Impact Assessment"
    REMEDIATION_PLANNED = "Remediation Planned"
    IN_PROGRESS = "In Progress"
    PENDING_2LOD_REVIEW = "Pending 2LOD Review"
    REJECTED_BY_2LOD = "Rejected by 2LOD"
    CLOSED = "Closed"
    OVERDUE = "Overdue"
    AUDIT_REVIEW = "Audit Review"


class LODRole(str, Enum):
    FIRST_LINE_DATA_STEWARD = "1LOD Data Steward"
    FIRST_LINE_MODEL_OWNER = "1LOD Model Owner"
    SECOND_LINE_DATA_GOVERNANCE = "2LOD Data Governance"
    SECOND_LINE_MODEL_RISK = "2LOD Model Risk"
    THIRD_LINE_INTERNAL_AUDIT = "3LOD Internal Audit"
    EXECUTIVE_COMMITTEE = "Executive Committee"


class ActionType(str, Enum):
    CREATE = "Create"
    ACKNOWLEDGE = "Acknowledge"
    INVESTIGATE = "Investigate"
    ASSESS_IMPACT = "Assess impact"
    PLAN_REMEDIATION = "Plan remediation"
    UPDATE_PROGRESS = "Update progress"
    ADD_EVIDENCE = "Add evidence"
    SUBMIT_2LOD = "Submit for 2LOD review"
    ACCEPT_CLOSURE = "Accept closure"
    REJECT_CLOSURE = "Reject closure"
    RETURN_TO_REMEDIATION = "Return to remediation"
    AUDIT_OBSERVATION = "Audit observation"


class EvidenceType(str, Enum):
    DATA_EXTRACT = "Data extract"
    CONTROL_RESULT = "Control result"
    TEST_RESULT = "Test result"
    RECONCILIATION_REPORT = "Reconciliation report"
    ROOT_CAUSE_DOCUMENT = "Root-cause document"
    REMEDIATION_PROOF = "Remediation proof"
    APPROVAL_RECORD = "Approval record"


@dataclass(frozen=True)
class DataQualityControl:
    control_id: str
    control_name: str
    description: str
    data_element: str
    quality_dimension: QualityDimension
    control_type: ControlType
    severity: Severity
    threshold: float
    owner: str
    frequency: str
    source_system: str
    downstream_process: str
    regulatory_relevance: str
    enabled: bool = True


@dataclass(frozen=True)
class ControlExecutionResult:
    execution_id: str
    control_id: str
    control_name: str
    execution_timestamp: datetime
    records_tested: int
    records_failed: int
    failure_rate: float
    threshold: float
    status: ControlStatus
    severity: Severity
    sample_failed_records: list[dict[str, object]]
    affected_data_elements: list[str]
    downstream_impact: str
    owner: str
    dimension: QualityDimension


@dataclass
class GovernanceIssue:
    issue_id: str
    title: str
    description: str
    source_control: str
    severity: Severity
    status: IssueStatus
    detected_date: date
    due_date: date
    owner: str
    data_owner: str
    data_steward: str
    affected_model: str
    affected_report: str
    financial_impact: float
    regulatory_impact: str
    root_cause: str = ""
    remediation_plan: str = ""
    closure_evidence: list[str] = field(default_factory=list)
    two_lod_conclusion: str = ""
    audit_status: str = "Not reviewed"
    affected_population: str = ""
    preventive_control: str = ""
    two_lod_approved: bool = False


@dataclass(frozen=True)
class WorkflowAction:
    action_id: str
    issue_id: str
    actor_role: LODRole
    actor_name: str
    action_type: ActionType
    timestamp: datetime
    comment: str
    previous_status: IssueStatus
    new_status: IssueStatus
    evidence_reference: str = ""


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    issue_id: str
    evidence_type: EvidenceType
    description: str
    created_date: date
    created_by: str
    reference: str
    validation_status: str
    reviewer_comment: str = ""


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    timestamp: datetime
    user_role: str
    module: str
    object_type: str
    object_id: str
    action: str
    previous_value: str
    new_value: str
    reason: str
    approval_status: str
