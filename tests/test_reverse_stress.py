from src.risk.reverse_stress import cet1_depletion_bps, required_loss_for_target, reverse_stress_solver


def test_required_loss_for_target_bps():
    assert required_loss_for_target(100, 1_000_000, 300) == 30_000


def test_cet1_depletion_bps():
    assert cet1_depletion_bps(0.12, 0.09) == 300


def test_reverse_stress_solver_flags_target_breach():
    result = reverse_stress_solver(
        cet1=100,
        at1=0,
        tier2=0,
        rwa_amount=1000,
        target_depletion_bps=300,
        ead=1000,
        pd=0.01,
        lgd=0.5,
        pd_multiplier=2,
        lgd_multiplier=1,
        market_loss=20,
        operational_loss=5,
        funding_cost_shock=0,
    )
    assert result["depletion_bps"] >= 300
    assert result["status"] == "Target breached"
