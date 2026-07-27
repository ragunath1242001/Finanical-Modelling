"""Approval decision checks."""

from __future__ import annotations

from datetime import date

from src.data.synthetic_model_risk import synthetic_approvals
from src.model_risk.models import ApprovalDecision, ApprovalDecisionType, ModelRiskError, ValidationOutcome


def approval_expired(approval: ApprovalDecision, as_of: date | None = None) -> bool:
    as_of = as_of or date(2026, 7, 27)
    return approval.expiry_date is not None and approval.expiry_date < as_of


def validate_approval_decision(approval: ApprovalDecision, validation_outcome: ValidationOutcome) -> None:
    if approval.decision == ApprovalDecisionType.APPROVED and validation_outcome not in {ValidationOutcome.PASS, ValidationOutcome.PASS_WITH_CONDITIONS}:
        raise ModelRiskError("Approved model requires completed validation.")
    if approval.decision == ApprovalDecisionType.CONDITIONALLY_APPROVED and not approval.conditions:
        raise ModelRiskError("Conditional approval requires explicit conditions.")
    if approval.decision == ApprovalDecisionType.REJECTED and not approval.required_remediation:
        raise ModelRiskError("Rejected model should document required remediation.")


def approvals_frame():
    import pandas as pd

    return pd.DataFrame([approval.__dict__ | {"decision": approval.decision.value, "conditions": "; ".join(approval.conditions), "use_restrictions": "; ".join(approval.use_restrictions), "expired": approval_expired(approval)} for approval in synthetic_approvals()])
