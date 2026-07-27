from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.risk.ead import scenario_adjusted_ead
from src.risk.expected_loss import LifetimeECLResult, discount_factor, lifetime_expected_credit_loss, point_in_time_expected_loss
from src.risk.ifrs9_staging import IFRS9Stage, StagingRequest, assign_ifrs9_stage
from src.risk.lgd import downturn_lgd
from src.risk.pd import scenario_adjusted_pd
from src.risk.scenarios import EconomicScenario, validate_scenarios


@dataclass(frozen=True)
class IFRS9ECLResult:
    stage: IFRS9Stage
    twelve_month_ecl: float
    lifetime_ecl: float
    provision: float
    period_table: pd.DataFrame
    assumptions: tuple[str, ...]
    warnings: tuple[str, ...]
    steps: tuple[str, ...]


@dataclass(frozen=True)
class ScenarioECLResult:
    selected_stage: IFRS9Stage
    weighted_ecl: float
    scenario_table: pd.DataFrame
    period_table: pd.DataFrame
    assumptions: tuple[str, ...]
    warnings: tuple[str, ...]


def expected_credit_loss(pd: float, lgd: float, ead: float) -> float:
    return round(point_in_time_expected_loss(pd, lgd, ead).expected_loss, 6)


def assign_stage(
    days_past_due: int,
    credit_score_change: int = 0,
    industry_stress: str = "normal",
    default_flag: bool = False,
    sicr_threshold: int = 60,
) -> tuple[int, str]:
    result = assign_ifrs9_stage(
        StagingRequest(
            days_past_due=days_past_due,
            default_flag=default_flag,
            rating_deterioration_notches=2 if credit_score_change <= -abs(sicr_threshold) else 0,
            sector_stress=industry_stress,
        )
    )
    return int(result.stage), result.explanation


def calculate_ifrs9_lifetime_ecl(
    conditional_pds: list[float],
    lgds: list[float],
    eads: list[float],
    annual_discount_rate: float,
    stage: int | IFRS9Stage,
) -> IFRS9ECLResult:
    selected_stage = IFRS9Stage(stage)
    discount_factors = [discount_factor(period, annual_discount_rate) for period in range(1, len(conditional_pds) + 1)]
    lifetime = lifetime_expected_credit_loss(conditional_pds, lgds, eads, discount_factors)
    horizon_periods = min(1, len(lifetime.periods)) if selected_stage == IFRS9Stage.STAGE_1 else len(lifetime.periods)
    selected_periods = lifetime.periods[:horizon_periods]
    twelve_month_ecl = selected_periods[0].discounted_ecl if lifetime.periods else 0.0
    lifetime_ecl = lifetime.total_discounted_ecl
    provision = twelve_month_ecl if selected_stage == IFRS9Stage.STAGE_1 else lifetime_ecl
    table = pd.DataFrame([period.__dict__ for period in lifetime.periods])
    return IFRS9ECLResult(
        stage=selected_stage,
        twelve_month_ecl=twelve_month_ecl,
        lifetime_ecl=lifetime_ecl,
        provision=provision,
        period_table=table,
        assumptions=(
            "Stage 1 uses an educational 12-month horizon approximation based on period 1 marginal default risk.",
            "Stage 2 and Stage 3 use lifetime ECL across the full supplied term.",
        ),
        warnings=("This is an educational IFRS 9 approximation; institution-specific policies may differ.",),
        steps=("Base PD -> marginal PD -> LGD -> EAD -> discount factor -> period ECL -> selected provision.",),
    )


def scenario_weighted_ifrs9_ecl(
    base_conditional_pds: list[float],
    base_lgds: list[float],
    base_eads: list[float],
    annual_discount_rate: float,
    stage: int | IFRS9Stage,
    scenarios: tuple[EconomicScenario, ...],
) -> ScenarioECLResult:
    scenario_tuple = validate_scenarios(scenarios)
    rows = []
    period_frames = []
    weighted = 0.0
    for scenario in scenario_tuple:
        scenario_pds = [scenario_adjusted_pd(pd, scenario.pd_multiplier).stressed_pd for pd in base_conditional_pds]
        scenario_lgds = [downturn_lgd(lgd, scenario.lgd_multiplier).lgd for lgd in base_lgds]
        scenario_eads = [scenario_adjusted_ead(ead, scenario.ead_multiplier).stressed_ead for ead in base_eads]
        result = calculate_ifrs9_lifetime_ecl(scenario_pds, scenario_lgds, scenario_eads, annual_discount_rate, stage)
        weighted += scenario.probability * result.provision
        rows.append(
            {
                "scenario": scenario.name,
                "weight": scenario.probability,
                "pd_multiplier": scenario.pd_multiplier,
                "lgd_multiplier": scenario.lgd_multiplier,
                "ead_multiplier": scenario.ead_multiplier,
                "scenario_ecl": result.provision,
            }
        )
        frame = result.period_table.copy()
        frame["scenario"] = scenario.name
        period_frames.append(frame)
    return ScenarioECLResult(
        selected_stage=IFRS9Stage(stage),
        weighted_ecl=weighted,
        scenario_table=pd.DataFrame(rows),
        period_table=pd.concat(period_frames, ignore_index=True) if period_frames else pd.DataFrame(),
        assumptions=("Scenario-weighted ECL = sum scenario probability x scenario ECL.",),
        warnings=("Scenario weights and multipliers are educational assumptions.",),
    )


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
