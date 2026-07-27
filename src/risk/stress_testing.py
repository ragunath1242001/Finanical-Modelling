from __future__ import annotations

from dataclasses import dataclass

from src.risk.basel import capital_ratios
from src.risk.capital_bridge import CapitalBridgeInput, capital_movement_bridge
from src.risk.expected_loss import point_in_time_expected_loss
from src.risk.ifrs9 import expected_credit_loss
from src.risk.scenarios import SCENARIOS, EconomicScenario, scenario_by_name
from src.risk.validation import validate_non_negative, validate_positive


@dataclass(frozen=True)
class ManagementAction:
    dividend_reduction: float = 0.0
    capital_raise: float = 0.0
    rwa_reduction: float = 0.0
    provision_overlay: float = 0.0


@dataclass(frozen=True)
class StressCapitalResult:
    scenario: str
    baseline_ecl: float
    stressed_ecl: float
    provision_increase: float
    pre_management_cet1: float
    pre_management_cet1_ratio: float
    post_management_cet1: float
    post_management_cet1_ratio: float
    threshold: float
    breach_indicator: bool
    absolute_change: float
    percentage_change: float
    steps: tuple[str, ...]


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


def stress_capital_chain(
    pd: float,
    lgd: float,
    ead: float,
    cet1: float,
    at1: float,
    tier2: float,
    rwa_amount: float,
    scenario: EconomicScenario,
    threshold: float = 0.045,
    management_action: ManagementAction | None = None,
) -> StressCapitalResult:
    validate_positive(rwa_amount, "RWA")
    baseline = point_in_time_expected_loss(pd, lgd, ead).expected_loss
    stressed_pd = min(pd * scenario.pd_multiplier, 1.0)
    stressed_lgd = min(lgd * scenario.lgd_multiplier, 1.0)
    stressed_ead = ead * scenario.ead_multiplier
    stressed = point_in_time_expected_loss(stressed_pd, stressed_lgd, stressed_ead).expected_loss
    provision_increase = max(0.0, stressed - baseline)
    pre_bridge = capital_movement_bridge(
        CapitalBridgeInput(
            opening_cet1=cet1,
            profit_before_impairment=0.0,
            incremental_impairment=provision_increase,
            tax_rate=0.0,
        )
    )
    pre_ratio = capital_ratios(pre_bridge.closing_cet1, at1, tier2, rwa_amount)["cet1_ratio"]
    action = management_action or ManagementAction()
    validate_non_negative(action.dividend_reduction, "Dividend reduction")
    validate_non_negative(action.capital_raise, "Capital raise")
    validate_non_negative(action.rwa_reduction, "RWA reduction")
    validate_non_negative(action.provision_overlay, "Provision overlay")
    post_cet1 = pre_bridge.closing_cet1 + action.dividend_reduction + action.capital_raise - action.provision_overlay
    post_rwa = max(rwa_amount - action.rwa_reduction, 1e-9)
    post_ratio = capital_ratios(post_cet1, at1, tier2, post_rwa)["cet1_ratio"]
    return StressCapitalResult(
        scenario=scenario.name,
        baseline_ecl=baseline,
        stressed_ecl=stressed,
        provision_increase=provision_increase,
        pre_management_cet1=pre_bridge.closing_cet1,
        pre_management_cet1_ratio=pre_ratio,
        post_management_cet1=post_cet1,
        post_management_cet1_ratio=post_ratio,
        threshold=threshold,
        breach_indicator=post_ratio < threshold,
        absolute_change=stressed - baseline,
        percentage_change=((stressed - baseline) / baseline) if baseline else 0.0,
        steps=(
            f"{scenario.name} scenario -> PD x{scenario.pd_multiplier:.2f}, LGD x{scenario.lgd_multiplier:.2f}, EAD x{scenario.ead_multiplier:.2f}.",
            "Stressed ECL -> incremental provision -> CET1 bridge -> capital ratio.",
        ),
    )


def stress_capital_chain_by_name(*args, scenario_name: str = "Baseline", **kwargs) -> StressCapitalResult:
    return stress_capital_chain(*args, scenario=scenario_by_name(scenario_name), **kwargs)
