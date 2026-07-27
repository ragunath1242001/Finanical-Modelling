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
from src.risk.ifrs9 import assign_stage, calculate_ifrs9, expected_credit_loss
from src.risk.ifrs9_scenario_engine import ecl_bridge, scenario_weighted_ecl, stage_migration_table
from src.risk.irb import irb_rwa_equivalent, simplified_irb_capital, standardized_rwa
from src.risk.liquidity import compliance, lcr, leverage_ratio, nsfr
from src.risk.reverse_stress import required_loss_for_target, reverse_stress_solver
from src.risk.stress_testing import SCENARIOS, stress_ecl
from src.risk.xva import xva_summary
from src.ui.components import metrics_row, render_capability_cards, teaching_block
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

def render_climate_risk_page(ctx: PortfolioContext) -> None:
    globals().update(_unpack(ctx))
    st.subheader("ESG and Climate Credit Risk")
    cp = climate_portfolio_table()
    sector = st.selectbox("Sector", cp["sector"])
    physical = st.selectbox("Physical risk", ["Low", "Medium", "High"], index=2)
    c1, c2, c3 = st.columns(3)
    carbon_price = c1.slider("Carbon price EUR/tCO2", 0.0, 250.0, 90.0, 5.0)
    collateral_decline = c2.slider("Collateral value decline", 0.0, 0.50, 0.15, 0.01)
    disorderly = c3.checkbox("Disorderly transition", value=True)
    climate = climate_adjusted_credit_risk(
        portfolio_pd,
        portfolio_lgd,
        portfolio_ead,
        sector,
        physical,
        carbon_price,
        collateral_decline,
        disorderly,
    )
    metrics_row(
        [
            ("PD multiplier", f"{climate['pd_multiplier']:.2f}x"),
            ("Adjusted PD", f"{climate['adjusted_pd']:.2%}"),
            ("Adjusted LGD", f"{climate['adjusted_lgd']:.2%}"),
            ("ECL increase", f"EUR {climate['ecl_increase']:,.0f}"),
        ]
    )
    st.plotly_chart(px.bar(cp, x="sector", y="exposure", color="physical_risk", title="Climate-sensitive exposure by sector"), width="stretch")
    st.dataframe(cp, width="stretch")
    teaching_block(
        "How can climate and ESG risk affect credit risk?",
        "Climate ECL = adjusted PD x adjusted LGD x EAD. Transition risk changes PD; physical risk and collateral decline can increase LGD.",
        "Climate risk is not a separate spreadsheet exercise. It can transmit into borrower cash flows, collateral values, sector concentration, provisions, and capital planning.",
        "I use climate scenarios to show how transition and physical risk can be translated into credit risk parameters and management actions.",
    )


def render_page(ctx: PortfolioContext) -> None:
    render_climate_risk_page(ctx)


