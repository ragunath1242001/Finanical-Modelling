from __future__ import annotations

import pandas as pd


def aml_alerts(transactions: pd.DataFrame) -> pd.DataFrame:
    result = transactions.copy()
    result["aml_score"] = (
        (result["amount"] > 10000).astype(int) * 35
        + result["country_risk"].eq("high").astype(int) * 25
        + result["round_amount"].astype(int) * 15
        + result["rapid_in_out"].astype(int) * 20
        + (result["velocity_24h"] >= 8).astype(int) * 15
    ).clip(0, 100)
    result["alert_reason"] = result.apply(_reason, axis=1)
    result["investigation_priority"] = pd.cut(result["aml_score"], bins=[-1, 24, 54, 100], labels=["Low", "Medium", "High"])
    return result.sort_values("aml_score", ascending=False)


def _reason(row: pd.Series) -> str:
    reasons = []
    if row["amount"] > 10000:
        reasons.append("large unusual transfer")
    if row["country_risk"] == "high":
        reasons.append("high-risk jurisdiction")
    if row["round_amount"]:
        reasons.append("round amount pattern")
    if row["rapid_in_out"]:
        reasons.append("rapid movement of funds")
    if row["velocity_24h"] >= 8:
        reasons.append("high transaction frequency")
    return ", ".join(reasons) or "routine monitoring"
