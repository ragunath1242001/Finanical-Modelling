from src.risk.liquidity import lcr, leverage_ratio, nsfr


def test_leverage_ratio_calculation():
    assert leverage_ratio(50, 1000) == 0.05


def test_lcr_calculation():
    assert lcr(120, 100) == 1.2


def test_nsfr_calculation():
    assert nsfr(105, 100) == 1.05
