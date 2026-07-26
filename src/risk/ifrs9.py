from __future__ import annotations


def expected_credit_loss(pd: float, lgd: float, ead: float) -> float:
    return round(float(pd) * float(lgd) * float(ead), 6)


def assign_stage(
    days_past_due: int,
    credit_score_change: int = 0,
    industry_stress: str = "normal",
    default_flag: bool = False,
    sicr_threshold: int = 60,
) -> tuple[int, str]:
    if default_flag or days_past_due >= 90:
        return 3, "Stage 3: defaulted or credit-impaired because default/90+ days past due is present."
    if days_past_due >= 30:
        return 2, "Stage 2: significant increase in credit risk because payments are 30+ days past due."
    if credit_score_change <= -abs(sicr_threshold):
        return 2, "Stage 2: significant increase in credit risk because credit score deterioration exceeds the threshold."
    if industry_stress.lower() in {"severe", "high"}:
        return 2, "Stage 2: significant increase in credit risk because the industry is under severe stress."
    return 1, "Stage 1: performing exposure with no significant increase in credit risk."


def calculate_ifrs9(pd: float, lgd: float, ead: float, stage: int, lifetime_multiplier: float = 3.0) -> dict[str, float | str]:
    twelve_month_ecl = expected_credit_loss(pd, lgd, ead)
    lifetime_ecl = twelve_month_ecl * lifetime_multiplier
    provision = lifetime_ecl if stage in {2, 3} else twelve_month_ecl
    return {
        "stage": stage,
        "12_month_ecl": round(twelve_month_ecl, 2),
        "lifetime_ecl": round(lifetime_ecl, 2),
        "provision": round(provision, 2),
        "profit_impact": round(-provision, 2),
        "retained_earnings_impact": round(-provision, 2),
        "cet1_impact": round(-provision, 2),
    }
