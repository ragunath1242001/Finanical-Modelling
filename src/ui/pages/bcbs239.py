from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.governance.audit import append_audit_event, audit_events_to_frame, read_events
from src.governance.dashboard import build_governance_dashboard_state
from src.governance.data_quality import QUALITY_DIMENSION_DEFINITIONS, results_to_frame
from src.governance.evidence import create_evidence, evidence_to_frame
from src.governance.impact_analysis import impact_for_control
from src.governance.issues import issues_to_frame
from src.governance.lineage import LINEAGE_NODES, controls_for_node, downstream_lineage, lineage_edges_frame, lineage_nodes_frame, upstream_lineage
from src.governance.lod_workflows import ROLE_DEFINITIONS, role_dashboard, submit_closure_package, transition_issue
from src.governance.models import EvidenceType, GovernanceError, IssueStatus, LODRole
from src.governance.ownership import ownership_catalogue_frame
from src.reporting.downloads import dataframe_csv_bytes
from src.reporting.governance_reporting import governance_kpis_frame
from src.ui.components import metrics_row, modelling_depth_label, teaching_block
from src.ui.context import PortfolioContext


def _dimension_scores(results_frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dimension, group in results_frame.groupby("dimension"):
        rows.append(
            {
                "dimension": dimension,
                "score": round(100 * (1 - group["failed_records"].sum() / max(1, group["records_tested"].sum())), 2),
                "failed_controls": int(group["status"].eq("Fail").sum()),
            }
        )
    return pd.DataFrame(rows)


def render_page(ctx: PortfolioContext) -> None:
    st.subheader("BCBS 239 Governance")
    modelling_depth_label(
        "Analytical Engine",
        "Connect data-quality controls to model confidence, reporting readiness, issue ownership and auditability.",
        "Structured controls execute against deterministic synthetic data, failed controls create issues, and 1LOD/2LOD/3LOD actions are validated.",
        "Synthetic defects are intentional; financial impact is a sensitivity, not a formal adjustment.",
        "This is an educational governance workflow and not a certified BCBS 239 compliance platform.",
    )

    state = build_governance_dashboard_state(ctx.base_cet1, ctx.base_rwa)
    results_frame = results_to_frame(state.control_results)
    issues_frame = issues_to_frame(state.issues)
    kpis = state.kpis

    metrics_row(
        [
            ("Controls executed", f"{kpis['controls_executed']:,}"),
            ("Controls failed", f"{kpis['controls_failed']:,}"),
            ("Failed records", f"{kpis['failed_records']:,}"),
            ("Open issues", f"{kpis['open_issues']:,}"),
        ]
    )
    metrics_row(
        [
            ("High/Critical", f"{kpis['high_or_critical_issues']:,}"),
            ("Risk-Finance diff", f"EUR {kpis['risk_finance_difference']:,.0f}"),
            ("ECL sensitivity", f"EUR {kpis['illustrative_ecl_impact']:,.0f}"),
            ("Pending 2LOD", f"{kpis['pending_2lod_closures']:,}"),
        ]
    )

    role = st.selectbox("Educational role view", [role.value for role in LODRole], index=0)
    selected_role = LODRole(role)
    st.info(ROLE_DEFINITIONS[selected_role])

    tab_overview, tab_controls, tab_impact, tab_recon, tab_lineage, tab_workflow, tab_learning = st.tabs(
        ["Overview", "Controls", "Impact", "Reconciliation", "Lineage", "1LOD/2LOD/3LOD", "Learning"]
    )

    with tab_overview:
        st.dataframe(governance_kpis_frame(kpis), width="stretch")
        scores = _dimension_scores(results_frame)
        st.plotly_chart(px.bar(scores, x="dimension", y="score", color="failed_controls", title="Quality dimension scores"), width="stretch")
        st.dataframe(scores, width="stretch")
        st.download_button("Download governance KPI CSV", dataframe_csv_bytes(governance_kpis_frame(kpis)), file_name="governance_kpis.csv", mime="text/csv")

    with tab_controls:
        st.write("Control execution results are structured. A failed material control can become a governance issue.")
        st.dataframe(results_frame, width="stretch", height=430)
        selected_control = st.selectbox("Inspect failed control", results_frame["control_id"].tolist())
        selected_result = next(result for result in state.control_results if result.control_id == selected_control)
        impact = impact_for_control(selected_control, selected_result.records_failed, state.portfolio)
        st.write(f"Likely directional impact: {impact.likely_directional_impact}")
        st.write(f"Limitations: {impact.limitations}")
        st.dataframe(pd.DataFrame(selected_result.sample_failed_records), width="stretch")
        st.download_button("Download control results CSV", dataframe_csv_bytes(results_frame), file_name="bcbs239_control_results.csv", mime="text/csv")

    with tab_impact:
        st.write(state.sensitivity["label"])
        metrics_row(
            [
                ("Missing income rate", f"{state.sensitivity['missing_income_rate']:.1%}"),
                ("Base ECL", f"EUR {state.sensitivity['base_ecl']:,.0f}"),
                ("Conservative ECL", f"EUR {state.sensitivity['conservative_ecl']:,.0f}"),
                ("CET1 ratio impact", f"{state.sensitivity['cet1_ratio_impact']:.2%}"),
            ]
        )
        st.write(
            "Example chain: missing income -> PD uncertainty -> IFRS 9 ECL sensitivity -> provision uncertainty -> retained earnings and CET1 uncertainty -> reporting limitation."
        )
        st.dataframe(issues_frame[["issue_id", "title", "affected_model", "affected_report", "financial_impact", "regulatory_impact"]], width="stretch")

    with tab_recon:
        rec = state.reconciliation
        metrics_row(
            [
                ("Matched records", f"{rec.summary.matched_records:,}"),
                ("Unmatched Risk", f"{rec.summary.unmatched_risk_records:,}"),
                ("Unmatched Finance", f"{rec.summary.unmatched_finance_records:,}"),
                ("Status", rec.summary.status),
            ]
        )
        st.dataframe(rec.details, width="stretch")
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("Unmatched Risk records")
            st.dataframe(rec.unmatched_risk, width="stretch")
        with col_b:
            st.write("Unmatched Finance records")
            st.dataframe(rec.unmatched_finance, width="stretch")

    with tab_lineage:
        selected_node = st.selectbox("Select lineage node", [node.node_id for node in LINEAGE_NODES], format_func=lambda node_id: next(node.name for node in LINEAGE_NODES if node.node_id == node_id))
        node = next(node for node in LINEAGE_NODES if node.node_id == selected_node)
        st.write(f"Definition: {node.description}")
        metrics_row([("Owner", node.owner), ("Steward", node.data_steward), ("Node type", node.node_type), ("Controls", ", ".join(controls_for_node(selected_node)))])
        st.write(f"Transformation: {node.transformation}")
        st.write(f"Regulatory relevance: {node.regulatory_relevance}")
        st.write("Upstream lineage")
        st.dataframe(pd.DataFrame([item.__dict__ for item in upstream_lineage(selected_node)]), width="stretch")
        st.write("Downstream lineage")
        st.dataframe(pd.DataFrame([item.__dict__ for item in downstream_lineage(selected_node)]), width="stretch")
        st.write("Full lineage nodes and edges")
        st.dataframe(lineage_nodes_frame(), width="stretch")
        st.dataframe(lineage_edges_frame(), width="stretch")
        st.write("Ownership catalogue")
        st.dataframe(ownership_catalogue_frame(), width="stretch")

    with tab_workflow:
        st.dataframe(role_dashboard(state.issues, selected_role), width="stretch")
        issue = submit_closure_package(state.issues[0])
        st.write("Worked issue: 30% missing income")
        st.dataframe(issues_to_frame([issue]), width="stretch")
        evidence = create_evidence("EV-DQ-001", issue.issue_id, EvidenceType.REMEDIATION_PROOF, "Control rerun and source validation proof.", selected_role.value, "Synthetic evidence note")
        st.dataframe(evidence_to_frame([evidence]), width="stretch")
        action = st.selectbox("Try workflow action", ["Acknowledge", "Invalid direct close from Open", "Submit for 2LOD review", "2LOD accept closure", "2LOD reject closure"])
        try:
            if action == "Acknowledge":
                _, _, event = transition_issue(issue, IssueStatus.ACKNOWLEDGED, selected_role, comment="Issue acknowledged by 1LOD.")
            elif action == "Invalid direct close from Open":
                issue.status = IssueStatus.OPEN
                _, _, event = transition_issue(issue, IssueStatus.CLOSED, selected_role, comment="Invalid direct closure attempt.")
            elif action == "Submit for 2LOD review":
                issue.status = IssueStatus.IN_PROGRESS
                _, _, event = transition_issue(issue, IssueStatus.PENDING_2LOD_REVIEW, LODRole.FIRST_LINE_DATA_STEWARD, comment="1LOD submits completed remediation package.", evidence_reference=evidence.evidence_id)
            elif action == "2LOD accept closure":
                issue.status = IssueStatus.PENDING_2LOD_REVIEW
                _, _, event = transition_issue(issue, IssueStatus.CLOSED, LODRole.SECOND_LINE_DATA_GOVERNANCE, comment="2LOD accepts closure evidence.", evidence_reference=evidence.evidence_id)
            else:
                issue.status = IssueStatus.PENDING_2LOD_REVIEW
                _, _, event = transition_issue(issue, IssueStatus.REJECTED_BY_2LOD, LODRole.SECOND_LINE_DATA_GOVERNANCE, comment="2LOD requests stronger preventive-control evidence.")
            append_audit_event(event)
            st.success(f"Workflow action recorded: {event.action}")
        except GovernanceError as exc:
            st.error(str(exc))
        st.write("Audit trail")
        events = read_events(limit=25)
        st.dataframe(events, width="stretch")
        st.download_button("Download audit trail CSV", dataframe_csv_bytes(events), file_name="bcbs239_audit_trail.csv", mime="text/csv")
        st.write("Synthetic chronological audit example")
        st.dataframe(audit_events_to_frame([]), width="stretch")

    with tab_learning:
        st.write("Data-quality dimensions")
        st.dataframe(pd.DataFrame([{"dimension": dim.value, "definition": definition} for dim, definition in QUALITY_DIMENSION_DEFINITIONS.items()]), width="stretch")
        teaching_block(
            "How does a data-quality issue move through 1LOD, 2LOD and 3LOD?",
            "30% missing income -> control failure -> issue creation -> 1LOD investigates -> model/report impact assessed -> evidence submitted -> 2LOD challenges or accepts -> audit trail preserved.",
            "1LOD owns and manages the risk. 2LOD provides independent oversight and challenge. 3LOD provides independent assurance.",
            "A technically accurate model can still be unreliable if its input data is incomplete, invalid, stale, unreconciled or not traceable.",
        )
        questions = pd.DataFrame(
            [
                ("Who owns a data-quality issue?", "1LOD owns remediation; 2LOD challenges and oversees."),
                ("Can 2LOD fix the issue directly?", "No. 2LOD should challenge and monitor, while 1LOD owns the process correction."),
                ("Why can a technically accurate model still be unreliable?", "Because incorrect, missing or stale inputs can invalidate otherwise correct formulas."),
                ("What evidence is required before closure?", "Root cause, affected population, impact assessment, remediation proof, preventive control and 2LOD approval for material issues."),
                ("What is the difference between validation and audit?", "Validation challenges model/control design and performance; audit independently assures whether governance processes operate effectively."),
            ],
            columns=["question", "answer"],
        )
        st.dataframe(questions, width="stretch")
