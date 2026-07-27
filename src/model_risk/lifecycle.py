"""Lifecycle transition rules for model-risk management."""

from __future__ import annotations

from src.model_risk.models import ApprovalDecisionType, LifecycleStatus, ModelRecord, ModelRiskError, ValidationOutcome


ALLOWED_MODEL_TRANSITIONS = {
    LifecycleStatus.PROPOSED: {LifecycleStatus.IN_DEVELOPMENT},
    LifecycleStatus.IN_DEVELOPMENT: {LifecycleStatus.DEVELOPMENT_COMPLETE},
    LifecycleStatus.DEVELOPMENT_COMPLETE: {LifecycleStatus.PENDING_VALIDATION},
    LifecycleStatus.PENDING_VALIDATION: {LifecycleStatus.VALIDATION_IN_PROGRESS},
    LifecycleStatus.VALIDATION_IN_PROGRESS: {LifecycleStatus.APPROVED, LifecycleStatus.CONDITIONAL_APPROVAL, LifecycleStatus.VALIDATION_FAILED},
    LifecycleStatus.VALIDATION_FAILED: {LifecycleStatus.IN_DEVELOPMENT, LifecycleStatus.REVALIDATION_REQUIRED},
    LifecycleStatus.CONDITIONAL_APPROVAL: {LifecycleStatus.IN_PRODUCTION, LifecycleStatus.USE_RESTRICTED},
    LifecycleStatus.APPROVED: {LifecycleStatus.IN_PRODUCTION},
    LifecycleStatus.IN_PRODUCTION: {LifecycleStatus.UNDER_MONITORING, LifecycleStatus.PERFORMANCE_CONCERN, LifecycleStatus.RETIRED},
    LifecycleStatus.UNDER_MONITORING: {LifecycleStatus.PERFORMANCE_CONCERN, LifecycleStatus.RETIRED},
    LifecycleStatus.PERFORMANCE_CONCERN: {LifecycleStatus.USE_RESTRICTED, LifecycleStatus.REVALIDATION_REQUIRED},
    LifecycleStatus.USE_RESTRICTED: {LifecycleStatus.REVALIDATION_REQUIRED, LifecycleStatus.RETIRED},
    LifecycleStatus.REVALIDATION_REQUIRED: {LifecycleStatus.VALIDATION_IN_PROGRESS},
    LifecycleStatus.RETIRED: set(),
}


def validate_lifecycle_transition(
    current: LifecycleStatus,
    target: LifecycleStatus,
    approval: ApprovalDecisionType | None = None,
    validation_outcome: ValidationOutcome | None = None,
    same_version: bool = True,
) -> None:
    if target not in ALLOWED_MODEL_TRANSITIONS[current]:
        raise ModelRiskError(f"Invalid lifecycle transition from {current.value} to {target.value}.")
    if target == LifecycleStatus.IN_PRODUCTION and approval not in {ApprovalDecisionType.APPROVED, ApprovalDecisionType.CONDITIONALLY_APPROVED}:
        raise ModelRiskError("A production model requires a valid approval.")
    if target in {LifecycleStatus.APPROVED, LifecycleStatus.CONDITIONAL_APPROVAL} and validation_outcome not in {ValidationOutcome.PASS, ValidationOutcome.PASS_WITH_CONDITIONS}:
        raise ModelRiskError("Approval requires completed validation.")
    if current == LifecycleStatus.VALIDATION_FAILED and target == LifecycleStatus.APPROVED:
        raise ModelRiskError("Validation-failed model cannot move directly to Approved.")
    if current == LifecycleStatus.RETIRED and target == LifecycleStatus.IN_PRODUCTION and same_version:
        raise ModelRiskError("Retired model cannot return to production under the same version.")


def production_ready(record: ModelRecord) -> bool:
    return record.approval_status in {ApprovalDecisionType.APPROVED, ApprovalDecisionType.CONDITIONALLY_APPROVED} and record.lifecycle_status in {
        LifecycleStatus.IN_PRODUCTION,
        LifecycleStatus.UNDER_MONITORING,
        LifecycleStatus.PERFORMANCE_CONCERN,
        LifecycleStatus.USE_RESTRICTED,
    }
