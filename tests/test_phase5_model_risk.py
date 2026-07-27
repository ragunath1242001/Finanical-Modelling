from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from src.data.synthetic_model_risk import (
    synthetic_approvals,
    synthetic_champion_challenger,
    synthetic_development_evidence,
    synthetic_findings,
    synthetic_model_inventory,
    synthetic_restrictions,
)
from src.model_risk.approvals import approval_expired, validate_approval_decision
from src.model_risk.champion_challenger import compare_champion_challenger
from src.model_risk.classification import TieringInput, classify_model_tier
from src.model_risk.drift import categorical_drift, drift_status, missingness_drift, population_stability_index
from src.model_risk.explainability import global_feature_importance, local_contributions
from src.model_risk.inventory import validate_inventory
from src.model_risk.lifecycle import production_ready, validate_lifecycle_transition
from src.model_risk.limitations import limitation_expired, validate_limitation
from src.model_risk.models import (
    ApprovalDecisionType,
    FindingSeverity,
    LifecycleStatus,
    ModelRiskError,
    ModelTier,
    Rating,
    ThresholdDirection,
    ValidationOutcome,
    MonitoringThreshold,
)
from src.model_risk.monitoring import evaluate_monitoring_metric, revalidation_trigger_from_monitoring, red_breach_to_finding
from src.model_risk.performance import binary_classification_metrics, calibration_table, regression_metrics
from src.model_risk.reporting import model_confidence, model_risk_kpis
from src.model_risk.revalidation import scheduled_revalidation_due, trigger_for_overdue_validation
from src.model_risk.use_restrictions import restriction_active
from src.model_risk.validation import close_finding, development_evidence_complete, finding_to_governance_issue, submit_to_validation
from src.reporting.model_risk_reporting import model_risk_readiness_factors


def test_inventory_unique_owner_and_independent_validator():
    records = synthetic_model_inventory()
    validate_inventory(records)
    duplicate = records + [records[0]]
    with pytest.raises(ModelRiskError):
        validate_inventory(duplicate)


def test_invalid_lifecycle_transitions_are_blocked():
    with pytest.raises(ModelRiskError):
        validate_lifecycle_transition(LifecycleStatus.PROPOSED, LifecycleStatus.IN_PRODUCTION, ApprovalDecisionType.DEFERRED, ValidationOutcome.NOT_ASSESSED)
    with pytest.raises(ModelRiskError):
        validate_lifecycle_transition(LifecycleStatus.VALIDATION_IN_PROGRESS, LifecycleStatus.APPROVED, ApprovalDecisionType.APPROVED, ValidationOutcome.FAIL)
    with pytest.raises(ModelRiskError):
        validate_lifecycle_transition(LifecycleStatus.RETIRED, LifecycleStatus.IN_PRODUCTION, ApprovalDecisionType.APPROVED, ValidationOutcome.PASS)


def test_production_model_requires_valid_approval():
    approved = synthetic_model_inventory()[0]
    assert production_ready(approved)
    with pytest.raises(ModelRiskError):
        validate_lifecycle_transition(LifecycleStatus.APPROVED, LifecycleStatus.IN_PRODUCTION, ApprovalDecisionType.REJECTED, ValidationOutcome.PASS)


def test_expired_approval_and_overdue_validation_detected():
    approvals = synthetic_approvals()
    assert any(approval_expired(approval) for approval in approvals)
    overdue_model = next(model for model in synthetic_model_inventory() if model.model_id == "LGD-COLL-001")
    assert scheduled_revalidation_due(overdue_model)
    assert trigger_for_overdue_validation(overdue_model) is not None


def test_development_evidence_and_validator_separation():
    evidence = synthetic_development_evidence()[0]
    assert development_evidence_complete(evidence)
    submit_to_validation(evidence, "Developer", "Independent Validator")
    with pytest.raises(ModelRiskError):
        submit_to_validation(evidence, "Same Person", "Same Person")


def test_tiering_higher_materiality_higher_or_equal_tier():
    low = classify_model_tier(TieringInput(1, 1, 1, 1, 1, 1, 1, 1, 8, 8, 8, 1))
    high = classify_model_tier(TieringInput(10, 10, 10, 9, 8, 9, 9, 8, 9, 1, 2, 8))
    assert high.score > low.score
    assert high.tier == ModelTier.TIER_1
    assert high.contributing_factors
    assert high.validation_frequency != low.validation_frequency
    with pytest.raises(ModelRiskError):
        classify_model_tier(TieringInput(11, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1))


