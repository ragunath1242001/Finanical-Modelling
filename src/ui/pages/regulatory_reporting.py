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
from src.governance.dashboard import build_governance_dashboard_state
from src.reporting.governance_reporting import reporting_readiness
from src.reporting.model_risk_reporting import model_risk_readiness_factors
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

def render_regulatory_reporting_page(ctx: PortfolioContext) -> None:
    globals().update(_unpack(ctx))
    governance_state = build_governance_dashboard_state(base_cet1, base_rwa)
    readiness = reporting_readiness(governance_state.control_results, governance_state.issues, governance_state.reconciliation)
    model_readiness = model_risk_readiness_factors()
    finrep = finrep_metrics(120_000_000, 108_000_000, 3_600_000, portfolio_ecl, 1_800_000)
    corep = corep_metrics(base_cet1 - portfolio_ecl, at1, tier2, base_rwa, portfolio_ead)
    metrics_row([("FINREP profit", f"EUR {finrep['profit']:,.0f}"), ("FINREP equity", f"EUR {finrep['equity']:,.0f}"), ("COREP CET1", f"{corep['cet1_ratio']:.2%}"), ("Capital status", corep["capital_adequacy_status"])])
    metrics_row(
        [
            ("Report readiness", readiness["report_production_readiness"]),
            ("Sign-off status", readiness["sign_off_status"]),
            ("Open control failures", readiness["open_control_failures"]),
            ("Reconciliation", readiness["reconciliation_status"]),
        ]
    )
    metrics_row(
        [
            ("Model readiness", str(model_readiness["model_risk_readiness"])),
            ("Approval valid", str(model_readiness["model_approval_valid"])),
            ("Validation current", str(model_readiness["validation_current"])),
            ("Monitoring acceptable", str(model_readiness["monitoring_status_acceptable"])),
        ]
    )
    st.write(f"Affected data elements: {readiness['affected_data_elements']}")
    rec = reconcile_exposure(portfolio_ead, portfolio_ead * 1.012)
    st.dataframe(rec, width="stretch")
    st.dataframe(governance_state.reconciliation.details, width="stretch")
    teaching_block(
        "How do financial reporting and capital reporting connect?",
        "Provision expense lowers FINREP profit; retained earnings are part of CET1, so provisions can reduce COREP capital ratios.",
        "FINREP explains financial performance and position. COREP explains regulatory capital adequacy and risk-weighted exposure.",
        "A PD shock flows through IFRS 9 provisions into profit, retained earnings, CET1, and capital ratio reporting.",
    )


def render_page(ctx: PortfolioContext) -> None:
    render_regulatory_reporting_page(ctx)


