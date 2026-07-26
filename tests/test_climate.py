from src.risk.climate import climate_adjusted_credit_risk, climate_pd_multiplier


def test_climate_pd_multiplier_increases_with_high_risk():
    low = climate_pd_multiplier("Technology", "Low", 0, False)
    high = climate_pd_multiplier("Energy", "High", 100, True)
    assert high > low


def test_climate_adjusted_credit_risk_increases_ecl():
    result = climate_adjusted_credit_risk(0.02, 0.4, 100_000, "Energy", "High", 100, 0.2, True)
    assert result["adjusted_pd"] > 0.02
    assert result["adjusted_lgd"] > 0.4
    assert result["climate_ecl"] > result["baseline_ecl"]
