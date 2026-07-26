from __future__ import annotations

import pandas as pd


def reconcile_exposure(risk_exposure: float, finance_exposure: float, owner: str = "Finance/Risk Data Steward") -> pd.DataFrame:
    difference = finance_exposure - risk_exposure
    return pd.DataFrame(
        [
            {
                "risk_exposure": risk_exposure,
                "finance_exposure": finance_exposure,
                "difference": difference,
                "adjustment_reason": "Timing, write-off, or source-system mapping difference" if difference else "No adjustment",
                "owner": owner,
                "status": "Open" if abs(difference) > 1 else "Matched",
            }
        ]
    )
