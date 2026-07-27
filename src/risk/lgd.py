"""Loss-given-default engine."""

from __future__ import annotations

from dataclasses import dataclass

from src.risk.validation import validate_non_negative, validate_probability, validate_rate


@dataclass(frozen=True)
class LGDResult:
    lgd: float
    raw_lgd: float
    bounded: bool
    steps: tuple[str, ...]
    assumptions: tuple[str, ...]


def validate_lgd(lgd: float) -> float:
    return validate_probability(lgd, "LGD")


def recovery_based_lgd(
    ead: float,
    collateral_value: float,
    collateral_haircut: float,
    recovery_rate: float,
    recovery_cost: float,
    time_to_recovery_years: float,
    discount_rate: float,
    unsecured_recovery: float = 0.0,
    downturn_adjustment: float = 0.0,
) -> LGDResult:
    ead = validate_non_negative(ead, "EAD")
    if ead == 0:
        return LGDResult(0.0, 0.0, False, ("Zero EAD produces zero LGD for this educational calculation.",), ("Educational recovery-based LGD.",))
    collateral_value = validate_non_negative(collateral_value, "Collateral value")
    collateral_haircut = validate_probability(collateral_haircut, "Collateral haircut")
    recovery_rate = validate_probability(recovery_rate, "Recovery rate")
    recovery_cost = validate_non_negative(recovery_cost, "Recovery cost")
    time_to_recovery_years = validate_non_negative(time_to_recovery_years, "Time to recovery")
    discount_rate = validate_rate(discount_rate, "Discount rate")
    unsecured_recovery = validate_non_negative(unsecured_recovery, "Unsecured recovery")
    downturn_adjustment = validate_non_negative(downturn_adjustment, "Downturn adjustment")

    collateral_recovery = collateral_value * (1 - collateral_haircut) * recovery_rate
    gross_recovery = max(collateral_recovery + unsecured_recovery - recovery_cost, 0.0)
    discount_factor = 1 / ((1 + discount_rate) ** time_to_recovery_years)
    npv_recovery = gross_recovery * discount_factor
    raw_lgd = 1 - npv_recovery / ead + downturn_adjustment
    bounded_lgd = min(max(raw_lgd, 0.0), 1.0)
    return LGDResult(
        lgd=bounded_lgd,
        raw_lgd=raw_lgd,
        bounded=raw_lgd != bounded_lgd,
        steps=(
            f"Collateral recovery = {collateral_value:,.2f} x (1 - {collateral_haircut:.4f}) x {recovery_rate:.4f} = {collateral_recovery:,.2f}",
            f"NPV recovery = max(collateral + unsecured - cost, 0) x discount factor = {npv_recovery:,.2f}",
            f"LGD = 1 - NPV recoveries / EAD + downturn adjustment = {raw_lgd:.6f}",
        ),
        assumptions=("Educational recovery-based LGD; institution-specific workout and collateral policies may differ.",),
    )


def downturn_lgd(base_lgd: float, multiplier: float) -> LGDResult:
    base = validate_lgd(base_lgd)
    validate_non_negative(multiplier, "LGD multiplier")
    raw = base * float(multiplier)
    bounded = min(raw, 1.0)
    return LGDResult(
        lgd=bounded,
        raw_lgd=raw,
        bounded=raw != bounded,
        steps=(f"Downturn LGD = base LGD {base:.6f} x multiplier {float(multiplier):.4f} = {raw:.6f}", f"Bounded LGD = {bounded:.6f}"),
        assumptions=("LGD multiplier is an educational downturn approximation.",),
    )
