from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data.synthetic_model_risk import synthetic_champion_challenger, synthetic_monitoring_history, synthetic_score_samples
from src.governance.audit import append_audit_event
from src.governance.dashboard import build_governance_dashboard_state
from src.model_risk.approvals import approvals_frame
from src.model_risk.champion_challenger import compare_champion_challenger
from src.model_risk.classification import TieringInput, classify_model_tier
from src.model_risk.drift import categorical_drift, missingness_drift, population_stability_index
from src.model_risk.explainability import global_feature_importance, local_contributions
from src.model_risk.inventory import inventory_to_frame, model_by_id
from src.model_risk.limitations import limitations_frame
from src.model_risk.lifecycle import validate_lifecycle_transition
from src.model_risk.models import ApprovalDecisionType, LifecycleStatus, ModelRiskError, ValidationOutcome
from src.model_risk.monitoring import monitoring_results_for_pd_model, revalidation_trigger_from_monitoring, red_breach_to_finding
from src.model_risk.reporting import model_risk_kpis, model_risk_kpis_frame, model_risk_narrative
from src.model_risk.revalidation import trigger_for_overdue_validation
from src.model_risk.use_restrictions import restrictions_frame
from src.model_risk.validation import development_evidence_frame, findings_frame, validation_assessments_frame
from src.reporting.downloads import dataframe_csv_bytes
from src.ui.components import metrics_row, modelling_depth_label, teaching_block
from src.ui.context import PortfolioContext


MODEL_RISK_ROLES = [
    "Model Developer",
    "Model Owner",
    "Independent Validator",
    "Model Risk Manager",
    "Business User",
    "Internal Audit",
    "Executive Risk Committee",
]


def _role_focus(role: str) -> str:
    return {
        "Model Developer": "Development evidence, performance, remediation and documentation.",
        "Model Owner": "Model use, monitoring, limitations, restrictions and business impact.",
        "Independent Validator": "Validation testing, challenge, findings and conclusion.",
        "Model Risk Manager": "Inventory, tiering, approval, overdue reviews and aggregate risk.",
        "Business User": "Approved use, restrictions, output interpretation and limitations.",
        "Internal Audit": "Lifecycle evidence, approvals, findings and audit trail.",
        "Executive Risk Committee": "Tier 1 exposure, critical findings, restrictions and portfolio impact.",
    }[role]


