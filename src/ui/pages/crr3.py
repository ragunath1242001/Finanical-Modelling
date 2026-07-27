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
from src.reporting.portfolio import crr3_rwa_stack
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

def render_crr3_page(ctx: PortfolioContext) -> None:
    globals().update(_unpack(ctx))
    st.subheader("CRR3 / Basel III Final Reforms Lab")
    col1, col2, col3 = st.columns(3)
    internal_rwa = col1.number_input("Internal model credit RWA", min_value=1.0, value=base_rwa * 0.72, step=500_000.0)
    standardized_credit_rwa = col2.number_input("Fully standardized credit RWA", min_value=1.0, value=base_rwa * 1.15, step=500_000.0)
    floor_rate = col3.slider("Output floor rate", 0.50, 0.725, 0.55, 0.005)
    floor = output_floor(internal_rwa, standardized_credit_rwa, floor_rate)

    st.write("Operational risk standardized measurement approach approximation")
    op1, op2, op3, op4 = st.columns(4)
    interest_component = op1.number_input("Interest component", min_value=0.0, value=420_000_000.0, step=10_000_000.0)
    services_component = op2.number_input("Services component", min_value=0.0, value=110_000_000.0, step=5_000_000.0)
    financial_component = op3.number_input("Financial component", min_value=0.0, value=60_000_000.0, step=5_000_000.0)
    loss_multiplier = op4.slider("Internal loss multiplier", 0.75, 1.50, 1.00, 0.05)
    op_risk = operational_risk_sma(interest_component, services_component, financial_component, loss_multiplier)

    st.write("CVA-lite counterparty credit valuation adjustment")
    c1, c2, c3, c4 = st.columns(4)
    epe = c1.number_input("Expected positive exposure", min_value=0.0, value=12_000_000.0, step=500_000.0)
    counterparty_pd = c2.slider("Counterparty PD", 0.001, 0.20, 0.025, 0.001)
    counterparty_lgd = c3.slider("Counterparty LGD", 0.05, 0.95, 0.60, 0.01)
    collateral = c4.slider("Collateral coverage", 0.0, 0.95, 0.35, 0.05)
    cva = cva_lite_capital(epe, counterparty_pd, counterparty_lgd, 3.0, collateral_coverage=collateral)
    market_rwa = st.number_input("Market risk RWA placeholder", min_value=0.0, value=base_rwa * 0.12, step=250_000.0)
    crr3 = crr3_total_rwa(floor["binding_rwa"], market_rwa, cva["cva_rwa"], op_risk["operational_risk_rwa"], internal_rwa, standardized_credit_rwa, floor_rate)
    crr3_ratios = capital_ratios(base_cet1, at1, tier2, crr3["total_rwa"])
    metrics_row(
        [
            ("Output floor binding", "Yes" if floor["is_floor_binding"] else "No"),
            ("RWA add-on", f"EUR {floor['rwa_add_on']:,.0f}"),
            ("Operational RWA", f"EUR {op_risk['operational_risk_rwa']:,.0f}"),
            ("CVA-lite RWA", f"EUR {cva['cva_rwa']:,.0f}"),
        ]
    )
    metrics_row([("CRR3 total RWA", f"EUR {crr3['total_rwa']:,.0f}"), ("CET1 ratio", f"{crr3_ratios['cet1_ratio']:.2%}"), ("Op risk capital", f"EUR {op_risk['operational_risk_capital']:,.0f}"), ("CVA-lite", f"EUR {cva['cva_lite']:,.0f}")])
    st.warning("These CRR3 calculations are simplified educational approximations, not production regulatory capital engines.")
    st.plotly_chart(px.bar(crr3_rwa_stack(floor["binding_rwa"], market_rwa, cva["cva_rwa"], op_risk["operational_risk_rwa"]), x="component", y="amount", title="CRR3 RWA stack"), width="stretch")
    teaching_block(
        "How do final Basel III / CRR3 reforms change capital analysis?",
        "Output floor = max(internal model RWA, standardized RWA x floor rate). Total RWA adds credit, market, CVA, and operational risk.",
        "The final reforms reduce excessive RWA variability by constraining internal models and adding more standardized treatment for CVA and operational risk.",
        "I can explain CRR3 as a capital comparability reform: even if an internal model produces low RWA, the output floor can increase binding capital requirements.",
    )


def render_page(ctx: PortfolioContext) -> None:
    render_crr3_page(ctx)


