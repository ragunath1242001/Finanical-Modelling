"""Aggregate model-risk reporting summaries."""

from __future__ import annotations

import pandas as pd

from src.data.synthetic_model_risk import synthetic_approvals, synthetic_findings, synthetic_model_inventory, synthetic_restrictions
from src.model_risk.approvals import approval_expired
from src.model_risk.models import ApprovalDecisionType, FindingSeverity, LifecycleStatus, ModelTier, Rating
from src.model_risk.monitoring import monitoring_results_for_pd_model
from src.model_risk.revalidation import scheduled_revalidation_due
from src.model_risk.use_restrictions import restriction_active


def model_risk_kpis() -> dict[str, int]:
    inventory = synthetic_model_inventory()
    findings = synthetic_findings()
    approvals = synthetic_approvals()
    restrictions = synthetic_restrictions()
    monitoring = monitoring_results_for_pd_model()
    return {
        "total_models": len(inventory),
        "tier1_models": sum(model.model_tier == ModelTier.TIER_1 for model in inventory),
        "approved_models": sum(model.approval_status == ApprovalDecisionType.APPROVED for model in inventory),
        "conditionally_approved_models": sum(model.approval_status == ApprovalDecisionType.CONDITIONALLY_APPROVED for model in inventory),
        "models_with_active_restrictions": sum(restriction_active(item) for item in restrictions),
        "overdue_validations": sum(scheduled_revalidation_due(model) for model in inventory),
        "open_high_findings": sum(finding.severity in {FindingSeverity.HIGH, FindingSeverity.CRITICAL} and finding.status.value != "Closed" for finding in findings),
        "red_monitoring_breaches": sum(result.status == Rating.RED for result in monitoring),
        "expired_approvals": sum(approval_expired(item) for item in approvals),
        "models_affecting_ifrs9": sum("IFRS" in ", ".join(model.affected_reports + model.downstream_systems) for model in inventory),
        "models_affecting_capital": sum("COREP" in ", ".join(model.affected_reports + model.downstream_systems) for model in inventory),
        "models_affecting_reporting": sum(bool(model.affected_reports) for model in inventory),
    }


def model_risk_narrative(kpis: dict[str, int]) -> str:
    if kpis["red_monitoring_breaches"] == 0 and kpis["open_high_findings"] == 0:
        return "Model-risk indicators are stable in the synthetic portfolio."
    return (
        f"{kpis['tier1_models']} Tier 1 model(s) are tracked. "
        f"{kpis['red_monitoring_breaches']} red monitoring breach(es) and {kpis['open_high_findings']} high/critical finding(s) are open. "
        "The main educational concern is that PD calibration and LGD data quality can limit confidence in IFRS 9, stress testing and reporting outputs."
    )


def model_risk_kpis_frame() -> pd.DataFrame:
    return pd.DataFrame([{"metric": key, "value": value} for key, value in model_risk_kpis().items()])


def model_confidence(model_id: str) -> str:
    kpis = model_risk_kpis()
    if model_id == "PD-LOGIT-001" and kpis["red_monitoring_breaches"]:
        return "Use restricted"
    if model_id == "LGD-COLL-001":
        return "Limited confidence"
    return "Moderate confidence"
