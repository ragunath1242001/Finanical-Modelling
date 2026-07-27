"""Reusable drift measures for model monitoring."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.model_risk.models import Rating


def population_stability_index(expected, actual, bins: int = 10, epsilon: float = 1e-6) -> float:
    expected = pd.Series(expected).dropna()
    actual = pd.Series(actual).dropna()
    if expected.empty or actual.empty:
        return 0.0
    breakpoints = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
    if len(breakpoints) < 3:
        return 0.0
    expected_pct = pd.cut(expected, breakpoints, include_lowest=True).value_counts(normalize=True, sort=False).replace(0, epsilon)
    actual_pct = pd.cut(actual, breakpoints, include_lowest=True).value_counts(normalize=True, sort=False).reindex(expected_pct.index).fillna(epsilon).replace(0, epsilon)
    return float(((actual_pct - expected_pct) * np.log(actual_pct / expected_pct)).sum())


def categorical_drift(expected, actual) -> dict[str, float | list[str]]:
    exp = pd.Series(expected).fillna("__missing__")
    act = pd.Series(actual).fillna("__missing__")
    categories = sorted(set(exp.unique()) | set(act.unique()))
    exp_freq = exp.value_counts(normalize=True).reindex(categories).fillna(0)
    act_freq = act.value_counts(normalize=True).reindex(categories).fillna(0)
    return {"total_variation_distance": float(0.5 * np.abs(exp_freq - act_freq).sum()), "unseen_categories": sorted(set(act.unique()) - set(exp.unique()))}


def missingness_drift(expected: pd.Series, actual: pd.Series) -> dict[str, float | str]:
    reference = float(expected.isna().mean())
    current = float(actual.isna().mean())
    return {"reference_missing_rate": reference, "current_missing_rate": current, "difference": current - reference, "status": "Red" if current - reference >= 0.10 else "Amber" if current - reference >= 0.05 else "Green"}


def drift_status(value: float, amber: float = 0.10, red: float = 0.25) -> Rating:
    if value >= red:
        return Rating.RED
    if value >= amber:
        return Rating.AMBER
    return Rating.GREEN
