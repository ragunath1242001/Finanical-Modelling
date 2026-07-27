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

def render_geopolitical_reverse_stress_page(ctx: PortfolioContext) -> None:
    globals().update(_unpack(ctx))
    st.subheader("ECB-Style Geopolitical Reverse Stress Test")
    target_bps = st.slider("Target CET1 depletion", 100, 500, 300, 25)
    req_loss = required_loss_for_target(base_cet1, base_rwa, target_bps)
    s1, s2, s3 = st.columns(3)
    pd_mult = s1.slider("Credit channel: PD multiplier", 0.5, 5.0, 2.2, 0.1)
    lgd_mult = s2.slider("Collateral channel: LGD multiplier", 0.5, 2.5, 1.4, 0.05)
    funding_cost = s3.number_input("Funding/liquidity cost shock", min_value=0.0, value=850_000.0, step=50_000.0)
    m1, m2 = st.columns(2)
    market_loss = m1.number_input("Market/geopolitical loss", min_value=0.0, value=1_250_000.0, step=50_000.0)
    operational_loss = m2.number_input("Operational/cyber disruption loss", min_value=0.0, value=450_000.0, step=50_000.0)
    reverse = reverse_stress_solver(
        base_cet1,
        at1,
        tier2,
        base_rwa,
        target_bps,
        portfolio_ead,
        portfolio_pd,
        portfolio_lgd,
        pd_mult,
        lgd_mult,
        market_loss,
        operational_loss,
        funding_cost,
    )
    metrics_row(
        [
            ("Opening CET1 ratio", f"{reverse['opening_cet1_ratio']:.2%}"),
            ("Stressed CET1 ratio", f"{reverse['stressed_cet1_ratio']:.2%}"),
            ("CET1 depletion", f"{reverse['depletion_bps']:,.0f} bps"),
            ("Status", str(reverse["status"])),
        ]
    )
    metrics_row([("Loss needed for target", f"EUR {req_loss:,.0f}"), ("Simulated total loss", f"EUR {reverse['total_loss']:,.0f}"), ("Target gap", f"{reverse['target_gap_bps']:,.0f} bps"), ("Provision increase", f"EUR {reverse['provision_increase']:,.0f}")])
    bridge = pd.DataFrame(
        {
            "channel": ["Credit provision", "Market loss", "Operational/cyber", "Funding cost"],
            "loss": [reverse["provision_increase"], market_loss, operational_loss, funding_cost],
        }
    )
    st.plotly_chart(px.bar(bridge, x="channel", y="loss", title="Reverse stress loss channels"), width="stretch")
    st.write("Example geopolitical narratives")
    st.write("- Sanctions and trade fragmentation weaken export-sector borrowers, raising PD.")
    st.write("- Energy or commodity shock reduces collateral values, raising LGD.")
    st.write("- Cyber disruption or critical provider outage creates operational losses and funding pressure.")
    teaching_block(
        "What scenario could reduce CET1 by the target amount?",
        "Reverse stress starts with a failure outcome, then searches for plausible shocks that could create it.",
        "This is different from ordinary stress testing: instead of asking what a fixed scenario does, it asks what scenario could break the capital plan.",
        "I can use reverse stress testing to explain scenario design, transmission channels, CET1 depletion, funding impacts, and management actions.",
    )


def render_page(ctx: PortfolioContext) -> None:
    render_geopolitical_reverse_stress_page(ctx)


