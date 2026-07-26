from __future__ import annotations

from src.risk.basel import capital_ratios


def cet1_depletion_bps(opening_cet1_ratio: float, stressed_cet1_ratio: float) -> float:
    return (opening_cet1_ratio - stressed_cet1_ratio) * 10_000


def reverse_stress_solver(
    cet1: float,
    at1: float,
    tier2: float,
    rwa_amount: float,
    target_depletion_bps: float,
    ead: float,
    pd: float,
    lgd: float,
    pd_multiplier: float,
    lgd_multiplier: float,
    market_loss: float,
    operational_loss: float,
    funding_cost_shock: float,
) -> dict[str, float | str]:
    opening_ratio = capital_ratios(cet1, at1, tier2, rwa_amount)["cet1_ratio"]
    stressed_pd = min(pd * pd_multiplier, 1.0)
    stressed_lgd = min(lgd * lgd_multiplier, 1.0)
    baseline_ecl = pd * lgd * ead
    stressed_ecl = stressed_pd * stressed_lgd * ead
    provision_increase = max(0.0, stressed_ecl - baseline_ecl)
    total_loss = provision_increase + market_loss + operational_loss + funding_cost_shock
    stressed_cet1 = max(0.0, cet1 - total_loss)
    stressed_ratio = capital_ratios(stressed_cet1, at1, tier2, rwa_amount)["cet1_ratio"]
    depletion = cet1_depletion_bps(opening_ratio, stressed_ratio)
    gap = target_depletion_bps - depletion
    status = "Target breached" if depletion >= target_depletion_bps else "More severe shocks required"
    return {
        "opening_cet1_ratio": opening_ratio,
        "stressed_pd": stressed_pd,
        "stressed_lgd": stressed_lgd,
        "baseline_ecl": baseline_ecl,
        "stressed_ecl": stressed_ecl,
        "provision_increase": provision_increase,
        "total_loss": total_loss,
        "stressed_cet1": stressed_cet1,
        "stressed_cet1_ratio": stressed_ratio,
        "depletion_bps": depletion,
        "target_gap_bps": gap,
        "status": status,
    }


def required_loss_for_target(cet1: float, rwa_amount: float, target_depletion_bps: float) -> float:
    return rwa_amount * (target_depletion_bps / 10_000)
