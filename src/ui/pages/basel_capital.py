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
from src.risk.basel import CapitalStack, calculate_capital_stack, capital_after_provision, capital_ratios, standardised_rwa
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
from src.risk.irb import irb_comparison, irb_rwa_equivalent, simplified_irb_capital, standardized_rwa
from src.risk.liquidity import compliance, lcr, leverage_ratio, nsfr
from src.risk.reverse_stress import required_loss_for_target, reverse_stress_solver
from src.risk.stress_testing import SCENARIOS, stress_ecl
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

def render_basel_capital_page(ctx: PortfolioContext) -> None:
    globals().update(_unpack(ctx))
    modelling_depth_label(
        "Analytical Engine",
        "Compare standardised RWA, simplified IRB-style RWA and capital ratios.",
        "Exposure x risk weight, educational corporate IRB-style capital, output-floor comparison.",
        "Illustrative risk weights and simplified IRB assumptions.",
        "Not a full Basel/CRR implementation and not suitable for regulatory reporting.",
    )
    exposure = st.number_input("Exposure", min_value=1.0, value=1_000_000.0, step=50_000.0)
    risk_weight = st.slider("Standardized risk weight", 0.0, 1.5, 0.75, 0.05)
    pd_input = st.slider("IRB PD", 0.001, 0.5, 0.035, 0.001)
    lgd_input = st.slider("IRB LGD", 0.05, 0.95, 0.45, 0.01)
    std_result = standardised_rwa("custom", exposure, risk_weight)
    irb_result = irb_comparison(pd_input, lgd_input, exposure, 2.5, risk_weight, 0.725)
    basel_stack = calculate_capital_stack(CapitalStack(120_000, 20_000, 30_000, std_result.rwa, total_exposure_measure=exposure))
    metrics_row([("Standardized RWA", f"EUR {std_result.rwa:,.0f}"), ("IRB capital estimate", f"EUR {irb_result.capital_requirement:,.0f}"), ("Final RWA after floor", f"EUR {irb_result.final_rwa:,.0f}"), ("CET1 ratio", f"{basel_stack.cet1_ratio:.2%}")])
    st.dataframe(pd.DataFrame([std_result.__dict__ | {"assumptions": "; ".join(std_result.assumptions)}, irb_result.__dict__ | {"assumptions": "; ".join(irb_result.assumptions)}]), width="stretch")
    st.warning("IRB output is a simplified educational approximation, not a full regulatory IRB implementation.")
    teaching_block(
        "How do standardized and internal-model capital views differ?",
        "Standardized RWA = exposure x risk weight. Simplified IRB capital = sqrt(PD) x LGD x EAD x 1.06.",
        "IFRS 9 asks what losses are expected; IRB asks how much capital should be held for risk. Similar inputs serve different regulatory objectives.",
        "I compare standardized and internal-model views while clearly labeling the IRB approximation as educational.",
    )


def render_page(ctx: PortfolioContext) -> None:
    render_basel_capital_page(ctx)


