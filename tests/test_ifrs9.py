from src.risk.ifrs9 import assign_stage, calculate_ifrs9, expected_credit_loss


def test_ecl_formula_basic():
    assert expected_credit_loss(0.02, 0.45, 100_000) == 900


def test_ifrs9_stage_three_default():
    stage, _ = assign_stage(days_past_due=90)
    assert stage == 3
    stage, _ = assign_stage(days_past_due=0, default_flag=True)
    assert stage == 3


def test_ifrs9_stage_two_sicr():
    stage, _ = assign_stage(days_past_due=0, credit_score_change=-80)
    assert stage == 2
    stage, _ = assign_stage(days_past_due=30)
    assert stage == 2


def test_stage_two_uses_lifetime_provision():
    result = calculate_ifrs9(0.01, 0.5, 100_000, stage=2, lifetime_multiplier=4)
    assert result["12_month_ecl"] == 500
    assert result["provision"] == 2000
