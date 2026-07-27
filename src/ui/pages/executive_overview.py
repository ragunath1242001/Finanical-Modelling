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
from src.reporting.governance_reporting import executive_governance_narrative
from src.model_risk.reporting import model_risk_kpis, model_risk_narrative
from src.reporting.corep import corep_metrics
from src.reporting.downloads import capital_summary_report, dataframe_csv_bytes, pdf_report_bytes, validation_report
from src.reporting.executive import management_actions
from src.reporting.finrep import finrep_metrics
from src.reporting.portfolio import (
    fraud_alert_distribution,
    ifrs9_stage_mix,
    product_expected_loss,
    product_risk_summary,
)
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

CAPABILITY_MAP = [
    ("CR", "Credit risk", "PD/LGD/EAD, expected loss, top-risk loans, reason codes, model development lab."),
    ("E9", "IFRS 9", "Stage 1/2/3 logic, 12-month vs lifetime ECL, scenario-weighted ECL, provision bridge."),
    ("BC", "Capital and regulation", "Basel capital ratios, IRB approximation, CRR3 output floor, COREP-style metrics."),
    ("ST", "Stress testing", "Macro shock, reverse stress, geopolitical loss channels, CET1 sensitivity."),
    ("LQ", "Liquidity", "LCR, NSFR, leverage, and simple compliance interpretation."),
    ("FC", "Financial crime", "Fraud alert scoring, AML indicators, threshold tuning, alert downloads."),
    ("FR", "Forecasting", "12-month balance, provision, income, and alert trend forecasting."),
    ("GV", "Governance", "BCBS 239 data quality, reconciliation, lineage, audit logging, issue workflow."),
    ("MR", "Model risk", "Validation findings, drift, calibration, confusion matrix, monitoring concepts."),
    ("AI", "EU AI Act and DORA", "AI control assessment, fairness gap, ICT incident classification, resilience checks."),
    ("CX", "Climate and XVA", "Climate-adjusted credit risk and counterparty exposure valuation adjustments."),
    ("SG", "Study guide", "Definitions, formulas, memory hooks, interactive learning, and end-to-end case studies."),
]

