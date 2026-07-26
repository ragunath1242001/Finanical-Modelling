from __future__ import annotations

import pandas as pd


def pd_reason_codes(row: pd.Series) -> list[str]:
    reasons = []
    if row.get("credit_score", 850) < 620:
        reasons.append("Low credit score increases default likelihood")
    if row.get("debt_to_income", 0) > 0.45:
        reasons.append("High debt-to-income reduces repayment capacity")
    if row.get("days_past_due", 0) >= 30:
        reasons.append("Delinquency is a strong credit deterioration signal")
    if row.get("ltv", 0) > 0.85:
        reasons.append("High LTV can increase loss severity")
    return reasons or ["Risk is mainly driven by the combined portfolio model profile"]
