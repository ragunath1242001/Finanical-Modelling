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
from src.risk.ifrs9 import assign_stage, calculate_ifrs9, calculate_ifrs9_lifetime_ecl, expected_credit_loss, scenario_weighted_ifrs9_ecl
from src.risk.ifrs9_staging import StagingRequest, assign_ifrs9_stage
from src.risk.ifrs9_scenario_engine import ecl_bridge, scenario_weighted_ecl, stage_migration_table
from src.risk.irb import irb_rwa_equivalent, simplified_irb_capital, standardized_rwa
from src.risk.liquidity import compliance, lcr, leverage_ratio, nsfr
from src.risk.reverse_stress import required_loss_for_target, reverse_stress_solver
from src.risk.scenarios import ADVERSE_SCENARIO, BASELINE_SCENARIO, UPSIDE_SCENARIO, EconomicScenario
from src.risk.stress_testing import SCENARIOS, stress_ecl
from src.risk.xva import xva_summary
from src.model_risk.inventory import model_by_id
from src.model_risk.reporting import model_confidence
from src.model_risk.limitations import limitations_frame
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

def render_ifrs9_ecl_calculator(ctx: PortfolioContext) -> None:
    globals().update(_unpack(ctx))
    modelling_depth_label(
        "Analytical Engine",
        "Assign an educational IFRS 9 stage and calculate 12-month versus lifetime ECL.",
        "Stage rules -> PD term structure -> marginal PD -> LGD -> EAD -> discount factor -> provision.",
        "Flat annual PD/LGD/EAD inputs are expanded into an educational term structure.",
        "Not an institution-specific IFRS 9 policy or accounting engine.",
    )
    col1, col2, col3 = st.columns(3)
    pd_model = model_by_id("PD-LOGIT-001")
    lgd_model = model_by_id("LGD-COLL-001")
    st.caption(
        f"PD model: {pd_model.model_id} v{pd_model.model_version}, confidence: {model_confidence(pd_model.model_id)} | "
        f"LGD model: {lgd_model.model_id} v{lgd_model.model_version}, confidence: {model_confidence(lgd_model.model_id)}"
    )
    st.dataframe(limitations_frame().query("model_id in ['PD-LOGIT-001', 'LGD-COLL-001']"), width="stretch")
    pd_input = col1.slider("PD", 0.0, 1.0, portfolio_pd, 0.005)
    lgd_input = col2.slider("LGD", 0.0, 1.0, portfolio_lgd, 0.01)
    ead_input = col3.number_input("EAD", min_value=0.0, value=250_000.0, step=10_000.0)
    dpd = st.slider("Days past due", 0, 150, 0)
    score_change = st.slider("Credit score change", -200, 50, -20)
    stress_flag = st.selectbox("Industry stress", ["normal", "high", "severe"])
    default_flag = st.checkbox("Default flag")
    staging = assign_ifrs9_stage(StagingRequest(days_past_due=dpd, default_flag=default_flag, rating_deterioration_notches=2 if score_change <= -60 else 0, sector_stress=stress_flag))
    stage = int(staging.stage)
    life_years = st.slider("Remaining lifetime years", 1, 7, 4)
    discount_rate = st.slider("Effective interest rate for discounting", 0.0, 0.15, 0.03, 0.005)
    calc = calculate_ifrs9_lifetime_ecl([pd_input] * life_years, [lgd_input] * life_years, [ead_input] * life_years, discount_rate, stage)
    metrics_row([("Stage", str(stage)), ("12-month ECL", f"EUR {calc.twelve_month_ecl:,.0f}"), ("Lifetime ECL", f"EUR {calc.lifetime_ecl:,.0f}"), ("Provision", f"EUR {calc.provision:,.0f}")])
    st.info(staging.explanation)
    st.dataframe(calc.period_table, width="stretch")
    teaching_block(
        "Why does a loan move between Stage 1, Stage 2, and Stage 3?",
        " -> ".join(calc.steps),
        "Stage 2 is based on significant increase in credit risk, not only default. Higher provisions reduce profit, retained earnings, and CET1.",
        "IFRS 9 asks what losses are expected. Stage 1 uses 12-month ECL, while Stage 2 and Stage 3 use lifetime ECL in this simplified model.",
    )


