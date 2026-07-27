"""Expected-loss calculations with period-level detail."""

from __future__ import annotations

from dataclasses import dataclass

from src.risk.lgd import validate_lgd
from src.risk.pd import build_pd_term_structure, validate_pd
from src.risk.validation import validate_equal_lengths, validate_non_negative, validate_positive


@dataclass(frozen=True)
class ExpectedLossResult:
    pd: float
    lgd: float
    ead: float
    expected_loss: float
    steps: tuple[str, ...]


@dataclass(frozen=True)
class ECLPeriod:
    period: int
    survival_probability_start: float
    conditional_pd: float
    marginal_pd: float
    cumulative_pd: float
    lgd: float
    ead: float
    discount_factor: float
    undiscounted_ecl: float
    discounted_ecl: float


@dataclass(frozen=True)
class LifetimeECLResult:
    periods: tuple[ECLPeriod, ...]
    total_undiscounted_ecl: float
    total_discounted_ecl: float
    steps: tuple[str, ...]


def point_in_time_expected_loss(pd: float, lgd: float, ead: float) -> ExpectedLossResult:
    pd_value = validate_pd(pd)
    lgd_value = validate_lgd(lgd)
    ead_value = validate_non_negative(ead, "EAD")
    expected_loss = pd_value * lgd_value * ead_value
    return ExpectedLossResult(
        pd_value,
        lgd_value,
        ead_value,
        expected_loss,
        (f"Expected loss = PD {pd_value:.6f} x LGD {lgd_value:.6f} x EAD {ead_value:,.2f} = {expected_loss:,.2f}",),
    )


def discount_factor(period: int, discount_rate: float) -> float:
    validate_positive(period, "Period")
    if discount_rate < 0:
        raise ValueError("Discount rate cannot be negative.")
    return 1 / ((1 + float(discount_rate)) ** int(period))


def lifetime_expected_credit_loss(
    conditional_pds: list[float],
    lgds: list[float],
    eads: list[float],
    discount_factors: list[float],
) -> LifetimeECLResult:
    length = validate_equal_lengths({"conditional_pds": conditional_pds, "lgds": lgds, "eads": eads, "discount_factors": discount_factors})
    pd_periods = build_pd_term_structure(conditional_pds)
    rows: list[ECLPeriod] = []
    total_undiscounted = 0.0
    total_discounted = 0.0
    for idx in range(length):
        lgd = validate_lgd(lgds[idx])
        ead = validate_non_negative(eads[idx], "EAD")
        df = validate_positive(discount_factors[idx], "Discount factor")
        pd_row = pd_periods[idx]
        undiscounted = pd_row.marginal_pd * lgd * ead
        discounted = undiscounted * df
        total_undiscounted += undiscounted
        total_discounted += discounted
        rows.append(
            ECLPeriod(
                period=pd_row.period,
                survival_probability_start=pd_row.survival_probability_start,
                conditional_pd=pd_row.conditional_pd,
                marginal_pd=pd_row.marginal_pd,
                cumulative_pd=pd_row.cumulative_pd,
                lgd=lgd,
                ead=ead,
                discount_factor=df,
                undiscounted_ecl=undiscounted,
                discounted_ecl=discounted,
            )
        )
    return LifetimeECLResult(
        tuple(rows),
        total_undiscounted,
        total_discounted,
        ("Lifetime ECL = sum(marginal PD x LGD x EAD x discount factor) across all periods.",),
    )
