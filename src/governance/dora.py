from __future__ import annotations

import pandas as pd


def dora_incident_classification(
    affected_users: int,
    downtime_hours: float,
    data_loss: bool,
    critical_service: bool,
    third_party_provider: bool,
) -> dict[str, int | str | bool]:
    score = 0
    score += 25 if affected_users >= 10_000 else 10 if affected_users >= 1_000 else 0
    score += 25 if downtime_hours >= 4 else 10 if downtime_hours >= 1 else 0
    score += 20 if data_loss else 0
    score += 20 if critical_service else 0
    score += 10 if third_party_provider else 0
    if score >= 60:
        severity = "Major ICT-related incident"
        reporting = "Initial notification required; activate crisis and regulator reporting workflow"
    elif score >= 30:
        severity = "Significant operational resilience event"
        reporting = "Internal escalation and supervisory reporting assessment required"
    else:
        severity = "Low severity event"
        reporting = "Log, monitor, and close through standard incident management"
    return {
        "incident_score": score,
        "severity": severity,
        "third_party_provider": third_party_provider,
        "reporting_action": reporting,
    }


def resilience_score(
    rto_hours: float,
    actual_recovery_hours: float,
    rpo_hours: float,
    actual_data_loss_hours: float,
    tested_this_year: bool,
    exit_plan_available: bool,
) -> dict[str, float | str | bool]:
    rto_met = actual_recovery_hours <= rto_hours
    rpo_met = actual_data_loss_hours <= rpo_hours
    score = 25 * rto_met + 25 * rpo_met + 25 * tested_this_year + 25 * exit_plan_available
    return {
        "rto_met": bool(rto_met),
        "rpo_met": bool(rpo_met),
        "tested_this_year": tested_this_year,
        "exit_plan_available": exit_plan_available,
        "resilience_score": float(score),
        "status": "Resilient" if score >= 75 else "Remediation required",
    }


def third_party_register() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["Cloud data platform", "Critical", "EU region", "Exit plan drafted", "Annual resilience test"],
            ["Payment screening API", "Critical", "Cross-border", "Exit plan gap", "Quarterly SLA review"],
            ["KYC document service", "Important", "EU region", "Substitution available", "Annual control review"],
        ],
        columns=["provider", "criticality", "location", "exit_plan_status", "oversight_activity"],
    )
