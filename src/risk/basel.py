from __future__ import annotations

from dataclasses import dataclass

from src.risk.validation import validate_non_negative, validate_positive, validate_probability


ILLUSTRATIVE_RISK_WEIGHTS = {
    "sovereign": 0.00,
    "bank": 0.20,
    "corporate": 1.00,
    "residential mortgage": 0.35,
    "retail": 0.75,
    "past due": 1.50,
}


@dataclass(frozen=True)
class StandardisedRWAResult:
    exposure_class: str
    exposure_amount: float
    risk_weight: float
    rwa: float
    capital_requirement: float
    assumptions: tuple[str, ...]


@dataclass(frozen=True)
class CapitalStack:
    cet1: float
    at1: float
    tier2: float
    credit_rwa: float
    market_rwa: float = 0.0
    operational_rwa: float = 0.0
    total_exposure_measure: float | None = None


@dataclass(frozen=True)
class CapitalRatioResult:
    cet1_ratio: float
    tier1_ratio: float
    total_capital_ratio: float
    leverage_ratio: float | None
    total_rwa: float
    total_capital: float
    steps: tuple[str, ...]


def rwa(exposure: float, risk_weight: float) -> float:
    return standardised_rwa("custom", exposure, risk_weight).rwa


def capital_ratios(cet1: float, at1: float, tier2: float, rwa_amount: float) -> dict[str, float]:
    validate_positive(rwa_amount, "RWA")
    return {
        "cet1_ratio": cet1 / rwa_amount,
        "tier1_ratio": (cet1 + at1) / rwa_amount,
        "total_capital_ratio": (cet1 + at1 + tier2) / rwa_amount,
    }


def capital_after_provision(cet1: float, provision_shock: float) -> float:
    return max(0.0, cet1 - max(0.0, provision_shock))


def standardised_rwa(exposure_class: str, exposure_amount: float, risk_weight: float | None = None, capital_requirement_rate: float = 0.08) -> StandardisedRWAResult:
    exposure = validate_non_negative(exposure_amount, "Exposure amount")
    if risk_weight is None:
        risk_weight = ILLUSTRATIVE_RISK_WEIGHTS.get(exposure_class.lower())
        if risk_weight is None:
            raise ValueError(f"Unknown exposure class: {exposure_class}.")
    risk_weight = validate_non_negative(risk_weight, "Risk weight")
    capital_requirement_rate = validate_probability(capital_requirement_rate, "Capital requirement rate")
    calculated_rwa = exposure * risk_weight
    return StandardisedRWAResult(
        exposure_class=exposure_class,
        exposure_amount=exposure,
        risk_weight=risk_weight,
        rwa=calculated_rwa,
        capital_requirement=calculated_rwa * capital_requirement_rate,
        assumptions=("Illustrative risk weights are configurable and not universal regulatory values.",),
    )


def calculate_capital_stack(stack: CapitalStack) -> CapitalRatioResult:
    credit_rwa = validate_non_negative(stack.credit_rwa, "Credit RWA")
    market_rwa = validate_non_negative(stack.market_rwa, "Market RWA")
    operational_rwa = validate_non_negative(stack.operational_rwa, "Operational RWA")
    total_rwa = validate_positive(credit_rwa + market_rwa + operational_rwa, "Total RWA")
    total_capital = stack.cet1 + stack.at1 + stack.tier2
    leverage = None
    if stack.total_exposure_measure is not None:
        leverage = (stack.cet1 + stack.at1) / validate_positive(stack.total_exposure_measure, "Total exposure measure")
    return CapitalRatioResult(
        cet1_ratio=stack.cet1 / total_rwa,
        tier1_ratio=(stack.cet1 + stack.at1) / total_rwa,
        total_capital_ratio=total_capital / total_rwa,
        leverage_ratio=leverage,
        total_rwa=total_rwa,
        total_capital=total_capital,
        steps=("CET1 ratio = CET1 / total RWA.", "Tier 1 ratio = CET1 + AT1 / total RWA.", "Total capital ratio = CET1 + AT1 + Tier 2 / total RWA."),
    )
