from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from statistics import NormalDist

from src.risk.basel import standardised_rwa
from src.risk.lgd import validate_lgd
from src.risk.pd import validate_pd
from src.risk.validation import validate_non_negative, validate_positive


class IRBApproach(str, Enum):
    STANDARDISED = "Standardised Approach"
    FOUNDATION = "Foundation IRB"
    ADVANCED = "Advanced IRB"


@dataclass(frozen=True)
class IRBComparisonResult:
    approach: IRBApproach
    pd: float
    lgd: float
    ead: float
    maturity: float
    correlation: float
    capital_requirement: float
    model_based_rwa: float
    standardised_rwa: float
    final_rwa: float
    output_floor_rwa: float
    output_floor_applied: bool
    assumptions: tuple[str, ...]


def standardized_rwa(exposure: float, risk_weight: float) -> float:
    return standardised_rwa("custom", exposure, risk_weight).rwa


def corporate_correlation(pd: float) -> float:
    pd = validate_pd(pd)
    import math

    denominator = 1 - math.exp(-50)
    return 0.12 * (1 - math.exp(-50 * pd)) / denominator + 0.24 * (1 - (1 - math.exp(-50 * pd)) / denominator)


def simplified_irb_capital(pd: float, lgd: float, ead: float, maturity_adjustment: float = 1.0) -> float:
    result = irb_comparison(pd, lgd, ead, maturity_adjustment, 1.0, 0.725)
    return result.capital_requirement


def irb_rwa_equivalent(capital: float) -> float:
    return validate_non_negative(capital, "Capital") * 12.5


def irb_comparison(
    pd: float,
    lgd: float,
    ead: float,
    maturity: float,
    standardised_risk_weight: float = 1.0,
    output_floor_percentage: float = 0.725,
    approach: IRBApproach = IRBApproach.ADVANCED,
) -> IRBComparisonResult:
    pd = validate_pd(pd)
    lgd = validate_lgd(lgd)
    ead = validate_non_negative(ead, "EAD")
    maturity = validate_positive(maturity, "Maturity")
    validate_non_negative(output_floor_percentage, "Output floor percentage")
    correlation = corporate_correlation(max(pd, 0.0003))
    normal = NormalDist()
    # Educational corporate IRB-style unexpected loss approximation.
    capital_rate = lgd * normal.cdf((normal.inv_cdf(pd) + correlation**0.5 * normal.inv_cdf(0.999)) / (1 - correlation) ** 0.5) - pd * lgd
    maturity_adjustment = max(0.5, min(maturity / 2.5, 2.0))
    capital = max(capital_rate * maturity_adjustment * ead, 0.0)
    model_rwa = capital * 12.5
    std_rwa = standardized_rwa(ead, standardised_risk_weight)
    floor_rwa = output_floor_percentage * std_rwa
    final_rwa = max(model_rwa, floor_rwa)
    return IRBComparisonResult(
        approach=approach,
        pd=pd,
        lgd=lgd,
        ead=ead,
        maturity=maturity,
        correlation=correlation,
        capital_requirement=capital,
        model_based_rwa=model_rwa,
        standardised_rwa=std_rwa,
        final_rwa=final_rwa,
        output_floor_rwa=floor_rwa,
        output_floor_applied=floor_rwa > model_rwa,
        assumptions=("Educational corporate IRB-style approximation; it does not cover all Basel exposure classes or adjustments.",),
    )