def test_binary_metrics_ranges_and_confusion_reconcile():
    y = np.array([0, 0, 1, 1])
    score = np.array([0.1, 0.4, 0.7, 0.9])
    metrics = binary_classification_metrics(y, score, threshold=0.5)
    assert 0 <= metrics["auc"] <= 1
    assert metrics["gini"] == pytest.approx(2 * metrics["auc"] - 1)
    assert metrics["brier_score"] >= 0
    assert metrics["true_negative"] + metrics["false_positive"] + metrics["false_negative"] + metrics["true_positive"] == 4
    cal = calibration_table(y, score, bins=2)
    assert cal["count"].sum() == 4


def test_regression_rmse_non_negative():
    metrics = regression_metrics([1, 2, 3], [1.1, 1.9, 3.2])
    assert metrics["rmse"] >= 0


def test_drift_measures_and_statuses():
    same = pd.Series([1, 2, 3, 4, 5] * 20)
    shifted = pd.Series([5, 6, 7, 8, 9] * 20)
    assert population_stability_index(same, same) < 0.001
    assert population_stability_index(same, shifted) > population_stability_index(same, same)
    assert population_stability_index(pd.Series([0, 0, 0, 1]), pd.Series([1, 1, 1, 1])) >= 0
    miss = missingness_drift(pd.Series([1, 2, 3]), pd.Series([None, None, 3]))
    assert miss["status"] == "Red"
    cat = categorical_drift(pd.Series(["A", "B"]), pd.Series(["A", "C"]))
    assert "C" in cat["unseen_categories"]
    assert drift_status(0.31) == Rating.RED


def test_monitoring_threshold_directions_and_red_escalation():
    green = evaluate_monitoring_metric("M1", "auc", 0.82, 0.80, MonitoringThreshold("auc", 0.75, 0.70, ThresholdDirection.LOWER_IS_WORSE), 100)
    assert green.status == Rating.GREEN
    red = evaluate_monitoring_metric("M1", "psi", 0.30, 0.05, MonitoringThreshold("psi", 0.10, 0.25, ThresholdDirection.HIGHER_IS_WORSE), 100)
    assert red.status == Rating.RED
    assert red_breach_to_finding(red) is not None
    assert revalidation_trigger_from_monitoring(red) is not None
    with pytest.raises(ModelRiskError):
        evaluate_monitoring_metric("M1", "psi", 0.30, 0.05, MonitoringThreshold("psi", 0.10, 0.25, ThresholdDirection.HIGHER_IS_WORSE, minimum_sample_size=1000), 50)


def test_approvals_restrictions_findings_and_limitations():
    conditional = next(app for app in synthetic_approvals() if app.decision == ApprovalDecisionType.CONDITIONALLY_APPROVED)
    validate_approval_decision(conditional, ValidationOutcome.PASS_WITH_CONDITIONS)
    assert conditional.conditions
    rejected = conditional.__class__("APP-X", "M", "1", ApprovalDecisionType.REJECTED, date(2026, 1, 1), "Committee", [], [], None, [], date(2026, 2, 1))
    with pytest.raises(ModelRiskError):
        validate_approval_decision(rejected, ValidationOutcome.FAIL)
    assert any(restriction_active(item) for item in synthetic_restrictions())
    finding = synthetic_findings()[0]
    with pytest.raises(ModelRiskError):
        close_finding(finding, [], "Accepted")
    assert finding_to_governance_issue(finding) is None


def test_limitation_register_validation_and_expiry():
    from src.data.synthetic_model_risk import synthetic_limitations

    limitation = synthetic_limitations()[0]
    validate_limitation(limitation)
    expired = synthetic_limitations()[1]
    assert limitation_expired(expired)


def test_champion_challenger_does_not_promote_auc_alone():
    result = compare_champion_challenger(synthetic_champion_challenger())
    assert result.recommendation == "continue parallel run"
    assert "AUC" in result.rationale


def test_explainability_outputs_are_structured():
    global_exp = global_feature_importance(["a", "b"], [0.2, -0.1])
    assert set(global_exp["direction"]) == {"increases risk", "decreases risk"}
    local = local_contributions({"a": 1.0, "b": 2.0}, {"a": 0.1, "b": -0.05})
    assert "limitations" in local


def test_reporting_integration_and_confidence():
    kpis = model_risk_kpis()
    assert kpis["open_high_findings"] > 0
    assert model_confidence("PD-LOGIT-001") == "Use restricted"
    readiness = model_risk_readiness_factors()
    assert readiness["model_risk_readiness"] in {"Ready with limitations", "Under review"}
