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

def render_dora_page(ctx: PortfolioContext) -> None:
    globals().update(_unpack(ctx))
    st.subheader("DORA Operational Resilience and ICT Third-Party Risk")
    i1, i2, i3 = st.columns(3)
    affected_users = i1.number_input("Affected users", min_value=0, value=12_500, step=500)
    downtime = i2.slider("Downtime hours", 0.0, 24.0, 4.5, 0.5)
    critical_service = i3.checkbox("Critical or important function affected", value=True)
    data_loss = st.checkbox("Data loss or integrity issue", value=False)
    third_party = st.checkbox("Third-party ICT provider involved", value=True)
    incident = dora_incident_classification(affected_users, downtime, data_loss, critical_service, third_party)

    r1, r2, r3, r4 = st.columns(4)
    rto = r1.slider("RTO hours", 0.5, 24.0, 4.0, 0.5)
    actual_recovery = r2.slider("Actual recovery hours", 0.5, 48.0, 5.0, 0.5)
    rpo = r3.slider("RPO hours", 0.0, 12.0, 1.0, 0.5)
    actual_loss = r4.slider("Actual data loss hours", 0.0, 24.0, 0.5, 0.5)
    tested = st.checkbox("Resilience test completed this year", value=True)
    exit_plan = st.checkbox("Exit plan available for critical provider", value=False)
    resilience = resilience_score(rto, actual_recovery, rpo, actual_loss, tested, exit_plan)
    metrics_row(
        [
            ("Incident score", str(incident["incident_score"])),
            ("Severity", str(incident["severity"])),
            ("Resilience score", f"{resilience['resilience_score']:.0f}/100"),
            ("Status", str(resilience["status"])),
        ]
    )
    st.info(str(incident["reporting_action"]))
    st.dataframe(third_party_register(), width="stretch")
    dora_report = pdf_report_bytes(
        "DORA Incident Assessment",
        {
            "Incident Classification": f"Severity: {incident['severity']}\n\nScore: {incident['incident_score']}\n\nAction: {incident['reporting_action']}",
            "Resilience": f"Score: {resilience['resilience_score']:.0f}/100\n\nStatus: {resilience['status']}",
            "Third Party": f"Third-party provider involved: {incident['third_party_provider']}",
        },
    )
    st.download_button("Download DORA incident report", dora_report, file_name="dora_incident_report.pdf", mime="application/pdf")
    if st.button("Log DORA incident assessment"):
        log_event("portfolio-user", "DORA Operational Resilience", "ICT incident classified", "", str(incident["severity"]), str(incident["reporting_action"]))
        st.success("DORA audit event written.")
    teaching_block(
        "How does DORA change operational risk and governance expectations?",
        "Incident severity combines affected users, downtime, data loss, critical service impact, and third-party involvement. Resilience score checks RTO, RPO, testing, and exit planning.",
        "DORA connects ICT risk, third-party oversight, resilience testing, incident reporting, and senior management accountability.",
        "I can explain DORA as operational resilience governance: banks must know critical providers, test recovery, manage incidents, and evidence oversight.",
    )


def render_page(ctx: PortfolioContext) -> None:
    render_dora_page(ctx)


