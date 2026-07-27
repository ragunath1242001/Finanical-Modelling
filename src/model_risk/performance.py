"""Model validation and monitoring metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)


def binary_classification_metrics(y_true, y_score, threshold: float = 0.5) -> dict[str, float]:
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)
    y_pred = y_score >= threshold
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    auc = roc_auc_score(y_true, y_score)
    return {
        "auc": float(auc),
        "gini": float(2 * auc - 1),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "specificity": float(tn / max(1, tn + fp)),
        "brier_score": float(brier_score_loss(y_true, y_score)),
        "log_loss": float(log_loss(y_true, np.clip(y_score, 1e-6, 1 - 1e-6))),
        "true_negative": float(tn),
        "false_positive": float(fp),
        "false_negative": float(fn),
        "true_positive": float(tp),
    }


def regression_metrics(y_true, y_pred) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    errors = y_true - y_pred
    mse = float(np.mean(errors**2))
    mae = float(np.mean(np.abs(errors)))
    ss_res = float(np.sum(errors**2))
    ss_tot = float(np.sum((y_true - y_true.mean()) ** 2))
    return {"mae": mae, "mse": mse, "rmse": float(np.sqrt(mse)), "r_squared": 1 - ss_res / ss_tot if ss_tot else 0.0, "bias": float(np.mean(y_pred - y_true))}


def calibration_table(y_true, y_score, bins: int = 5) -> pd.DataFrame:
    frame = pd.DataFrame({"actual": y_true, "score": y_score})
    frame["bucket"] = pd.qcut(frame["score"], q=bins, duplicates="drop")
    return frame.groupby("bucket", observed=True).agg(predicted=("score", "mean"), observed=("actual", "mean"), count=("actual", "size")).reset_index(drop=True)
