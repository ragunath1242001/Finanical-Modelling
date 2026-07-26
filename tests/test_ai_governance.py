from src.governance.ai_governance import ai_act_control_assessment, ai_risk_tier, fairness_gap


def test_ai_risk_tier_credit_scoring_high_risk():
    assert ai_risk_tier("Credit scoring", True, True) == "High-risk AI system"


def test_ai_control_assessment_scores_implemented_controls():
    table, score = ai_act_control_assessment({"risk_management": True, "data_governance": True})
    assert score == 30
    assert int(table["status"].eq("Gap").sum()) == 6


def test_fairness_gap_flags_large_difference():
    result = fairness_gap(0.8, 0.65)
    assert result["absolute_gap"] == 0.15
    assert result["status"] == "Fairness review required"
