from src.risk.xva import cva, exposure_profile, mva, xva_summary


def test_exposure_profile_collateral_reduces_epe():
    uncollateralized = exposure_profile(1000, 3, 0.1, 0.0)
    collateralized = exposure_profile(1000, 3, 0.1, 0.5)
    assert collateralized["expected_positive_exposure"].sum() < uncollateralized["expected_positive_exposure"].sum()


def test_cva_positive_for_positive_exposure():
    profile = exposure_profile(1000, 3, 0.1, 0.0)
    assert cva(profile, 0.02, 0.6, 0.03) > 0


def test_xva_summary_contains_total_cost():
    _, summary = xva_summary(1000, 3, 0.1, 0.2, 0.02, 0.6, 0.01, 0.015, 100, 0.01, 0.03)
    assert "Total XVA cost" in summary
    assert mva(100, 0.01, 3, 0.03) > 0
