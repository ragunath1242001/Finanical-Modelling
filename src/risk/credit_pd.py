from __future__ import annotations

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURES = ["age", "income", "credit_score", "debt_to_income", "loan_amount", "ltv", "days_past_due"]


def train_pd_model(frame: pd.DataFrame) -> Pipeline:
    data = frame.copy()
    data["default_target"] = data["default_flag"].astype(int)
    data["income"] = data["income"].fillna(data["income"].median())
    model = Pipeline([("scale", StandardScaler()), ("clf", LogisticRegression(max_iter=500, class_weight="balanced"))])
    model.fit(data[FEATURES], data["default_target"])
    return model


def score_pd(model: Pipeline, frame: pd.DataFrame) -> pd.Series:
    data = frame.copy()
    data["income"] = data["income"].fillna(data["income"].median())
    return pd.Series(model.predict_proba(data[FEATURES])[:, 1], index=frame.index)