def render_executive_overview_page(ctx: PortfolioContext) -> None:
    globals().update(_unpack(ctx))
    governance_state = build_governance_dashboard_state(base_cet1, base_rwa)
    governance_kpis = governance_state.kpis
    mr_kpis = model_risk_kpis()
    st.subheader("Executive Overview")
    st.write(
        "A portfolio control room for exploring how synthetic banking data flows through credit risk, IFRS 9, capital, reporting, data governance, model risk and executive decisions."
    )
    st.info(
        "This app is for learning and portfolio review. All data is synthetic, all methods are simplified educational approximations, "
        "and the outputs are not regulatory submissions, accounting decisions or production model results."
    )
    render_capability_cards(
        [
            ("RK", "Risk", "PD/LGD/EAD, ECL, staging, stress and reverse stress."),
            ("CP", "Capital", "RWA, CET1, IRB comparison, CRR3 and leverage."),
            ("RP", "Reporting", "COREP/FINREP-style readiness and reconciliation."),
            ("GV", "Governance", "BCBS 239 controls, lineage, 1LOD/2LOD and audit trail."),
            ("MR", "Model Risk", "Inventory, validation, monitoring, drift and restrictions."),
            ("LR", "Learning", "Banking 101, study guide, glossary and interview preparation."),
        ]
    )
    metrics_row(
        [
            ("Customers ingested", f"{customers['customer_id'].nunique():,}"),
            ("Loans ingested", f"{len(loans_raw):,}"),
            ("Transactions ingested", f"{len(transactions):,}"),
            ("Financial months", f"{len(financials):,}"),
        ]
    )
    metrics_row(
        [
            ("Portfolio ECL", f"EUR {portfolio_ecl:,.0f}"),
            ("Stressed CET1 ratio", f"{ratios['cet1_ratio']:.2%}"),
            ("RWA", f"EUR {base_rwa:,.0f}"),
            ("Data quality score", f"{quality_score:.1f}%"),
        ]
    )
    metrics_row(
        [
            ("LCR", f"{liq_lcr:.1%}"),
            ("NSFR", f"{liq_nsfr:.1%}"),
            ("Fraud alerts", f"{int(fraud_scored['risk_label'].eq('Alert').sum()):,}"),
            ("AML high alerts", f"{int(aml_scored['investigation_priority'].eq('High').sum()):,}"),
        ]
    )
    metrics_row(
        [
            ("Open DQ issues", f"{governance_kpis['open_issues']:,}"),
            ("High/Critical DQ", f"{governance_kpis['high_or_critical_issues']:,}"),
            ("Failed controls", f"{governance_kpis['controls_failed']:,}"),
            ("Pending 2LOD", f"{governance_kpis['pending_2lod_closures']:,}"),
        ]
    )
    st.info(executive_governance_narrative(governance_kpis))
    metrics_row(
        [
            ("Models", f"{mr_kpis['total_models']:,}"),
            ("Tier 1 models", f"{mr_kpis['tier1_models']:,}"),
            ("Red model breaches", f"{mr_kpis['red_monitoring_breaches']:,}"),
            ("Use restrictions", f"{mr_kpis['models_with_active_restrictions']:,}"),
        ]
    )
    st.warning(model_risk_narrative(mr_kpis))

    overview_tab, data_tab, capability_tab, action_tab = st.tabs(["Dashboard", "Data Ingested", "Learning & Testing", "Actions & Report"])

    with overview_tab:
        chart_left, chart_right = st.columns([1.4, 1])
        with chart_left:
            st.plotly_chart(px.histogram(loans, x="expected_loss", nbins=45, title="Expected loss distribution"), width="stretch")
        with chart_right:
            product_ecl = product_expected_loss(loans)
            st.plotly_chart(px.bar(product_ecl, x="product_type", y="expected_loss", title="Expected loss by product"), width="stretch")
        split_left, split_right = st.columns(2)
        with split_left:
            stage_counts = ifrs9_stage_mix(loans_raw)
            st.plotly_chart(px.pie(stage_counts, names="stage", values="loans", title="IFRS 9 stage mix"), width="stretch")
        with split_right:
            crime_counts = fraud_alert_distribution(fraud_scored)
            st.plotly_chart(px.bar(crime_counts, x="risk_label", y="transactions", title="Fraud alert distribution"), width="stretch")

    with data_tab:
        st.write("These are the synthetic datasets currently loaded into the app and used across the risk, reporting, financial crime, and governance modules.")
        st.info(
            "Dataset narrative: this synthetic portfolio behaves like a compact retail and SME bank. "
            "Borrowers have income, credit score, debt burden, products, collateral indicators, and repayment behaviour. "
            "Transactions add fraud and AML signals, while financial time series add reporting and forecasting context. "
            "The data deliberately contains quality issues so BCBS 239, reconciliation, audit, and model monitoring checks have realistic problems to detect."
        )
        st.dataframe(context_dataset_summary(app_data), width="stretch")
        data_left, data_right = st.columns([1, 1])
        with data_left:
            st.subheader("Portfolio Snapshot")
            metrics_row(
                [
                    ("Total EAD", f"EUR {portfolio_ead:,.0f}"),
                    ("Avg PD", f"{portfolio_pd:.2%}"),
                    ("Avg LGD", f"{portfolio_lgd:.2%}"),
                ]
            )
            st.dataframe(
                product_risk_summary(loans),
                width="stretch",
            )
        with data_right:
            st.subheader("Data Quality Signals")
            st.dataframe(quality_table, width="stretch")
        st.subheader("Field Inventory")
        inventory = context_field_inventory(app_data)
        download_left, download_right = st.columns([1, 1])
        with download_left:
            st.download_button(
                "Download data dictionary PDF",
                context_data_dictionary_pdf(app_data),
                file_name="data_dictionary.pdf",
                mime="application/pdf",
            )
        with download_right:
            st.download_button(
                "Download field inventory CSV",
                dataframe_csv_bytes(inventory),
                file_name="field_inventory.csv",
                mime="text/csv",
            )
        st.dataframe(inventory, width="stretch", height=420)

    with capability_tab:
        st.write("Use this view as a map of what the platform can help you understand, test, and explain.")
        render_capability_cards(CAPABILITY_MAP)
        learn_a, learn_b, learn_c = st.columns(3)
        with learn_a:
            st.subheader("Risk Calculations")
            for item in ["Expected loss", "IFRS 9 staging", "Scenario-weighted ECL", "RWA and CET1 ratios", "Reverse stress loss threshold"]:
                st.write(f"- {item}")
        with learn_b:
            st.subheader("Controls and Governance")
            for item in ["BCBS 239 data quality", "Lineage and reconciliation", "Model validation findings", "AI Act controls", "DORA incident assessment"]:
                st.write(f"- {item}")
        with learn_c:
            st.subheader("Decision Practice")
            for item in ["Management actions", "Threshold tuning", "Capital sensitivity", "Case study explanation", "Downloadable evidence reports"]:
                st.write(f"- {item}")

    with action_tab:
        st.subheader("Management Actions")
        for action in management_actions(ratios["cet1_ratio"], liq_lcr, liq_nsfr, quality_score):
            st.write(f"- {action}")
        st.divider()
        st.subheader("Download")
        st.download_button(
            "Download capital summary",
            capital_summary_report(ratios["cet1_ratio"], base_rwa, liq_lcr, liq_nsfr),
            file_name="capital_liquidity_summary.pdf",
            mime="application/pdf",
        )
    teaching_block(
        "What data has been loaded, what risk signals does it create, and which parts of the platform can be used for learning or testing?",
        "Customers + loans + transactions + financial trends -> data quality checks -> ECL, capital, liquidity, fraud/AML, IFRS 9 stage mix, and management actions.",
        "The overview connects the ingested synthetic datasets to the calculations and modules built on top of them. It shows portfolio size, field coverage, data quality issues, risk indicators, available learning areas, and the reports that can be downloaded.",
        "Use this page as the project control room: first understand the data, then inspect the risk metrics, then choose the module you want to study, test, or explain in more detail.",
    )


def render_page(ctx: PortfolioContext) -> None:
    render_executive_overview_page(ctx)


