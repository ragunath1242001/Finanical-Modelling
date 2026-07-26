from __future__ import annotations

import pandas as pd


def mean_drift(baseline: pd.Series, current: pd.Series, threshold: float = 0.1) -> dict[str, float | str]:
    base_mean = baseline.mean()
    current_mean = current.mean()
    change = 0.0 if base_mean == 0 else (current_mean - base_mean) / abs(base_mean)
    return {
        "baseline_mean": round(base_mean, 4),
        "current_mean": round(current_mean, 4),
        "relative_change": round(change, 4),
        "status": "Drift flag" if abs(change) >= threshold else "Within threshold",
    }
