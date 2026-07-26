from __future__ import annotations

import pandas as pd


def fraud_score(transactions: pd.DataFrame) -> pd.Series:
    score = (
        0.02
        + (transactions["amount"] > 1000).astype(float) * 0.12
        + (transactions["amount"] > 5000).astype(float) * 0.18
        + transactions["device_mismatch"].astype(float) * 0.28
        + (transactions["velocity_24h"] > 5).astype(float) * 0.16
        + transactions["merchant_category"].eq("crypto").astype(float) * 0.08
    )
    return score.clip(0, 0.98)


def alert_queue(transactions: pd.DataFrame, threshold: float) -> pd.DataFrame:
    result = transactions.copy()
    result["fraud_probability"] = fraud_score(result)
    result["risk_label"] = result["fraud_probability"].apply(lambda x: "Alert" if x >= threshold else "No alert")
    return result.sort_values("fraud_probability", ascending=False)


def threshold_summary(scored: pd.DataFrame) -> dict[str, float]:
    alerts = scored["risk_label"].eq("Alert")
    positives = scored["fraud_label"].astype(bool)
    tp = int((alerts & positives).sum())
    fp = int((alerts & ~positives).sum())
    fn = int((~alerts & positives).sum())
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    return {"alerts": int(alerts.sum()), "precision": precision, "recall": recall}
