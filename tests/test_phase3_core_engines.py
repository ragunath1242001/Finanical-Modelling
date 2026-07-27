from __future__ import annotations

import pytest

from src.risk.basel import CapitalStack, calculate_capital_stack, capital_ratios, standardised_rwa
from src.risk.capital_bridge import CapitalBridgeInput, capital_movement_bridge
from src.risk.ead import amortising_ead_schedule, revolving_ead, scenario_adjusted_ead
from src.risk.expected_loss import lifetime_expected_credit_loss, point_in_time_expected_loss
from src.risk.ifrs9 import calculate_ifrs9_lifetime_ecl, scenario_weighted_ifrs9_ecl
from src.risk.ifrs9_staging import IFRS9Stage, StagingRequest, assign_ifrs9_stage
from src.risk.irb import irb_comparison
from src.risk.lgd import downturn_lgd, recovery_based_lgd, validate_lgd
from src.risk.pd import build_pd_term_structure, scenario_adjusted_pd, validate_pd
from src.risk.provision_bridge import ProvisionBridgeInput, provision_movement_bridge
from src.risk.reverse_stress import solve_pd_multiplier_for_cet1_threshold
from src.risk.scenarios import ADVERSE_SCENARIO, BASELINE_SCENARIO, SEVERE_SCENARIO, EconomicScenario, validate_scenarios
from src.risk.stress_testing import stress_capital_chain
from src.risk.validation import RiskValidationError


def test_pd_lgd_ead_validation_boundaries() -> None:
    with pytest.raises(RiskValidationError):
        validate_pd(-0.01)
    with pytest.raises(RiskValidationError):
        validate_pd(1.01)
    with pytest.raises(RiskValidationError):
        validate_lgd(1.2)
    with pytest.raises(RiskValidationError):
        scenario_adjusted_ead(-1, 1)
    assert validate_pd(0) == 0
    assert validate_pd(1) == 1
    assert validate_lgd(0) == 0


def test_revolving_ead_and_ccf_boundaries() -> None:
    assert revolving_ead(100, 50, 0).base_ead == 100
    assert revolving_ead(100, 50, 1).base_ead == 150
    with pytest.raises(RiskValidationError):
        revolving_ead(100, 50, 1.1)
    assert revolving_ead(100, 50, 0.25).base_ead >= 100


def test_amortising_ead_schedule_and_mismatch_validation() -> None:
    assert amortising_ead_schedule(100, [10, 10], [0, 5]) == [90, 85]
    with pytest.raises(RiskValidationError):
        amortising_ead_schedule(100, [], [])


def test_expected_loss_monotonicity_and_discounting() -> None:
    base = point_in_time_expected_loss(0.01, 0.4, 100).expected_loss
    assert point_in_time_expected_loss(0.02, 0.4, 100).expected_loss >= base
    assert point_in_time_expected_loss(0.01, 0.5, 100).expected_loss >= base
    assert point_in_time_expected_loss(0.01, 0.4, 200).expected_loss >= base
    discounted = lifetime_expected_credit_loss([0.1, 0.1], [0.5, 0.5], [100, 100], [0.95, 0.90])
    assert discounted.total_discounted_ecl <= discounted.total_undiscounted_ecl


def test_pd_term_structure_invariants() -> None:
    rows = build_pd_term_structure([0.1, 0.2, 0.3])
    assert [row.cumulative_pd for row in rows] == sorted(row.cumulative_pd for row in rows)
    survival = [row.survival_probability_start for row in rows] + [rows[-1].survival_probability_end]
    assert survival == sorted(survival, reverse=True)


def test_scenario_weight_validation() -> None:
    validate_scenarios((EconomicScenario("Standalone", 1.0),))
    with pytest.raises(RiskValidationError):
        validate_scenarios((EconomicScenario("A", 0.4), EconomicScenario("B", 0.4)))
    with pytest.raises(RiskValidationError):
        validate_scenarios((EconomicScenario("A", 0.5), EconomicScenario("A", 0.5)))


def test_ifrs9_stage_precedence_and_horizons() -> None:
    result = assign_ifrs9_stage(StagingRequest(days_past_due=45, default_flag=True, watchlist=True))
    assert result.stage == IFRS9Stage.STAGE_3
    stage1 = calculate_ifrs9_lifetime_ecl([0.1, 0.1, 0.1], [0.5] * 3, [100] * 3, 0.0, IFRS9Stage.STAGE_1)
    stage2 = calculate_ifrs9_lifetime_ecl([0.1, 0.1, 0.1], [0.5] * 3, [100] * 3, 0.0, IFRS9Stage.STAGE_2)
    assert stage1.provision == stage1.twelve_month_ecl
    assert stage2.provision == stage2.lifetime_ecl
    assert len(stage2.period_table) == 3


def test_scenario_weighted_lifetime_ecl() -> None:
    result = scenario_weighted_ifrs9_ecl(
        [0.02, 0.025],
        [0.4, 0.42],
        [100_000, 90_000],
        0.03,
        IFRS9Stage.STAGE_2,
        (EconomicScenario("Baseline", 1.0),),
    )
    assert result.weighted_ecl > 0
    assert set(result.scenario_table["scenario"]) == {"Baseline"}


def test_provision_and_capital_bridges_reconcile() -> None:
    provision = provision_movement_bridge(ProvisionBridgeInput(opening_allowance=100, new_originations=20, repayments=5, write_offs=10))
    assert provision.reconciles
    assert provision.closing_allowance == 105
    capital = capital_movement_bridge(CapitalBridgeInput(opening_cet1=1000, profit_before_impairment=100, incremental_impairment=50, tax_rate=0.2, dividends=10))
    assert capital.reconciles
    assert capital.closing_cet1 == 1050


def test_capital_rwa_and_irb_output_floor() -> None:
    assert capital_ratios(100, 10, 10, 1000)["cet1_ratio"] == 0.1
    with pytest.raises(RiskValidationError):
        capital_ratios(100, 10, 10, 0)
    std = standardised_rwa("retail", 1000)
    assert std.rwa == 750
    stack = calculate_capital_stack(CapitalStack(100, 10, 10, 750, total_exposure_measure=2000))
    assert stack.cet1_ratio == 100 / 750
    irb = irb_comparison(0.02, 0.45, 1000, 2.5, standardised_risk_weight=0.75, output_floor_percentage=0.725)
    assert irb.final_rwa == max(irb.model_based_rwa, irb.output_floor_rwa)


def test_stress_chain_and_reverse_stress() -> None:
    baseline = stress_capital_chain(0.02, 0.4, 100_000, 10_000, 500, 500, 80_000, BASELINE_SCENARIO)
    severe = stress_capital_chain(0.02, 0.4, 100_000, 10_000, 500, 500, 80_000, SEVERE_SCENARIO)
    assert severe.stressed_ecl >= baseline.stressed_ecl
    reverse = solve_pd_multiplier_for_cet1_threshold(10_000, 500, 500, 80_000, 100_000, 0.02, 0.4, 0.12)
    assert reverse["cet1_ratio"] <= 0.120001


def test_lgd_recovery_cases() -> None:
    full = recovery_based_lgd(100, 100, 0, 1, 0, 0, 0)
    assert full.lgd == 0
    zero_recovery = recovery_based_lgd(100, 0, 0, 0, 0, 0, 0)
    assert zero_recovery.lgd == 1
    assert downturn_lgd(0.5, 3).lgd == 1
