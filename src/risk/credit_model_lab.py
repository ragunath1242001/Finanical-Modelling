from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


MODEL_FEATURES = ["age", "income", "credit_score", "debt_to_income", "loan_amount", "ltv", "days_past_due"]


def prepare_model_frame(customers: pd.DataFrame, loans: pd.DataFrame) -> pd.DataFrame:
    frame = loans.merge(customers, on="customer_id", how="left")
    frame["income"] = frame["income"].fillna(frame["income"].median())
    frame["default_target"] = frame["default_flag"].astype(int)
    return frame.dropna(subset=MODEL_FEATURES + ["default_target"]).copy()


def train_credit_models(frame: pd.DataFrame, test_size: float = 0.3, random_state: int = 7) -> dict[str, object]:
    x_train, x_test, y_train, y_test = train_test_split(
        frame[MODEL_FEATURES],
        frame["default_target"],
        test_size=test_size,
        random_state=random_state,
        stratify=frame["default_target"],
    )
    models = {
        "Logistic Regression": Pipeline(
            [("scale", StandardScaler()), ("model", LogisticRegression(max_iter=500, class_weight="balanced"))]
        ),
        "Gradient Boosting": GradientBoostingClassifier(random_state=random_state),
    }
    fitted = {}
    for name, model in models.items():
        model.fit(x_train, y_train)
        fitted[name] = model
    return {"models": fitted, "x_train": x_train, "x_test": x_test, "y_train": y_train, "y_test": y_test}


def evaluate_model(model: object, x_test: pd.DataFrame, y_test: pd.Series, threshold: float = 0.5) -> dict[str, float]:
    scores = model.predict_proba(x_test)[:, 1]
    preds = scores >= threshold
    return {
        "auc": roc_auc_score(y_test, scores),
        "average_precision": average_precision_score(y_test, scores),
        "brier_score": brier_score_loss(y_test, scores),
        "accuracy": accuracy_score(y_test, preds),
        "precision": precision_score(y_test, preds, zero_division=0),
        "recall": recall_score(y_test, preds, zero_division=0),
    }


def model_comparison_table(result: dict[str, object], threshold: float = 0.5) -> pd.DataFrame:
    rows = []
    for name, model in result["models"].items():
        metrics = evaluate_model(model, result["x_test"], result["y_test"], threshold)
        rows.append({"model": name, **metrics})
    return pd.DataFrame(rows)


def roc_curve_frame(model: object, x_test: pd.DataFrame, y_test: pd.Series) -> pd.DataFrame:
    scores = model.predict_proba(x_test)[:, 1]
    fpr, tpr, thresholds = roc_curve(y_test, scores)
    return pd.DataFrame({"false_positive_rate": fpr, "true_positive_rate": tpr, "threshold": thresholds})


def calibration_table(model: object, x_test: pd.DataFrame, y_test: pd.Series, bins: int = 10) -> pd.DataFrame:
    scores = model.predict_proba(x_test)[:, 1]
    frame = pd.DataFrame({"score": scores, "actual": y_test.to_numpy()})
    frame["bucket"] = pd.qcut(frame["score"], q=bins, duplicates="drop")
    grouped = frame.groupby("bucket", observed=True).agg(predicted_pd=("score", "mean"), observed_default_rate=("actual", "mean"), count=("actual", "size"))
    return grouped.reset_index(drop=True)


def confusion_matrix_frame(model: object, x_test: pd.DataFrame, y_test: pd.Series, threshold: float) -> pd.DataFrame:
    scores = model.predict_proba(x_test)[:, 1]
    matrix = confusion_matrix(y_test, scores >= threshold, labels=[0, 1])
    return pd.DataFrame(matrix, index=["Actual non-default", "Actual default"], columns=["Predicted non-default", "Predicted default"])


def feature_importance(model: object) -> pd.DataFrame:
    if hasattr(model, "named_steps"):
        estimator = model.named_steps["model"]
        values = np.abs(estimator.coef_[0])
    else:
        values = model.feature_importances_
    return pd.DataFrame({"feature": MODEL_FEATURES, "importance": values}).sort_values("importance", ascending=False)


def assign_risk_grade(pd_value: float) -> str:
    if pd_value < 0.02:
        return "A - Low risk"
    if pd_value < 0.05:
        return "B - Moderate risk"
    if pd_value < 0.10:
        return "C - Watchlist"
    if pd_value < 0.20:
        return "D - High risk"
    return "E - Very high risk"


def score_with_grades(model: object, frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["model_pd"] = model.predict_proba(result[MODEL_FEATURES])[:, 1]
    result["risk_grade"] = result["model_pd"].apply(assign_risk_grade)
    return result


def population_stability_index(expected: pd.Series, actual: pd.Series, bins: int = 10) -> float:
    breakpoints = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
    if len(breakpoints) < 3:
        return 0.0
    expected_counts = pd.cut(expected, breakpoints, include_lowest=True).value_counts(normalize=True, sort=False)
    actual_counts = pd.cut(actual, breakpoints, include_lowest=True).value_counts(normalize=True, sort=False)
    expected_pct = expected_counts.replace(0, 0.0001)
    actual_pct = actual_counts.reindex(expected_counts.index).fillna(0.0001).replace(0, 0.0001)
    psi = ((actual_pct - expected_pct) * np.log(actual_pct / expected_pct)).sum()
    return float(psi)
