"""Independent validation assessment logic."""

from __future__ import annotations

import pandas as pd

from src.data.synthetic_model_risk import synthetic_development_evidence, synthetic_findings, synthetic_validation_assessments
from src.governance.issues import issue_from_control_result
from src.governance.models import ControlExecutionResult, ControlStatus, QualityDimension, Severity
from src.model_risk.models import DevelopmentEvidence, FindingSeverity, FindingStatus, ModelRiskError, ValidationFinding


REQUIRED_EVIDENCE_FIELDS = ["development_methodology", "objective", "population", "target_definition", "features", "algorithm", "developer_signoff"]


def development_evidence_complete(evidence: DevelopmentEvidence) -> bool:
    return all(bool(getattr(evidence, field)) for field in REQUIRED_EVIDENCE_FIELDS)


def submit_to_validation(evidence: DevelopmentEvidence, developer: str, validator: str) -> None:
    if developer == validator:
        raise ModelRiskError("Independent validator cannot be the same person as developer.")
    if not development_evidence_complete(evidence):
        raise ModelRiskError("Required development evidence is missing.")


def validation_assessments_frame() -> pd.DataFrame:
    return pd.DataFrame([assessment.__dict__ | {"rating": assessment.rating.value, "result": assessment.result.value, "severity": assessment.severity.value} for assessment in synthetic_validation_assessments()])


def findings_frame(findings: list[ValidationFinding] | None = None) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "finding_id": finding.finding_id,
                "model_id": finding.model_id,
                "version": finding.model_version,
                "dimension": finding.validation_dimension,
                "title": finding.title,
                "severity": finding.severity.value,
                "recommendation": finding.recommendation,
                "owner": finding.owner,
                "due_date": finding.due_date.isoformat(),
                "status": finding.status.value,
                "closure_evidence": ", ".join(finding.closure_evidence),
                "linked_governance_issue": finding.linked_governance_issue,
            }
            for finding in (findings or synthetic_findings())
        ]
    )


def close_finding(finding: ValidationFinding, evidence: list[str], validator_decision: str) -> ValidationFinding:
    if not evidence:
        raise ModelRiskError("Finding closure requires evidence.")
    finding.closure_evidence = evidence
    finding.validator_decision = validator_decision
    finding.status = FindingStatus.CLOSED
    return finding


def finding_to_governance_issue(finding: ValidationFinding):
    if finding.linked_governance_issue:
        return None
    result = ControlExecutionResult(
        execution_id=f"MR-{finding.finding_id}",
        control_id=finding.finding_id,
        control_name=finding.title,
        execution_timestamp=pd.Timestamp("2026-07-27").to_pydatetime(),
        records_tested=1,
        records_failed=1,
        failure_rate=1.0,
        threshold=0.0,
        status=ControlStatus.FAIL,
        severity=Severity.HIGH if finding.severity in {FindingSeverity.HIGH, FindingSeverity.CRITICAL} else Severity.MEDIUM,
        sample_failed_records=[{"model_id": finding.model_id, "finding": finding.title}],
        affected_data_elements=["model output"],
        downstream_impact="Model Risk Management, Executive Overview",
        owner=finding.owner,
        dimension=QualityDimension.INTEGRITY,
    )
    return issue_from_control_result(result)


def development_evidence_frame() -> pd.DataFrame:
    return pd.DataFrame([evidence.__dict__ | {"features": ", ".join(evidence.features), "limitations": ", ".join(evidence.limitations)} for evidence in synthetic_development_evidence()])
