"""Shared deterministic economic scenario framework."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.risk.validation import RiskValidationError, validate_non_negative, validate_probability, validate_weights


@dataclass(frozen=True)
class EconomicScenario:
    name: str
    probability: float
    gdp_growth: float = 0.0
    unemployment_rate: float = 0.06
    interest_rate_change: float = 0.0
    house_price_growth: float = 0.0
    inflation: float = 0.02
    sector_stress: float = 0.0
    pd_multiplier: float = 1.0
    lgd_multiplier: float = 1.0
    ead_multiplier: float = 1.0
    revenue_multiplier: float = 1.0
    funding_cost_multiplier: float = 1.0


BASELINE_SCENARIO = EconomicScenario("Baseline", 0.50, gdp_growth=0.012)
UPSIDE_SCENARIO = EconomicScenario(
    "Upside",
    0.15,
    gdp_growth=0.025,
    unemployment_rate=0.05,
    house_price_growth=0.025,
    pd_multiplier=0.85,
    lgd_multiplier=0.95,
    ead_multiplier=0.98,
    revenue_multiplier=1.03,
    funding_cost_multiplier=0.95,
)
ADVERSE_SCENARIO = EconomicScenario(
    "Adverse",
    0.25,
    gdp_growth=-0.015,
    unemployment_rate=0.085,
    interest_rate_change=0.015,
    house_price_growth=-0.08,
    inflation=0.045,
    sector_stress=0.25,
    pd_multiplier=1.45,
    lgd_multiplier=1.15,
    ead_multiplier=1.03,
    revenue_multiplier=0.92,
    funding_cost_multiplier=1.20,
)
SEVERE_SCENARIO = EconomicScenario(
    "Severe",
    0.10,
    gdp_growth=-0.045,
    unemployment_rate=0.12,
    interest_rate_change=0.025,
    house_price_growth=-0.18,
    inflation=0.065,
    sector_stress=0.45,
    pd_multiplier=2.10,
    lgd_multiplier=1.35,
    ead_multiplier=1.08,
    revenue_multiplier=0.82,
    funding_cost_multiplier=1.45,
)

DEFAULT_SCENARIO_SET = (UPSIDE_SCENARIO, BASELINE_SCENARIO, ADVERSE_SCENARIO, SEVERE_SCENARIO)


def validate_scenarios(scenarios: Iterable[EconomicScenario], require_weight_sum: bool = True) -> tuple[EconomicScenario, ...]:
    items = tuple(scenarios)
    if not items:
        raise RiskValidationError("At least one scenario is required.")
    names = [scenario.name for scenario in items]
    if len(names) != len(set(names)):
        raise RiskValidationError("Scenario names must be unique.")
    for scenario in items:
        if not scenario.name.strip():
            raise RiskValidationError("Scenario name cannot be blank.")
        validate_probability(scenario.probability, "Scenario probability")
        validate_non_negative(scenario.pd_multiplier, "PD multiplier")
        validate_non_negative(scenario.lgd_multiplier, "LGD multiplier")
        validate_non_negative(scenario.ead_multiplier, "EAD multiplier")
        validate_non_negative(scenario.revenue_multiplier, "Revenue multiplier")
        validate_non_negative(scenario.funding_cost_multiplier, "Funding-cost multiplier")
    if require_weight_sum:
        validate_weights([scenario.probability for scenario in items])
    return items


def scenario_by_name(name: str, scenarios: Iterable[EconomicScenario] = DEFAULT_SCENARIO_SET) -> EconomicScenario:
    for scenario in scenarios:
        if scenario.name == name:
            return scenario
    raise RiskValidationError(f"Unknown scenario: {name}.")


def apply_scenario_parameter(base_value: float, multiplier: float, cap: float | None = None) -> tuple[float, bool]:
    validate_non_negative(base_value, "Base value")
    validate_non_negative(multiplier, "Scenario multiplier")
    raw = base_value * multiplier
    if cap is not None and raw > cap:
        return cap, True
    return raw, False


def weighted_sum(values_by_scenario: dict[str, float], scenarios: Iterable[EconomicScenario]) -> float:
    scenario_tuple = validate_scenarios(scenarios)
    missing = {scenario.name for scenario in scenario_tuple} - set(values_by_scenario)
    if missing:
        raise RiskValidationError(f"Missing scenario values for: {sorted(missing)}.")
    return sum(values_by_scenario[scenario.name] * scenario.probability for scenario in scenario_tuple)


SCENARIOS = {
    "Baseline": {"pd_multiplier": BASELINE_SCENARIO.pd_multiplier, "lgd_multiplier": BASELINE_SCENARIO.lgd_multiplier, "revenue_shock": BASELINE_SCENARIO.revenue_multiplier - 1},
    "Adverse": {"pd_multiplier": ADVERSE_SCENARIO.pd_multiplier, "lgd_multiplier": ADVERSE_SCENARIO.lgd_multiplier, "revenue_shock": ADVERSE_SCENARIO.revenue_multiplier - 1},
    "Severe": {"pd_multiplier": SEVERE_SCENARIO.pd_multiplier, "lgd_multiplier": SEVERE_SCENARIO.lgd_multiplier, "revenue_shock": SEVERE_SCENARIO.revenue_multiplier - 1},
}
