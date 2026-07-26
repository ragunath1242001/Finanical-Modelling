from __future__ import annotations

import numpy as np
import pandas as pd


def twelve_month_forecast(series: pd.Series, macro_multiplier: float = 1.0) -> pd.DataFrame:
    values = series.astype(float).to_numpy()
    recent_growth = np.diff(values[-6:]).mean() if len(values) >= 7 else 0
    last = values[-1]
    rows = []
    for month in range(1, 13):
        point = (last + recent_growth * month) * macro_multiplier
        band = abs(point) * 0.06
        rows.append({"month_ahead": month, "forecast": point, "lower": point - band, "upper": point + band})
    return pd.DataFrame(rows)
