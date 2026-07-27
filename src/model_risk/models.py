"""Typed model-risk domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class ModelRiskError(ValueError):
    """Raised when model-risk state or input is invalid."""


class ModelFamily(str, Enum):
    PD = "PD"
    LGD = "LGD"
    EAD = "EAD"
    IFRS9 = "IFRS 9"
    IRB = "IRB"
    STRESS = "Stress testing"
    FRAUD = "Fraud"
    AML = "AML"
    FORECASTING = "Forecasting"
    LIQUIDITY = "Liquidity"
    CLIMATE = "Climate risk"
    XVA = "XVA"
    AI = "AI or machine learning"


class LifecycleStatus(str, Enum):
    PROPOSED = "Proposed"
    IN_DEVELOPMENT = "In Development"
    DEVELOPMENT_COMPLETE = "Development Complete"
    PENDING_VALIDATION = "Pending Validation"
    VALIDATION_IN_PROGRESS = "Validation in Progress"
    VALIDATION_FAILED = "Validation Failed"
    CONDITIONAL_APPROVAL = "Conditional Approval"
    APPROVED = "Approved"
    IN_PRODUCTION = "In Production"
    UNDER_MONITORING = "Under Monitoring"
    PERFORMANCE_CONCERN = "Performance Concern"
    USE_RESTRICTED = "Use Restricted"
    REVALIDATION_REQUIRED = "Revalidation Required"
    RETIRED = "Retired"


class ModelTier(str, Enum):
    TIER_1 = "Tier 1: High materiality"
    TIER_2 = "Tier 2: Medium materiality"
    TIER_3 = "Tier 3: Lower materiality"


class ApprovalDecisionType(str, Enum):
    APPROVED = "Approved"
    CONDITIONALLY_APPROVED = "Conditionally Approved"
    REJECTED = "Rejected"
    DEFERRED = "Deferred"


class ValidationOutcome(str, Enum):
    PASS = "Pass"
    PASS_WITH_CONDITIONS = "Pass with Conditions"
    FAIL = "Fail"
    NOT_ASSESSED = "Not Assessed"


class Rating(str, Enum):
    GREEN = "Green"
    AMBER = "Amber"
    RED = "Red"
    NOT_AVAILABLE = "Not Available"


class FindingSeverity(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"


class FindingStatus(str, Enum):
    OPEN = "Open"
    IN_REMEDIATION = "In remediation"
    PENDING_VALIDATOR_REVIEW = "Pending validator review"
    CLOSED = "Closed"


class ThresholdDirection(str, Enum):
    HIGHER_IS_WORSE = "higher_is_worse"
    LOWER_IS_WORSE = "lower_is_worse"
    OUTSIDE_RANGE_IS_WORSE = "outside_range_is_worse"


@dataclass(frozen=True)
class ModelRecord:
    model_id: str
    model_name: str
    model_version: str
    model_family: ModelFamily
    model_type: str
    business_purpose: str
    owner: str
    developer: str
    validator: str
    business_unit: str
    legal_entity: str
    jurisdiction: str
    regulatory_relevance: str
    materiality: float
    model_tier: ModelTier
    lifecycle_status: LifecycleStatus
    implementation_date: date
    last_validation_date: date
    next_validation_date: date
    monitoring_frequency: str
    input_datasets: list[str]
    output_fields: list[str]
    upstream_systems: list[str]
    downstream_systems: list[str]
    affected_reports: list[str]
    open_issues: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    use_restrictions: list[str] = field(default_factory=list)
    approval_status: ApprovalDecisionType = ApprovalDecisionType.DEFERRED
    retirement_date: date | None = None


@dataclass(frozen=True)
class DevelopmentEvidence:
    model_id: str
    model_version: str
    development_methodology: str
    objective: str
    population: str
    target_definition: str
    sample_period: str
    features: list[str]
    exclusions: list[str]
    missing_value_treatment: str
    outlier_treatment: str
    transformations: list[str]
    feature_selection: str
    algorithm: str
    hyperparameters: dict[str, object]
    calibration: str
    segmentation: str
    assumptions: list[str]
    limitations: list[str]
    performance_results: dict[str, float]
    stability_results: dict[str, float]
    explainability_results: dict[str, float | str]
    implementation_checks: list[str]
    developer_signoff: str


@dataclass(frozen=True)
class ValidationAssessment:
    model_id: str
    model_version: str
    dimension: str
    rating: Rating
    result: ValidationOutcome
    evidence: str
    finding: str
    severity: FindingSeverity
    recommendation: str
    validator_conclusion: str


@dataclass
class ValidationFinding:
    finding_id: str
    model_id: str
    model_version: str
    validation_dimension: str
    title: str
    description: str
    severity: FindingSeverity
    recommendation: str
    owner: str
    due_date: date
    status: FindingStatus
    closure_evidence: list[str] = field(default_factory=list)
    validator_decision: str = ""
    linked_governance_issue: str = ""


@dataclass(frozen=True)
class ApprovalDecision:
    decision_id: str
    model_id: str
    model_version: str
    decision: ApprovalDecisionType
    decision_date: date
    approver_role: str
    conditions: list[str]
    use_restrictions: list[str]
    expiry_date: date | None
    required_remediation: list[str]
    next_review_date: date


@dataclass(frozen=True)
class UseRestriction:
    restriction_id: str
    model_id: str
    model_version: str
    restriction: str
    reason: str
    effective_date: date
    expiry_date: date | None
    approving_role: str
    linked_finding: str
    linked_issue: str
    active_status: bool


@dataclass(frozen=True)
class MonitoringThreshold:
    metric_name: str
    warning_threshold: float
    breach_threshold: float
    direction: ThresholdDirection
    tolerance: float = 0.0
    minimum_sample_size: int = 30


@dataclass(frozen=True)
class MonitoringResult:
    model_id: str
    metric_name: str
    current_value: float
    reference_value: float
    warning_threshold: float
    breach_threshold: float
    status: Rating
    trend: str
    commentary: str
    required_action: str


@dataclass(frozen=True)
class RevalidationTrigger:
    trigger_id: str
    model_id: str
    trigger: str
    trigger_date: date
    evidence: str
    severity: FindingSeverity
    required_action: str
    due_date: date


@dataclass(frozen=True)
class Limitation:
    limitation_id: str
    model_id: str
    model_version: str
    description: str
    category: str
    severity: FindingSeverity
    affected_population: str
    impact: str
    compensating_control: str
    owner: str
    expiry_date: date
    review_status: str
    linked_finding: str
    linked_issue: str
