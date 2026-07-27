"""Transparent educational explainability outputs."""

from __future__ import annotations

import pandas as pd


def global_feature_importance(features: list[str], importances: list[float]) -> pd.DataFrame:
    total = sum(abs(value) for value in importances) or 1.0
    return pd.DataFrame(
        [
            {
                "feature": feature,
                "importance": abs(value) / total,
                "direction": "increases risk" if value > 0 else "decreases risk",
                "business_interpretation": f"{feature} is associated with model output movement; this is not proof of causality.",
            }
            for feature, value in zip(features, importances)
        ]
    ).sort_values("importance", ascending=False)


def local_contributions(row: dict[str, float], coefficients: dict[str, float], baseline_prediction: float = 0.05) -> dict[str, object]:
    contributions = {feature: float(row.get(feature, 0.0)) * coefficient for feature, coefficient in coefficients.items()}
    prediction = baseline_prediction + sum(contributions.values())
    ordered = sorted(contributions.items(), key=lambda item: item[1], reverse=True)
    return {
        "baseline_prediction": baseline_prediction,
        "prediction": max(0.0, min(1.0, prediction)),
        "feature_contributions": contributions,
        "largest_positive": ordered[:3],
        "largest_negative": sorted(contributions.items(), key=lambda item: item[1])[:3],
        "limitations": "Contribution output is an educational linear approximation and does not prove causality or fairness.",
    }
