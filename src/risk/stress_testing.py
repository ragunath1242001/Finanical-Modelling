from src.risk.ifrs9 import expected_credit_loss

SCENARIOS = {
    "Baseline": {"pd_multiplier": 1.0, "lgd_multiplier": 1.0, "revenue_shock": 0.0},
    "Adverse": {"pd_multiplier": 1.45, "lgd_multiplier": 1.15, "revenue_shock": -0.08},
    "Severe": {"pd_multiplier": 2.1, "lgd_multiplier": 1.35, "revenue_shock": -0.18},
}


def stress_ecl(pd: float, lgd: float, ead: float, pd_multiplier: float, lgd_multiplier: float) -> dict[str, float]:
    stressed_pd = min(pd * pd_multiplier, 1.0)
    stressed_lgd = min(lgd * lgd_multiplier, 1.0)
    baseline = expected_credit_loss(pd, lgd, ead)
    stressed = expected_credit_loss(stressed_pd, stressed_lgd, ead)
    return {
        "stressed_pd": stressed_pd,
        "stressed_lgd": stressed_lgd,
        "baseline_ecl": baseline,
        "stressed_ecl": stressed,
        "provision_increase": max(0.0, stressed - baseline),
    }
