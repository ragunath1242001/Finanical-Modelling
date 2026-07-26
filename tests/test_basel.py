from src.risk.basel import capital_after_provision, capital_ratios, rwa


def test_basel_rwa_standardized():
    assert rwa(1_000_000, 0.75) == 750_000


def test_cet1_ratio_after_provision():
    post_cet1 = capital_after_provision(100_000, 10_000)
    ratios = capital_ratios(post_cet1, 5_000, 5_000, 1_000_000)
    assert post_cet1 == 90_000
    assert ratios["cet1_ratio"] == 0.09
