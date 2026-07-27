"""Educational model tiering framework."""

from __future__ import annotations

from dataclasses import dataclass

from src.model_risk.models import ModelRiskError, ModelTier


@dataclass(frozen=True)
class TieringInput:
    financial_materiality: float
    regulatory_importance: float
    customer_impact: float
    model_complexity: float
    degree_of_automation: float
    credit_decision_use: float
    regulatory_reporting_use: float
    downstream_processes: int
    data_sensitivity: float
    substitutability: float
    explainability: float
    uncertainty: float


@dataclass(frozen=True)
class TieringResult:
    tier: ModelTier
    score: float
    contributing_factors: list[str]
    rationale: str
    validation_frequency: str
    monitoring_intensity: str
    approval_level: str


def classify_model_tier(data: TieringInput, tier1_threshold: float = 7.0, tier2_threshold: float = 4.0) -> TieringResult:
    values = [
        data.financial_materiality,
        data.regulatory_importance,
        data.customer_impact,
        data.model_complexity,
        data.degree_of_automation,
        data.credit_decision_use,
        data.regulatory_reporting_use,
        min(10.0, data.downstream_processes),
        data.data_sensitivity,
        10 - data.substitutability,
        10 - data.explainability,
        data.uncertainty,
    ]
    if any(value < 0 or value > 10 for value in values):
        raise ModelRiskError("Tiering factors must be between 0 and 10.")
    score = sum(values) / len(values)
    factors = []
    labels = [
        "financial materiality",
        "regulatory importance",
        "customer impact",
        "complexity",
        "automation",
        "credit-decision use",
        "regulatory-reporting use",
        "downstream process count",
        "data sensitivity",
        "low substitutability",
        "low explainability",
        "uncertainty",
    ]
    factors = [label for label, value in zip(labels, values) if value >= 7]
    if score >= tier1_threshold:
        return TieringResult(ModelTier.TIER_1, score, factors, "High materiality and governance intensity.", "At least annually", "Monthly with red-breach escalation", "Model Risk Committee")
    if score >= tier2_threshold:
        return TieringResult(ModelTier.TIER_2, score, factors, "Medium materiality with independent review.", "Every 18 months", "Monthly or quarterly", "Model Risk Manager")
    return TieringResult(ModelTier.TIER_3, score, factors, "Lower materiality educational model.", "Every 24-36 months", "Quarterly", "Model Owner")
