"""Reporting integration for model-risk management."""

from __future__ import annotations

from src.model_risk.reporting import model_risk_kpis


def model_risk_readiness_label() -> str:
    kpis = model_risk_kpis()
    if kpis["expired_approvals"] or kpis["red_monitoring_breaches"] >= 2:
        return "Under review"
    if kpis["open_high_findings"] or kpis["models_with_active_restrictions"]:
        return "Ready with limitations"
    return "Ready"


def model_risk_readiness_factors() -> dict[str, str | int]:
    kpis = model_risk_kpis()
    return {
        "model_approval_valid": "No" if kpis["expired_approvals"] else "Yes",
        "validation_current": "No" if kpis["overdue_validations"] else "Yes",
        "monitoring_status_acceptable": "No" if kpis["red_monitoring_breaches"] else "Yes",
        "critical_findings_clear": "No" if kpis["open_high_findings"] else "Yes",
        "prohibited_use_restriction": "No formal prohibited-use restriction; active limitations exist",
        "model_risk_readiness": model_risk_readiness_label(),
    }
