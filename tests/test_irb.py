from src.risk.irb import irb_rwa_equivalent, simplified_irb_capital, standardized_rwa


def test_standardized_irb_comparison_outputs_positive_values():
    assert standardized_rwa(100_000, 0.5) == 50_000
    capital = simplified_irb_capital(0.04, 0.45, 100_000)
    assert capital > 0
    assert irb_rwa_equivalent(capital) == capital * 12.5
