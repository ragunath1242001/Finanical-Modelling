from src.data.generate_synthetic_data import generate_customers, generate_loans
from src.risk.case_studies import CASE_STUDIES, case_study_steps, run_case_study
from src.ui.study_guide import case_study_report_sections


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


def test_case_study_report_sections_are_detailed():
    customers = generate_customers(n=100)
    loans = generate_loans(customers)
    result = run_case_study(loans, "Model drift alert triggers validation review", 1_000_000, 8_000_000)
    sections = case_study_report_sections(result, case_study_steps(result))
    assert "Executive Summary" in sections
    assert "Transmission Path" in sections
    assert "How To Explain This In An Interview Or Review" in sections
    assert "trigger -> calculation -> business impact -> control response" in sections["Learning Points"]
