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

def render_xva_page(ctx: PortfolioContext) -> None:
    globals().update(_unpack(ctx))
    st.subheader("XVA Counterparty Risk Mini Lab")
    x1, x2, x3, x4 = st.columns(4)
    notional = x1.number_input("Derivative notional", min_value=1.0, value=25_000_000.0, step=1_000_000.0)
    maturity = x2.slider("Maturity years", 1, 10, 5)
    volatility = x3.slider("Exposure volatility proxy", 0.01, 0.30, 0.08, 0.01)
    collateral_cov = x4.slider("Collateral/netting coverage", 0.0, 0.95, 0.45, 0.05)
    y1, y2, y3 = st.columns(3)
    cpd = y1.slider("Counterparty annual PD", 0.001, 0.20, 0.025, 0.001)
    own_pd = y2.slider("Own annual PD for DVA", 0.001, 0.10, 0.01, 0.001)
    xlgd = y3.slider("Counterparty LGD", 0.05, 0.95, 0.60, 0.01)
    z1, z2, z3 = st.columns(3)
    funding_spread = z1.slider("Funding spread", 0.0, 0.08, 0.018, 0.001)
    initial_margin = z2.number_input("Initial margin", min_value=0.0, value=2_500_000.0, step=100_000.0)
    margin_spread = z3.slider("Margin funding spread", 0.0, 0.08, 0.012, 0.001)
    profile, xva = xva_summary(notional, maturity, volatility, collateral_cov, cpd, xlgd, own_pd, funding_spread, initial_margin, margin_spread, 0.03)
    metrics_row([(name, f"EUR {value:,.0f}") for name, value in xva.items()])
    st.plotly_chart(px.line(profile, x="year", y="expected_positive_exposure", markers=True, title="Expected positive exposure profile"), width="stretch")
    st.dataframe(profile, width="stretch")
    st.warning("This XVA page is an educational approximation. It is not a full derivatives pricing, Monte Carlo, collateral, or regulatory CVA implementation.")
    teaching_block(
        "What is XVA and why do banks care about it?",
        "CVA estimates counterparty credit loss on positive exposure. FVA estimates funding cost. MVA estimates initial margin funding cost. DVA is shown separately for own-credit effects.",
        "XVA connects derivative valuation with counterparty credit risk, collateral, funding spreads, and model validation.",
        "I can explain XVA at a portfolio level: derivatives create future exposure, collateral reduces exposure, counterparty PD/LGD drive CVA, and funding/margin costs affect valuation.",
    )


def render_page(ctx: PortfolioContext) -> None:
    render_xva_page(ctx)


