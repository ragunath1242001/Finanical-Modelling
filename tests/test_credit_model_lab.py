import pandas as pd

from src.data.generate_synthetic_data import generate_customers, generate_loans
from src.risk.credit_model_lab import (
    assign_risk_grade,
    model_comparison_table,
    population_stability_index,
    prepare_model_frame,
    train_credit_models,
)


def test_credit_model_lab_trains_and_scores_models():
    customers = generate_customers(n=180)
    loans = generate_loans(customers)
    frame = prepare_model_frame(customers, loans)
    result = train_credit_models(frame)
    comparison = model_comparison_table(result)
    assert set(comparison["model"]) == {"Logistic Regression", "Gradient Boosting"}
    assert comparison["auc"].between(0, 1).all()


def test_risk_grade_assignment():
    assert assign_risk_grade(0.01).startswith("A")
    assert assign_risk_grade(0.25).startswith("E")


def test_population_stability_index_positive_for_shift():
    expected = pd.Series([0.01, 0.02, 0.03, 0.04, 0.05] * 20)
    actual = pd.Series([0.10, 0.12, 0.14, 0.16, 0.18] * 20)
    assert population_stability_index(expected, actual) > 0
