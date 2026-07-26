from src.governance.dora import dora_incident_classification, resilience_score


def test_dora_major_incident_classification():
    result = dora_incident_classification(20_000, 5, True, True, True)
    assert result["severity"] == "Major ICT-related incident"
    assert result["incident_score"] >= 60


def test_resilience_score_flags_remediation():
    result = resilience_score(4, 8, 1, 2, tested_this_year=True, exit_plan_available=False)
    assert result["rto_met"] is False
    assert result["rpo_met"] is False
    assert result["status"] == "Remediation required"
