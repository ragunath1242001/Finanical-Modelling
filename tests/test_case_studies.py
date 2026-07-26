from src.data.generate_synthetic_data import generate_customers, generate_loans
from src.risk.case_studies import CASE_STUDIES, case_study_steps, run_case_study


def test_case_study_runs_all_scenarios():
    customers = generate_customers(n=100)
    loans = generate_loans(customers)
    for case_name in CASE_STUDIES:
        result = run_case_study(loans, case_name, cet1=1_000_000, rwa_amount=8_000_000)
        assert result["stressed_ecl"] > 0
        assert "post_cet1_ratio" in result


def test_case_study_steps_are_ordered():
    customers = generate_customers(n=100)
    loans = generate_loans(customers)
    result = run_case_study(loans, "Unemployment shock drives credit deterioration", 1_000_000, 8_000_000)
    steps = case_study_steps(result)
    assert steps["step"].iloc[0] == "Scenario trigger"
    assert steps["step"].iloc[-1] == "Management action"