def render_ifrs9_scenario_ecl_engine(ctx: PortfolioContext) -> None:
    globals().update(_unpack(ctx))
    st.subheader("IFRS 9 Scenario ECL Engine")
    st.write("Scenario-weighted ECL with lifetime PD, stage migration, and provision movement analysis.")
    u1, u2, u3 = st.columns(3)
    upside_weight = u1.slider("Upside weight", 0.0, 1.0, 0.20, 0.05)
    baseline_weight = u2.slider("Baseline weight", 0.0, 1.0, 0.55, 0.05)
    downside_weight = u3.slider("Downside weight", 0.0, 1.0, 0.25, 0.05)
    total_weight = max(upside_weight + baseline_weight + downside_weight, 0.0001)
    downside_pd = st.slider("Downside PD multiplier", 1.0, 3.0, 1.65, 0.05)
    downside_lgd = st.slider("Downside LGD multiplier", 1.0, 2.0, 1.20, 0.05)
    scenarios = {
        "Upside": {"weight": upside_weight / total_weight, "pd_multiplier": 0.85, "lgd_multiplier": 0.95},
        "Baseline": {"weight": baseline_weight / total_weight, "pd_multiplier": 1.00, "lgd_multiplier": 1.00},
        "Downside": {"weight": downside_weight / total_weight, "pd_multiplier": downside_pd, "lgd_multiplier": downside_lgd},
    }
    life = st.slider("Remaining life years for Stage 2/3", 1.0, 8.0, 4.0, 0.5)
    scenario_loans, scenario_summary = scenario_weighted_ecl(loans_raw, scenarios, life)
    structured = scenario_weighted_ifrs9_ecl(
        [portfolio_pd] * int(life),
        [portfolio_lgd] * int(life),
        [portfolio_ead] * int(life),
        0.03,
        2,
        (
            EconomicScenario("Upside", scenarios["Upside"]["weight"], pd_multiplier=0.85, lgd_multiplier=0.95),
            EconomicScenario("Baseline", scenarios["Baseline"]["weight"]),
            EconomicScenario("Downside", scenarios["Downside"]["weight"], pd_multiplier=downside_pd, lgd_multiplier=downside_lgd),
        ),
    )
    weighted_ecl = float(scenario_loans["weighted_ecl"].sum())
    baseline_ecl = float(scenario_summary.loc[scenario_summary["scenario"].eq("Baseline"), "scenario_ecl"].iloc[0])
    migration = stage_migration_table(loans_raw, scenarios["Downside"]["pd_multiplier"])
    stage_migration_effect = max(0.0, weighted_ecl - baseline_ecl) * 0.35
    bridge = ecl_bridge(
        opening_ecl=baseline_ecl,
        new_lending=baseline_ecl * 0.08,
        repayments=baseline_ecl * 0.05,
        stage_migration=stage_migration_effect,
        macro_overlay=max(0.0, weighted_ecl - baseline_ecl) * 0.65,
    )
    metrics_row(
        [
            ("Baseline ECL", f"EUR {baseline_ecl:,.0f}"),
            ("Weighted ECL", f"EUR {weighted_ecl:,.0f}"),
            ("Overlay increase", f"EUR {max(0.0, weighted_ecl - baseline_ecl):,.0f}"),
            ("Scenario weights", f"{scenarios['Upside']['weight']:.0%}/{scenarios['Baseline']['weight']:.0%}/{scenarios['Downside']['weight']:.0%}"),
        ]
    )
    tab1, tab2, tab3, tab4 = st.tabs(["Scenario ECL", "Stage Migration", "ECL Bridge", "Loan Detail"])
    with tab1:
        st.dataframe(scenario_summary, width="stretch")
        st.download_button(
            "Download IFRS 9 scenario ECL CSV",
            dataframe_csv_bytes(scenario_summary),
            file_name="ifrs9_scenario_ecl.csv",
            mime="text/csv",
        )
        st.plotly_chart(px.bar(scenario_summary, x="scenario", y="scenario_ecl", color="scenario", title="ECL by macro scenario"), width="stretch")
    with tab2:
        st.dataframe(migration, width="stretch")
    with tab3:
        st.dataframe(bridge, width="stretch")
        st.download_button(
            "Download ECL bridge CSV",
            dataframe_csv_bytes(bridge),
            file_name="ifrs9_ecl_bridge.csv",
            mime="text/csv",
        )
        st.plotly_chart(px.bar(bridge, x="component", y="amount", title="Provision movement bridge"), width="stretch")
    with tab4:
        st.dataframe(scenario_loans[["loan_id", "customer_id", "base_stage", "upside_ecl", "baseline_ecl", "downside_ecl", "weighted_ecl"]].sort_values("weighted_ecl", ascending=False).head(30), width="stretch")
        st.write("Structured portfolio-level lifetime ECL period table")
        st.dataframe(structured.period_table, width="stretch")
    teaching_block(
        "How does IFRS 9 use forward-looking scenarios?",
        "Weighted ECL = Upside ECL x weight + Baseline ECL x weight + Downside ECL x weight.",
        "IFRS 9 provisions should reflect forward-looking information. Scenario weights make the result more realistic than a single deterministic forecast.",
        "This engine shows loan-level stage assignment, lifetime PD, macro scenario weighting, stage migration, and an ECL bridge from opening to closing provision.",
    )

def render_ifrs9_page(ctx: PortfolioContext) -> None:
    globals().update(_unpack(ctx))
    ifrs9_mode = st.segmented_control("Mode", ["ECL Calculator", "Scenario ECL Engine"], default="ECL Calculator")
    if ifrs9_mode == "Scenario ECL Engine":
        render_ifrs9_scenario_ecl_engine(ctx)
    else:
        render_ifrs9_ecl_calculator(ctx)


def render_page(ctx: PortfolioContext) -> None:
    render_ifrs9_page(ctx)


