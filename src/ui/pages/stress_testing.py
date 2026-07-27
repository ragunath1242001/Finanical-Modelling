from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.financial_crime.aml import aml_alerts
from src.financial_crime.fraud import alert_queue, threshold_summary
from src.forecasting.forecasting import twelve_month_forecast
from src.governance.audit import log_event, read_events
from src.governance.ai_governance import ai_act_control_assessment, ai_risk_tier, fairness_gap
from src.governance.dora import dora_incident_classification, resilience_score, third_party_register
from src.governance.drift import mean_drift
from src.governance.explainability import pd_reason_codes
from src.governance.lineage import LINEAGE_STEPS
from src.governance.lod_workflows import issue_queue
from src.governance.model_risk import model_inventory, validation_findings
from src.governance.reconciliation import reconcile_exposure
from src.reporting.corep import corep_metrics
from src.reporting.downloads import capital_summary_report, dataframe_csv_bytes, pdf_report_bytes, validation_report
from src.reporting.executive import management_actions
from src.reporting.finrep import finrep_metrics
from src.reporting.portfolio import capital_impact_waterfall
from src.risk.basel import capital_after_provision, capital_ratios
from src.risk.climate import climate_adjusted_credit_risk, climate_portfolio_table
from src.risk.credit_model_lab import (
    calibration_table,
    confusion_matrix_frame,
    feature_importance,
    model_comparison_table,
    population_stability_index,
    prepare_model_frame,
    roc_curve_frame,
    score_with_grades,
    train_credit_models,
)
from src.risk.crr3 import crr3_total_rwa, cva_lite_capital, operational_risk_sma, output_floor
from src.risk.ifrs9 import assign_stage, calculate_ifrs9, expected_credit_loss
from src.risk.ifrs9_scenario_engine import ecl_bridge, scenario_weighted_ecl, stage_migration_table
from src.risk.irb import irb_rwa_equivalent, simplified_irb_capital, standardized_rwa
from src.risk.liquidity import compliance, lcr, leverage_ratio, nsfr
from src.risk.reverse_stress import required_loss_for_target, reverse_stress_solver
from src.risk.scenarios import EconomicScenario, scenario_by_name
from src.risk.stress_testing import SCENARIOS, stress_capital_chain, stress_ecl
from src.risk.xva import xva_summary
from src.ui.components import metrics_row, modelling_depth_label, render_capability_cards, teaching_block
from src.ui.context import (
    PortfolioContext,
    data_dictionary_pdf as context_data_dictionary_pdf,
    dataset_summary as context_dataset_summary,
    field_inventory as context_field_inventory,
)

def _unpack(ctx: PortfolioContext):
    data = ctx.data
    return {
        "customers": data.customers,
        "loans_raw": data.loans_raw,
        "transactions": data.transactions,
        "financials": data.financials,
        "scenario": ctx.scenario,
        "loans": ctx.loans,
        "portfolio_pd": ctx.portfolio_pd,
        "portfolio_lgd": ctx.portfolio_lgd,
        "portfolio_ead": ctx.portfolio_ead,
        "portfolio_ecl": ctx.portfolio_ecl,
        "base_rwa": ctx.base_rwa,
        "base_cet1": ctx.base_cet1,
        "at1": ctx.at1,
        "tier2": ctx.tier2,
        "stressed": ctx.stressed,
        "post_cet1": ctx.post_cet1,
        "ratios": ctx.ratios,
        "liq_lcr": ctx.liq_lcr,
        "liq_nsfr": ctx.liq_nsfr,
        "quality_table": ctx.quality_table,
        "quality_score": ctx.quality_score,
        "fraud_scored": ctx.fraud_scored,
        "aml_scored": ctx.aml_scored,
        "app_data": data,
    }

def render_stress_testing_page(ctx: PortfolioContext) -> None:
    globals().update(_unpack(ctx))
    modelling_depth_label(
        "Analytical Engine",
        "Connect macro scenario shocks to PD/LGD/EAD, ECL, provision and CET1 ratio.",
        "Scenario -> stressed risk parameters -> expected loss -> impairment bridge -> CET1 ratio.",
        "Educational scenario multipliers and simplified capital transmission.",
        "Not a supervisory stress-testing framework.",
    )
    pd_mult = st.slider("PD multiplier", 0.5, 3.0, SCENARIOS[scenario]["pd_multiplier"], 0.05)
    lgd_mult = st.slider("LGD multiplier", 0.5, 2.0, SCENARIOS[scenario]["lgd_multiplier"], 0.05)
    revenue_shock = st.slider("Revenue shock", -0.5, 0.2, SCENARIOS[scenario]["revenue_shock"], 0.01)
    selected_scenario = scenario_by_name(scenario)
    custom_scenario = EconomicScenario(
        selected_scenario.name,
        1.0,
        pd_multiplier=pd_mult,
        lgd_multiplier=lgd_mult,
        ead_multiplier=selected_scenario.ead_multiplier,
        revenue_multiplier=1 + revenue_shock,
    )
    structured = stress_capital_chain(portfolio_pd, portfolio_lgd, portfolio_ead, base_cet1, at1, tier2, base_rwa, custom_scenario)
    stressed_pd = min(portfolio_pd * pd_mult, 1.0)
    stressed_lgd = min(portfolio_lgd * lgd_mult, 1.0)
    metrics_row([("Stressed PD", f"{stressed_pd:.2%}"), ("Stressed LGD", f"{stressed_lgd:.2%}"), ("Provision increase", f"EUR {structured.provision_increase:,.0f}"), ("Post-stress CET1 ratio", f"{structured.post_management_cet1_ratio:.2%}")])
    waterfall = capital_impact_waterfall(base_cet1, structured.provision_increase, revenue_shock, structured.pre_management_cet1)
    st.plotly_chart(px.bar(waterfall, x="step", y="amount", title="Capital impact bridge"), width="stretch")
    teaching_block(
        "What happens to provisions and capital under adverse macroeconomic scenarios?",
        "Stressed ECL = stressed PD x stressed LGD x EAD; provision increase reduces CET1.",
        "Stress testing supports capital planning by showing whether management should reduce dividends, raise capital, slow risky growth, or tighten lending.",
        "I use baseline, adverse, and severe scenarios to connect macro shocks with PD, LGD, ECL, profit, and CET1 ratio impacts.",
    )


def render_page(ctx: PortfolioContext) -> None:
    render_stress_testing_page(ctx)