def render_page(ctx: PortfolioContext) -> None:
    st.subheader("Model Risk Management")
    modelling_depth_label(
        "Analytical Engine",
        "Show how models move from inventory and validation into monitoring, findings, restrictions, revalidation and retirement.",
        "Typed inventory -> tiering -> evidence -> validation -> approval -> monitoring -> findings -> governance issues.",
        "Synthetic models and metrics are used to teach model-risk lifecycle concepts.",
        "This is not a production model-risk system or formal model approval workflow.",
    )
    kpis = model_risk_kpis()
    metrics_row(
        [
            ("Total models", f"{kpis['total_models']:,}"),
            ("Tier 1", f"{kpis['tier1_models']:,}"),
            ("Active restrictions", f"{kpis['models_with_active_restrictions']:,}"),
            ("Red breaches", f"{kpis['red_monitoring_breaches']:,}"),
        ]
    )
    metrics_row(
        [
            ("High findings", f"{kpis['open_high_findings']:,}"),
            ("Overdue validations", f"{kpis['overdue_validations']:,}"),
            ("Expired approvals", f"{kpis['expired_approvals']:,}"),
            ("IFRS 9 models", f"{kpis['models_affecting_ifrs9']:,}"),
        ]
    )
    st.warning(model_risk_narrative(kpis))
    role = st.selectbox("Educational model-risk role", MODEL_RISK_ROLES, index=3)
    st.info(_role_focus(role))

    inventory = inventory_to_frame()
    selected_model_id = st.selectbox("Select model", inventory["model_id"].tolist(), index=0)
    selected_model = model_by_id(selected_model_id)

    tabs = st.tabs(["Inventory", "Model Detail", "Validation", "Monitoring & Drift", "Restrictions", "Explainability", "Governance"])

    with tabs[0]:
        st.dataframe(model_risk_kpis_frame(), width="stretch")
        st.dataframe(inventory, width="stretch", height=420)
        st.download_button("Download model inventory CSV", dataframe_csv_bytes(inventory), file_name="model_inventory.csv", mime="text/csv")
        tier_result = classify_model_tier(
            TieringInput(
                financial_materiality=selected_model.materiality,
                regulatory_importance=8 if selected_model.regulatory_relevance else 3,
                customer_impact=8 if selected_model.model_family.value in {"PD", "Fraud"} else 4,
                model_complexity=6,
                degree_of_automation=7,
                credit_decision_use=8 if selected_model.model_family.value == "PD" else 2,
                regulatory_reporting_use=8 if selected_model.affected_reports else 2,
                downstream_processes=len(selected_model.downstream_systems),
                data_sensitivity=7,
                substitutability=4,
                explainability=5,
                uncertainty=6,
            )
        )
        st.write(f"Tiering rationale: {tier_result.rationale}")
        st.write(f"Contributing factors: {', '.join(tier_result.contributing_factors) or 'No dominant high-risk factor'}")

    with tabs[1]:
        detail = pd.DataFrame(
            [
                {
                    "field": key,
                    "value": ", ".join(value) if isinstance(value, list) else value.value if hasattr(value, "value") else value,
                }
                for key, value in selected_model.__dict__.items()
            ]
        )
        st.dataframe(detail, width="stretch")
        st.dataframe(development_evidence_frame().query("model_id == @selected_model_id"), width="stretch")
        try:
            validate_lifecycle_transition(LifecycleStatus.PROPOSED, LifecycleStatus.IN_PRODUCTION, ApprovalDecisionType.DEFERRED, ValidationOutcome.NOT_ASSESSED)
        except ModelRiskError as exc:
            st.info(f"Lifecycle validation example: {exc}")

    with tabs[2]:
        st.dataframe(validation_assessments_frame().query("model_id == @selected_model_id or model_id == 'PD-LOGIT-001'"), width="stretch")
        st.dataframe(findings_frame().query("model_id == @selected_model_id or model_id == 'PD-LOGIT-001'"), width="stretch")
        st.dataframe(approvals_frame().query("model_id == @selected_model_id or model_id == 'PD-LOGIT-001'"), width="stretch")

    with tabs[3]:
        history = synthetic_monitoring_history()
        st.plotly_chart(px.line(history, x="date", y=["auc", "brier_score", "calibration_error", "psi"], title="PD model monitoring history"), width="stretch")
        results = monitoring_results_for_pd_model()
        st.dataframe(pd.DataFrame([result.__dict__ | {"status": result.status.value} for result in results]), width="stretch")
        ref, cur = synthetic_score_samples()
        psi = population_stability_index(ref, cur)
        drift = missingness_drift(pd.Series([1, 2, None, 4]), pd.Series([None, None, 3, 4]))
        cat = categorical_drift(pd.Series(["A", "B", "B"]), pd.Series(["A", "C", "C"]))
        metrics_row([("Prediction PSI", f"{psi:.3f}"), ("Missingness drift", str(drift["status"])), ("Unseen categories", f"{len(cat['unseen_categories'])}"), ("Concept drift note", "Calibration + performance reviewed")])
        red = [red_breach_to_finding(result) for result in results if red_breach_to_finding(result)]
        triggers = [revalidation_trigger_from_monitoring(result) for result in results if revalidation_trigger_from_monitoring(result)]
        st.write(f"Red breaches generate {len(red)} finding(s) and {len(triggers)} revalidation trigger(s).")

    with tabs[4]:
        st.dataframe(restrictions_frame().query("model_id == @selected_model_id or model_id == 'PD-LOGIT-001'"), width="stretch")
        st.dataframe(limitations_frame().query("model_id == @selected_model_id or model_id == 'PD-LOGIT-001'"), width="stretch")
        overdue = trigger_for_overdue_validation(selected_model)
        if overdue:
            st.error(f"Revalidation trigger: {overdue.trigger} due by {overdue.due_date.isoformat()}")

    with tabs[5]:
        importance = global_feature_importance(["income", "credit_score", "debt_to_income", "days_past_due"], [-0.12, -0.20, 0.18, 0.35])
        st.dataframe(importance, width="stretch")
        local = local_contributions(
            {"income": 0.3, "credit_score": 0.2, "debt_to_income": 0.5, "days_past_due": 0.7},
            {"income": -0.02, "credit_score": -0.03, "debt_to_income": 0.08, "days_past_due": 0.12},
        )
        st.json(local)
        cc = compare_champion_challenger(synthetic_champion_challenger())
        st.dataframe(cc.comparison, width="stretch")
        st.info(f"Champion-challenger recommendation: {cc.recommendation}. {cc.rationale}")

    with tabs[6]:
        governance_state = build_governance_dashboard_state(ctx.base_cet1, ctx.base_rwa)
        st.dataframe(pd.DataFrame([issue.__dict__ | {"severity": issue.severity.value, "status": issue.status.value} for issue in governance_state.issues]), width="stretch")
        if st.button("Log model-risk review event"):
            from src.governance.audit import make_audit_event

            event = make_audit_event("MRM-REVIEW", role, "Model Risk Management", "Model", selected_model_id, "Model risk review", "", selected_model.lifecycle_status.value, "Synthetic model-risk review")
            append_audit_event(event)
            st.success("Model-risk audit event written.")

    teaching_block(
        "How is model risk managed after a model is built?",
        "Inventory -> tiering -> development evidence -> independent validation -> approval -> monitoring -> finding/restriction -> revalidation or retirement.",
        "Model development builds the model. Independent validation challenges whether it is conceptually sound, correctly implemented and fit for intended use. Monitoring does not replace validation.",
        "A high AUC is not enough: calibration, stability, explainability, limitations, approvals, restrictions and data quality all matter.",
    )
