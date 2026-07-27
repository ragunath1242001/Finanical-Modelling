"""Monitoring thresholds, escalation and revalidation triggers."""

from __future__ import annotations

from datetime import date, timedelta

from src.data.synthetic_model_risk import synthetic_findings
from src.model_risk.models import (
    FindingSeverity,
    MonitoringResult,
    MonitoringThreshold,
    ModelRiskError,
    Rating,
    RevalidationTrigger,
    ThresholdDirection,
    ValidationFinding,
    FindingStatus,
)


def evaluate_monitoring_metric(model_id: str, metric_name: str, current_value: float, reference_value: float, threshold: MonitoringThreshold, sample_size: int) -> MonitoringResult:
    if sample_size < threshold.minimum_sample_size:
        raise ModelRiskError("Minimum sample size is not met for monitoring.")
    if threshold.direction == ThresholdDirection.HIGHER_IS_WORSE:
        status = Rating.RED if current_value >= threshold.breach_threshold else Rating.AMBER if current_value >= threshold.warning_threshold else Rating.GREEN
    elif threshold.direction == ThresholdDirection.LOWER_IS_WORSE:
        status = Rating.RED if current_value <= threshold.breach_threshold else Rating.AMBER if current_value <= threshold.warning_threshold else Rating.GREEN
    else:
        status = Rating.RED if abs(current_value - reference_value) >= threshold.breach_threshold else Rating.AMBER if abs(current_value - reference_value) >= threshold.warning_threshold else Rating.GREEN
    trend = "increased" if current_value > reference_value else "decreased" if current_value < reference_value else "stable"
    action = "Create finding, assess use restriction and initiate revalidation." if status == Rating.RED else "Investigate and increase monitoring frequency." if status == Rating.AMBER else "Continue monitoring."
    return MonitoringResult(model_id, metric_name, current_value, reference_value, threshold.warning_threshold, threshold.breach_threshold, status, trend, f"{metric_name} {trend} from {reference_value:.4f} to {current_value:.4f}.", action)


def red_breach_to_finding(result: MonitoringResult) -> ValidationFinding | None:
    if result.status != Rating.RED:
        return None
    return ValidationFinding(
        finding_id=f"MON-{result.model_id}-{result.metric_name}",
        model_id=result.model_id,
        model_version="1.0",
        validation_dimension="Monitoring",
        title=f"Red monitoring breach: {result.metric_name}",
        description=result.commentary,
        severity=FindingSeverity.HIGH,
        recommendation=result.required_action,
        owner="Model Owner",
        due_date=date(2026, 7, 27) + timedelta(days=30),
        status=FindingStatus.OPEN,
    )


def revalidation_trigger_from_monitoring(result: MonitoringResult) -> RevalidationTrigger | None:
    if result.status != Rating.RED:
        return None
    return RevalidationTrigger(
        trigger_id=f"REV-{result.model_id}-{result.metric_name}",
        model_id=result.model_id,
        trigger=f"Red monitoring breach for {result.metric_name}",
        trigger_date=date(2026, 7, 27),
        evidence=result.commentary,
        severity=FindingSeverity.HIGH,
        required_action="Independent revalidation required.",
        due_date=date(2026, 8, 26),
    )


def monitoring_results_for_pd_model() -> list[MonitoringResult]:
    return [
        evaluate_monitoring_metric("PD-LOGIT-001", "calibration_error", 0.10, 0.02, MonitoringThreshold("calibration_error", 0.05, 0.08, ThresholdDirection.HIGHER_IS_WORSE), 500),
        evaluate_monitoring_metric("PD-LOGIT-001", "auc", 0.71, 0.80, MonitoringThreshold("auc", 0.75, 0.70, ThresholdDirection.LOWER_IS_WORSE), 500),
        evaluate_monitoring_metric("PD-LOGIT-001", "psi", 0.31, 0.04, MonitoringThreshold("psi", 0.10, 0.25, ThresholdDirection.HIGHER_IS_WORSE), 500),
    ]
