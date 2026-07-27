"""Probability-of-default engine with term-structure support."""

from __future__ import annotations

from dataclasses import dataclass

from src.risk.validation import validate_equal_lengths, validate_probability


@dataclass(frozen=True)
class StressedPDResult:
    base_pd: float
    multiplier: float
    raw_pd: float
    stressed_pd: float
    cap_applied: bool
    steps: tuple[str, ...]


@dataclass(frozen=True)
class PDPeriod:
    period: int
    conditional_pd: float
    survival_probability_start: float
    marginal_pd: float
    cumulative_pd: float
    survival_probability_end: float


def validate_pd(pd: float) -> float:
    return validate_probability(pd, "PD")


def scenario_adjusted_pd(base_pd: float, multiplier: float, cap: float = 1.0) -> StressedPDResult:
    base = validate_pd(base_pd)
    if multiplier < 0:
        raise ValueError("PD multiplier must be non-negative.")
    raw = base * float(multiplier)
    stressed = min(raw, cap)
    cap_applied = raw != stressed
    return StressedPDResult(
        base_pd=base,
        multiplier=float(multiplier),
        raw_pd=raw,
        stressed_pd=stressed,
        cap_applied=cap_applied,
        steps=(f"Base PD {base:.6f} x multiplier {float(multiplier):.4f} = raw PD {raw:.6f}", f"Bounded stressed PD = {stressed:.6f}"),
    )


def build_pd_term_structure(conditional_pds: list[float]) -> list[PDPeriod]:
    validate_equal_lengths({"conditional_pds": conditional_pds})
    survival = 1.0
    cumulative = 0.0
    rows: list[PDPeriod] = []
    for idx, pd_value in enumerate(conditional_pds, start=1):
        conditional = validate_pd(pd_value)
        marginal = survival * conditional
        cumulative += marginal
        survival_end = survival * (1 - conditional)
        rows.append(
            PDPeriod(
                period=idx,
                conditional_pd=conditional,
                survival_probability_start=survival,
                marginal_pd=marginal,
                cumulative_pd=cumulative,
                survival_probability_end=survival_end,
            )
        )
        survival = survival_end
    return rows
