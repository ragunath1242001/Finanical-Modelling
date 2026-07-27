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
from src.risk.expected_loss import point_in_time_expected_loss
from src.model_risk.reporting import model_confidence
from src.model_risk.inventory import model_by_id
from src.model_risk.use_restrictions import restrictions_frame
from src.risk.ifrs9 import assign_stage, calculate_ifrs9, expected_credit_loss
from src.risk.ifrs9_scenario_engine import ecl_bridge, scenario_weighted_ecl, stage_migration_table
from src.risk.irb import irb_rwa_equivalent, simplified_irb_capital, standardized_rwa
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

@st.cache_data
def run_credit_model_lab(customers_data: pd.DataFrame, loans_data: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    frame = prepare_model_frame(customers_data, loans_data)
    return frame, train_credit_models(frame)


def render_credit_portfolio_view(ctx: PortfolioContext) -> None:
    globals().update(_unpack(ctx))
    modelling_depth_label(
        "Model Lab",
        "Inspect borrower-level PD/LGD/EAD drivers and expected-loss ranking.",
        "Validated point-in-time expected loss: PD x LGD x EAD.",
        "Synthetic borrower and loan data; PD/LGD/EAD values are educational approximations.",
        "Not a production underwriting, IFRS 9, IRB or regulatory model.",
    )
    selected = st.selectbox("Customer loan", loans["loan_id"].head(200))
    row = loans.loc[loans["loan_id"].eq(selected)].iloc[0]
    pd_model = model_by_id("PD-LOGIT-001")
    confidence = model_confidence("PD-LOGIT-001")
    st.caption(
        f"Model reference: {pd_model.model_id} v{pd_model.model_version} | approval: {pd_model.approval_status.value} | "
        f"last validation: {pd_model.last_validation_date.isoformat()} | next validation: {pd_model.next_validation_date.isoformat()} | confidence: {confidence}"
    )
    if confidence == "Use restricted":
        st.warning("Model-risk confidence indicator: use restricted due to calibration monitoring breach. Outputs remain educational.")
    st.dataframe(restrictions_frame().query("model_id == 'PD-LOGIT-001'"), width="stretch")
    customer = customers.loc[customers["customer_id"].eq(row["customer_id"])].iloc[0]
    pd_input = st.slider("PD", 0.0, 1.0, float(row["adjusted_pd"]), 0.005)
    lgd_input = st.slider("LGD", 0.0, 1.0, float(row["adjusted_lgd"]), 0.01)
    ead_input = st.number_input("EAD", min_value=0.0, value=float(row["ead"]), step=1000.0)
    ecl_result = point_in_time_expected_loss(pd_input, lgd_input, ead_input)
    ecl = ecl_result.expected_loss
    metrics_row([("PD", f"{pd_input:.2%}"), ("LGD", f"{lgd_input:.2%}"), ("EAD", f"EUR {ead_input:,.0f}"), ("Expected loss", f"EUR {ecl:,.0f}")])
    profile = pd.DataFrame([customer.to_dict() | row.to_dict()])
    st.dataframe(profile[["customer_id", "age", "income", "credit_score", "debt_to_income", "product_type", "loan_amount", "ltv", "days_past_due"]], width="stretch")
    st.write("Top reason codes")
    for reason in pd_reason_codes(profile.iloc[0]):
        st.write(f"- {reason}")
    st.dataframe(loans.nlargest(10, "expected_loss")[["loan_id", "customer_id", "product_type", "adjusted_pd", "adjusted_lgd", "ead", "expected_loss"]], width="stretch")
    teaching_block(
        "Which borrowers create the most expected loss and why?",
        ecl_result.steps[0],
        "A large loan is not automatically the riskiest loan. Expected loss is multiplicative, so probability of default, loss severity, and exposure all matter.",
        "Credit risk combines default likelihood, loss severity, and exposure. I use PD, LGD, and EAD to rank customers and explain risk grades.",
    )


def render_credit_model_development_lab(ctx: PortfolioContext) -> None:
    globals().update(_unpack(ctx))
    st.subheader("Credit Risk Model Development Lab")
    model_frame, model_result = run_credit_model_lab(customers, loans_raw)
    threshold = st.slider("Default classification threshold", 0.05, 0.95, 0.50, 0.01)
    comparison = model_comparison_table(model_result, threshold)
    selected_model_name = st.selectbox("Model", list(model_result["models"].keys()))
    selected_model = model_result["models"][selected_model_name]
    metrics = comparison.loc[comparison["model"].eq(selected_model_name)].iloc[0]
    metrics_row(
        [
            ("AUC", f"{metrics['auc']:.3f}"),
            ("Average precision", f"{metrics['average_precision']:.3f}"),
            ("Brier score", f"{metrics['brier_score']:.3f}"),
            ("Recall", f"{metrics['recall']:.1%}"),
        ]
    )
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Comparison", "ROC & Calibration", "Confusion Matrix", "Risk Grades", "Monitoring"])
    with tab1:
        st.dataframe(comparison, width="stretch")
        st.download_button(
            "Download model comparison CSV",
            dataframe_csv_bytes(comparison),
            file_name="model_comparison.csv",
            mime="text/csv",
        )
        st.download_button(
            "Download validation report",
            validation_report(metrics.to_dict(), selected_model_name),
            file_name="model_validation_summary.pdf",
            mime="application/pdf",
        )
        st.plotly_chart(px.bar(feature_importance(selected_model), x="feature", y="importance", title=f"Feature importance: {selected_model_name}"), width="stretch")
    with tab2:
        roc = roc_curve_frame(selected_model, model_result["x_test"], model_result["y_test"])
        cal = calibration_table(selected_model, model_result["x_test"], model_result["y_test"])
        st.plotly_chart(px.line(roc, x="false_positive_rate", y="true_positive_rate", title="ROC curve"), width="stretch")
        st.plotly_chart(px.line(cal, x="predicted_pd", y="observed_default_rate", markers=True, title="Calibration: predicted PD vs observed default rate"), width="stretch")
        st.dataframe(cal, width="stretch")
    with tab3:
        st.dataframe(confusion_matrix_frame(selected_model, model_result["x_test"], model_result["y_test"], threshold), width="stretch")
    with tab4:
        scored = score_with_grades(selected_model, model_frame)
        grade_counts = scored["risk_grade"].value_counts().rename_axis("risk_grade").reset_index(name="count")
        st.plotly_chart(px.bar(grade_counts, x="risk_grade", y="count", title="Risk grade distribution"), width="stretch")
        st.dataframe(scored[["loan_id", "customer_id", "model_pd", "risk_grade", "default_flag", "credit_score", "debt_to_income", "days_past_due"]].sort_values("model_pd", ascending=False).head(25), width="stretch")
    with tab5:
        baseline_scores = selected_model.predict_proba(model_result["x_train"])[:, 1]
        current_scores = selected_model.predict_proba(model_result["x_test"])[:, 1]
        psi = population_stability_index(pd.Series(baseline_scores), pd.Series(current_scores))
        missingness = model_frame[["income", "pd"]].isna().mean().rename("missing_rate").reset_index().rename(columns={"index": "field"})
        metrics_row([("PD score PSI", f"{psi:.3f}"), ("Monitoring status", "Review" if psi >= 0.1 else "Stable"), ("Training rows", f"{len(model_result['x_train']):,}"), ("Test rows", f"{len(model_result['x_test']):,}")])
        st.dataframe(missingness, width="stretch")
    teaching_block(
        "How is a credit PD model developed and governed?",
        "Data -> train/test split -> model training -> AUC/calibration/Brier score -> threshold testing -> risk grades -> monitoring.",
        "A credit model should not only rank risk. It should be calibrated, explainable, monitored, and documented with known limitations.",
        "This lab shows a realistic model development workflow: baseline model, challenger model, validation metrics, calibration, risk grading, and monitoring evidence.",
    )



def render_credit_risk_page(ctx: PortfolioContext) -> None:
    globals().update(_unpack(ctx))
    credit_mode = st.segmented_control("Mode", ["Portfolio Risk View", "Model Development Lab"], default="Portfolio Risk View")
    if credit_mode == "Model Development Lab":
        render_credit_model_development_lab(ctx)
    else:
        render_credit_portfolio_view(ctx)


def render_page(ctx: PortfolioContext) -> None:
    render_credit_risk_page(ctx)


