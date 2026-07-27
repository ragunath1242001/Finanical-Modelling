"""Educational fairness metrics for synthetic groups only."""

from __future__ import annotations

import pandas as pd


FAIRNESS_DISCLAIMER = (
    "Fairness metrics are context-dependent educational indicators. Legal assessment requires jurisdiction-specific review; "
    "equal metrics do not prove absence of discrimination."
)


def approval_rate_difference(frame: pd.DataFrame, group_col: str, approved_col: str) -> dict[str, float | str]:
    rates = frame.groupby(group_col)[approved_col].mean()
    return {"max_rate": float(rates.max()), "min_rate": float(rates.min()), "difference": float(rates.max() - rates.min()), "disclaimer": FAIRNESS_DISCLAIMER}
