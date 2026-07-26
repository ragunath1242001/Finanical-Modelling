from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data.loaders import load_customers, load_financials, load_loans, load_transactions
from src.financial_crime.aml import aml_alerts
from src.financial_crime.fraud import alert_queue, threshold_summary
from src.forecasting.forecasting import twelve_month_forecast
from src.governance.audit import log_event, read_events
from src.governance.ai_governance import ai_act_control_assessment, ai_risk_tier, fairness_gap
from src.governance.data_quality import run_quality_checks
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
from src.risk.basel import capital_after_provision, capital_ratios, rwa
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
from src.ui.components import teaching_block
from src.ui.study_guide import render_study_guide


st.set_page_config(page_title="European Financial Risk Platform", layout="wide")


def inject_custom_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #17202A;
            --muted: #5D6D7E;
            --panel: #FFFFFF;
            --line: #D9E2EC;
            --teal: #0F766E;
            --teal-dark: #115E59;
            --blue: #2563EB;
            --amber: #B7791F;
            --rose: #B42318;
            --soft-blue: #EAF2FF;
            --soft-teal: #E6F4F1;
            --soft-amber: #FFF7E6;
        }

        .stApp {
            background:
                linear-gradient(180deg, #F4F8FB 0%, #F7FAFC 42%, #F5F7FA 100%);
            color: var(--ink);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #102A43 0%, #123B52 58%, #0F766E 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.18);
        }

        section[data-testid="stSidebar"] * {
            color: #F8FAFC !important;
        }

        section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background: #FFFFFF;
            border-color: rgba(255, 255, 255, 0.44);
            border-radius: 8px;
        }

        section[data-testid="stSidebar"] div[data-baseweb="select"] span,
        section[data-testid="stSidebar"] div[data-baseweb="select"] input {
            color: #102A43 !important;
            -webkit-text-fill-color: #102A43 !important;
        }

        section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
            color: var(--teal) !important;
            fill: var(--teal) !important;
        }

        section[data-testid="stSidebar"] .stSlider [data-testid="stTickBar"] {
            background: rgba(255, 255, 255, 0.22);
        }

        .main .block-container {
            padding-top: 1.5rem;
            max-width: 1320px;
        }

        .app-hero {
            background:
                linear-gradient(135deg, rgba(15, 118, 110, 0.96), rgba(37, 99, 235, 0.86) 54%, rgba(183, 121, 31, 0.86));
            border: 1px solid rgba(255, 255, 255, 0.38);
            border-radius: 12px;
            padding: 1.25rem 1.35rem;
            margin: 0.25rem 0 1.2rem 0;
            box-shadow: 0 18px 45px rgba(16, 42, 67, 0.18);
        }

        .app-hero h1 {
            color: white;
            font-size: 2rem;
            line-height: 1.15;
            margin: 0 0 0.45rem 0;
            letter-spacing: 0;
        }

        .app-hero p {
            color: rgba(255, 255, 255, 0.9);
            margin: 0;
            max-width: 920px;
            font-size: 0.98rem;
        }

        .hero-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 0.85rem;
        }

        .hero-chip {
            border: 1px solid rgba(255, 255, 255, 0.36);
            background: rgba(255, 255, 255, 0.15);
            color: white;
            border-radius: 999px;
            padding: 0.28rem 0.65rem;
            font-size: 0.82rem;
            font-weight: 650;
        }

        h2, h3 {
            letter-spacing: 0;
            color: #102A43;
        }

        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-left: 4px solid var(--teal);
            border-radius: 10px;
            padding: 0.8rem 0.95rem;
            box-shadow: 0 10px 26px rgba(16, 42, 67, 0.08);
        }

        div[data-testid="stMetricLabel"] p {
            color: var(--muted);
            font-weight: 700;
        }

        div[data-testid="stMetricValue"] {
            color: var(--ink);
            font-weight: 800;
        }

        button[kind="primary"], div.stButton > button, div[data-testid="stDownloadButton"] button {
            border-radius: 8px;
            border: 1px solid rgba(15, 118, 110, 0.25);
            background: linear-gradient(135deg, var(--teal), var(--teal-dark));
            color: white;
            font-weight: 700;
            box-shadow: 0 10px 22px rgba(15, 118, 110, 0.18);
        }

        div.stButton > button:hover, div[data-testid="stDownloadButton"] button:hover {
            border-color: rgba(37, 99, 235, 0.55);
            box-shadow: 0 12px 28px rgba(37, 99, 235, 0.20);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem;
            border-bottom: 1px solid var(--line);
        }

        .stTabs [data-baseweb="tab"] {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-bottom: none;
            border-radius: 8px 8px 0 0;
            padding: 0.45rem 0.85rem;
            color: var(--muted);
            font-weight: 700;
        }

        .stTabs [aria-selected="true"] {
            background: var(--soft-teal);
            color: var(--teal-dark);
            border-color: rgba(15, 118, 110, 0.32);
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 8px 22px rgba(16, 42, 67, 0.06);
        }

        div[data-testid="stPlotlyChart"] {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: 0.35rem;
            box-shadow: 0 8px 22px rgba(16, 42, 67, 0.06);
        }

        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, textarea {
            border-radius: 8px;
            border-color: var(--line);
        }

        div[data-testid="stSlider"] {
            background: rgba(255, 255, 255, 0.55);
            border-radius: 10px;
            padding: 0.35rem 0.55rem 0.15rem 0.55rem;
        }

        div[data-testid="stExpander"] {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 10px;
            box-shadow: 0 8px 22px rgba(16, 42, 67, 0.05);
        }

        .cap-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(245px, 1fr));
            gap: 0.8rem;
            margin: 0.7rem 0 1rem 0;
        }

        .cap-card {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-top: 4px solid var(--teal);
            border-radius: 10px;
            padding: 0.95rem;
            box-shadow: 0 12px 28px rgba(16, 42, 67, 0.08);
            min-height: 148px;
        }

        .cap-icon {
            width: 2.1rem;
            height: 2.1rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            background: var(--soft-blue);
            color: var(--blue);
            font-weight: 900;
            margin-bottom: 0.55rem;
        }

        .cap-card h4 {
            margin: 0 0 0.35rem 0;
            color: #102A43;
            font-size: 1rem;
        }

        .cap-card p {
            color: var(--muted);
            font-size: 0.9rem;
            margin: 0;
            line-height: 1.42;
        }

        .stAlert {
            border-radius: 10px;
            border: 1px solid rgba(15, 118, 110, 0.2);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_app_header() -> None:
    st.markdown(
        """
        <div class="app-hero">
            <h1>European Financial Risk, Regulatory, and Governance Platform</h1>
            <p>Explore synthetic banking data from ingestion to credit risk, IFRS 9, capital, liquidity, financial crime, model risk, operational resilience, climate risk, XVA, and governance evidence.</p>
            <div class="hero-chips">
                <span class="hero-chip">Risk analytics</span>
                <span class="hero-chip">Regulatory reporting</span>
                <span class="hero-chip">Governance controls</span>
                <span class="hero-chip">Study guide</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_capability_cards() -> None:
    for row_start in range(0, len(CAPABILITY_MAP), 3):
        columns = st.columns(3)
        for column, capability in zip(columns, CAPABILITY_MAP[row_start : row_start + 3]):
            icon, area, description = capability
            with column:
                with st.container(border=True):
                    st.markdown(f"#### `{icon}` {area}")
                    st.write(description)


inject_custom_style()
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = ["#0F766E", "#2563EB", "#B7791F", "#B42318", "#4C6FFF", "#64748B"]


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return load_customers(), load_loans(), load_transactions(), load_financials()


customers, loans_raw, transactions, financials = load_data()
loans = loans_raw.copy()
portfolio_pd = float(loans["pd"].fillna(loans["pd"].median()).mean())
portfolio_lgd = float(loans["lgd"].mean())
portfolio_ead = float(loans["ead"].sum())

st.sidebar.markdown("### Risk Platform")
st.sidebar.caption("Scenario controls and navigation")
DOCS_PAGE = "Documentation & Study Guide"
MAIN_PAGES = [
    "Executive Overview",
    "Credit Risk",
    "IFRS 9 ECL",
    "Basel Capital and IRB",
    "CRR3 Basel Final Reforms",
    "COREP/FINREP Reporting",
    "Stress Testing",
    "Geopolitical Reverse Stress",
    "Liquidity and Leverage",
    "Fraud and AML",
    "Forecasting",
    "BCBS 239 Governance",
    "Model Risk Management",
    "EU AI Act Governance",
    "DORA Operational Resilience",
    "ESG Climate Credit Risk",
    "XVA Counterparty Risk",
]

if "page" not in st.session_state:
    st.session_state.page = "Executive Overview"


def set_main_page() -> None:
    st.session_state.page = st.session_state.main_page_select


selected_index = MAIN_PAGES.index(st.session_state.page) if st.session_state.page in MAIN_PAGES else 0
st.sidebar.selectbox(
    "Navigation",
    MAIN_PAGES,
    index=selected_index,
    key="main_page_select",
    on_change=set_main_page,
)

st.sidebar.divider()

pd_shock = st.sidebar.slider("Portfolio PD shock", -20, 100, 0, 5) / 100
lgd_shock = st.sidebar.slider("Portfolio LGD shock", -20, 80, 0, 5) / 100
scenario = st.sidebar.selectbox("Scenario", list(SCENARIOS))
st.sidebar.divider()
if st.sidebar.button(DOCS_PAGE):
    st.session_state.page = DOCS_PAGE

page = st.session_state.page
adjusted_pd = (loans["pd"].fillna(loans["pd"].median()) * (1 + pd_shock)).clip(0, 1)
adjusted_lgd = (loans["lgd"] * (1 + lgd_shock)).clip(0, 1)
loans["adjusted_pd"] = adjusted_pd
loans["adjusted_lgd"] = adjusted_lgd
loans["expected_loss"] = loans["adjusted_pd"] * loans["adjusted_lgd"] * loans["ead"]
portfolio_ecl = float(loans["expected_loss"].sum())

base_rwa = rwa(portfolio_ead, 0.55)
base_cet1 = 8_500_000.0
at1 = 750_000.0
tier2 = 1_100_000.0
stressed = stress_ecl(portfolio_pd, portfolio_lgd, portfolio_ead, SCENARIOS[scenario]["pd_multiplier"], SCENARIOS[scenario]["lgd_multiplier"])
post_cet1 = capital_after_provision(base_cet1, stressed["provision_increase"])
ratios = capital_ratios(post_cet1, at1, tier2, base_rwa)
liq_lcr = lcr(18_000_000, 14_500_000)
liq_nsfr = nsfr(74_000_000, 71_000_000)
quality_table, quality_score = run_quality_checks(loans_raw, customers)
fraud_scored = alert_queue(transactions, 0.35)
aml_scored = aml_alerts(transactions)

render_app_header()


def metrics_row(items: list[tuple[str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


FIELD_DEFINITIONS = {
    "customers": {
        "customer_id": "Synthetic customer identifier used to join customers, loans, and transactions.",
        "age": "Customer age.",
        "income": "Annual income; includes missing values for data quality testing.",
        "employment_status": "Employment category used in PD modelling and risk segmentation.",
        "credit_score": "Synthetic credit score used in PD, explainability, and model development.",
        "debt_to_income": "Debt-to-income ratio used as an affordability and credit risk driver.",
        "country": "Customer country code for portfolio segmentation.",
        "customer_risk": "Simple low/medium/high risk label for segmentation.",
    },
    "loans": {
        "loan_id": "Synthetic loan identifier.",
        "customer_id": "Customer join key.",
        "product_type": "Loan product such as mortgage, personal loan, credit card, or SME loan.",
        "loan_amount": "Original loan amount; includes negative records for quality checks.",
        "outstanding_balance": "Current balance before EAD conversion.",
        "ltv": "Loan-to-value ratio used in LGD and secured lending analysis.",
        "days_past_due": "Delinquency measure used for IFRS 9 staging and default identification.",
        "default_flag": "Synthetic default marker used for model development and validation.",
        "pd": "Probability of default used across ECL, stress testing, IRB, and XVA-style thinking.",
        "lgd": "Loss given default used in expected loss and provision calculations.",
        "ead": "Exposure at default used in ECL, capital, and concentration analysis.",
        "last_update_days": "Data freshness indicator used in governance checks.",
    },
    "transactions": {
        "transaction_id": "Synthetic transaction identifier.",
        "customer_id": "Customer join key.",
        "amount": "Transaction amount used by fraud and AML rules.",
        "merchant_category": "Merchant segment used for fraud indicators.",
        "hour": "Transaction hour used for behaviour context.",
        "country_risk": "Standard or high country risk flag for AML screening.",
        "device_mismatch": "Fraud signal showing whether the device differs from normal behaviour.",
        "velocity_24h": "Number of recent transactions used for velocity risk.",
        "round_amount": "AML indicator for unusually round amounts.",
        "rapid_in_out": "AML indicator for quick movement of funds.",
        "fraud_label": "Synthetic fraud outcome label for testing alert logic.",
    },
    "financials": {
        "month": "Monthly reporting period.",
        "loan_balances": "Portfolio loan balance trend for forecasting and FINREP-style analysis.",
        "deposit_balances": "Deposit trend used for balance sheet context.",
        "net_interest_income": "Monthly NII used in forecasting.",
        "provisions": "Monthly provision amount used in financial trend analysis.",
        "fraud_aml_alerts": "Monthly financial crime alert count.",
    },
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


def dataset_summary() -> pd.DataFrame:
    frames = {
        "Customers": customers,
        "Loans": loans_raw,
        "Transactions": transactions,
        "Financials": financials,
    }
    return pd.DataFrame(
        [
            {
                "dataset": name,
                "rows": len(frame),
                "fields": len(frame.columns),
                "missing_values": int(frame.isna().sum().sum()),
                "duplicate_rows": int(frame.duplicated().sum()),
            }
            for name, frame in frames.items()
        ]
    )


def field_inventory() -> pd.DataFrame:
    frames = {
        "customers": customers,
        "loans": loans_raw,
        "transactions": transactions,
        "financials": financials,
    }
    rows = []
    for dataset, frame in frames.items():
        for column in frame.columns:
            rows.append(
                {
                    "dataset": dataset,
                    "field": column,
                    "type": str(frame[column].dtype),
                    "missing": int(frame[column].isna().sum()),
                    "definition": FIELD_DEFINITIONS.get(dataset, {}).get(column, "Synthetic project field."),
                }
            )
    return pd.DataFrame(rows)


@st.cache_data
def run_credit_model_lab(customers_data: pd.DataFrame, loans_data: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    frame = prepare_model_frame(customers_data, loans_data)
    return frame, train_credit_models(frame)


def render_credit_portfolio_view() -> None:
    selected = st.selectbox("Customer loan", loans["loan_id"].head(200))
    row = loans.loc[loans["loan_id"].eq(selected)].iloc[0]
    customer = customers.loc[customers["customer_id"].eq(row["customer_id"])].iloc[0]
    pd_input = st.slider("PD", 0.0, 1.0, float(row["adjusted_pd"]), 0.005)
    lgd_input = st.slider("LGD", 0.0, 1.0, float(row["adjusted_lgd"]), 0.01)
    ead_input = st.number_input("EAD", min_value=0.0, value=float(row["ead"]), step=1000.0)
    ecl = expected_credit_loss(pd_input, lgd_input, ead_input)
    metrics_row([("PD", f"{pd_input:.2%}"), ("LGD", f"{lgd_input:.2%}"), ("EAD", f"EUR {ead_input:,.0f}"), ("Expected loss", f"EUR {ecl:,.0f}")])
    profile = pd.DataFrame([customer.to_dict() | row.to_dict()])
    st.dataframe(profile[["customer_id", "age", "income", "credit_score", "debt_to_income", "product_type", "loan_amount", "ltv", "days_past_due"]], width="stretch")
    st.write("Top reason codes")
    for reason in pd_reason_codes(profile.iloc[0]):
        st.write(f"- {reason}")
    st.dataframe(loans.nlargest(10, "expected_loss")[["loan_id", "customer_id", "product_type", "adjusted_pd", "adjusted_lgd", "ead", "expected_loss"]], width="stretch")
    teaching_block(
        "Which borrowers create the most expected loss and why?",
        f"ECL = PD x LGD x EAD = {pd_input:.4f} x {lgd_input:.4f} x {ead_input:,.0f} = EUR {ecl:,.0f}",
        "A large loan is not automatically the riskiest loan. Expected loss is multiplicative, so probability of default, loss severity, and exposure all matter.",
        "Credit risk combines default likelihood, loss severity, and exposure. I use PD, LGD, and EAD to rank customers and explain risk grades.",
    )


def render_credit_model_development_lab() -> None:
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


def render_ifrs9_ecl_calculator() -> None:
    col1, col2, col3 = st.columns(3)
    pd_input = col1.slider("PD", 0.0, 1.0, portfolio_pd, 0.005)
    lgd_input = col2.slider("LGD", 0.0, 1.0, portfolio_lgd, 0.01)
    ead_input = col3.number_input("EAD", min_value=0.0, value=250_000.0, step=10_000.0)
    dpd = st.slider("Days past due", 0, 150, 0)
    score_change = st.slider("Credit score change", -200, 50, -20)
    stress_flag = st.selectbox("Industry stress", ["normal", "high", "severe"])
    default_flag = st.checkbox("Default flag")
    stage, reason = assign_stage(dpd, score_change, stress_flag, default_flag)
    calc = calculate_ifrs9(pd_input, lgd_input, ead_input, stage)
    metrics_row([("Stage", str(stage)), ("12-month ECL", f"EUR {calc['12_month_ecl']:,.0f}"), ("Lifetime ECL", f"EUR {calc['lifetime_ecl']:,.0f}"), ("Provision", f"EUR {calc['provision']:,.0f}")])
    st.info(reason)
    teaching_block(
        "Why does a loan move between Stage 1, Stage 2, and Stage 3?",
        f"12-month ECL = {pd_input:.4f} x {lgd_input:.4f} x {ead_input:,.0f}; Stage {stage} provision = EUR {calc['provision']:,.0f}",
        "Stage 2 is based on significant increase in credit risk, not only default. Higher provisions reduce profit, retained earnings, and CET1.",
        "IFRS 9 asks what losses are expected. Stage 1 uses 12-month ECL, while Stage 2 and Stage 3 use lifetime ECL in this simplified model.",
    )


def render_ifrs9_scenario_ecl_engine() -> None:
    st.subheader("IFRS 9 Scenario ECL Engine")
    st.write("Scenario-weighted ECL with lifetime PD, stage migration, and provision movement analysis.")
    u1, u2, u3 = st.columns(3)
    upside_weight = u1.slider("Upside weight", 0.0, 1.0, 0.20, 0.05)
    baseline_weight = u2.slider("Baseline weight", 0.0, 1.0, 0.55, 0.05)
    downside_weight = u3.slider("Downside weight", 0.0, 1.0, 0.25, 0.05)
    total_weight = max(upside_weight + baseline_weight + downside_weight, 0.0001)
    scenarios = {
        "Upside": {"weight": upside_weight / total_weight, "pd_multiplier": 0.85, "lgd_multiplier": 0.95},
        "Baseline": {"weight": baseline_weight / total_weight, "pd_multiplier": 1.00, "lgd_multiplier": 1.00},
        "Downside": {"weight": downside_weight / total_weight, "pd_multiplier": st.slider("Downside PD multiplier", 1.0, 3.0, 1.65, 0.05), "lgd_multiplier": st.slider("Downside LGD multiplier", 1.0, 2.0, 1.20, 0.05)},
    }
    life = st.slider("Remaining life years for Stage 2/3", 1.0, 8.0, 4.0, 0.5)
    scenario_loans, scenario_summary = scenario_weighted_ecl(loans_raw, scenarios, life)
    weighted_ecl = float(scenario_loans["weighted_ecl"].sum())
    baseline_ecl = float(scenario_summary.loc[scenario_summary["scenario"].eq("Baseline"), "scenario_ecl"].iloc[0])
    migration = stage_migration_table(loans_raw, scenarios["Downside"]["pd_multiplier"])
    stage_migration_effect = max(0.0, weighted_ecl - baseline_ecl) * 0.35
    bridge = ecl_bridge(
        opening_ecl=baseline_ecl,
        new_lending=baseline_ecl * 0.08,
        repayments=baseline_ecl * 0.05,
        stage_migration=stage_migration_effect,
        macro_overlay=max(0.0, weighted_ecl - baseline_ecl) * 0.65,
    )
    metrics_row(
        [
            ("Baseline ECL", f"EUR {baseline_ecl:,.0f}"),
            ("Weighted ECL", f"EUR {weighted_ecl:,.0f}"),
            ("Overlay increase", f"EUR {max(0.0, weighted_ecl - baseline_ecl):,.0f}"),
            ("Scenario weights", f"{scenarios['Upside']['weight']:.0%}/{scenarios['Baseline']['weight']:.0%}/{scenarios['Downside']['weight']:.0%}"),
        ]
    )
    tab1, tab2, tab3, tab4 = st.tabs(["Scenario ECL", "Stage Migration", "ECL Bridge", "Loan Detail"])
    with tab1:
        st.dataframe(scenario_summary, width="stretch")
        st.download_button(
            "Download IFRS 9 scenario ECL CSV",
            dataframe_csv_bytes(scenario_summary),
            file_name="ifrs9_scenario_ecl.csv",
            mime="text/csv",
        )
        st.plotly_chart(px.bar(scenario_summary, x="scenario", y="scenario_ecl", color="scenario", title="ECL by macro scenario"), width="stretch")
    with tab2:
        st.dataframe(migration, width="stretch")
    with tab3:
        st.dataframe(bridge, width="stretch")
        st.download_button(
            "Download ECL bridge CSV",
            dataframe_csv_bytes(bridge),
            file_name="ifrs9_ecl_bridge.csv",
            mime="text/csv",
        )
        st.plotly_chart(px.bar(bridge, x="component", y="amount", title="Provision movement bridge"), width="stretch")
    with tab4:
        st.dataframe(scenario_loans[["loan_id", "customer_id", "base_stage", "upside_ecl", "baseline_ecl", "downside_ecl", "weighted_ecl"]].sort_values("weighted_ecl", ascending=False).head(30), width="stretch")
    teaching_block(
        "How does IFRS 9 use forward-looking scenarios?",
        "Weighted ECL = Upside ECL x weight + Baseline ECL x weight + Downside ECL x weight.",
        "IFRS 9 provisions should reflect forward-looking information. Scenario weights make the result more realistic than a single deterministic forecast.",
        "This engine shows loan-level stage assignment, lifetime PD, macro scenario weighting, stage migration, and an ECL bridge from opening to closing provision.",
    )


if page == "Executive Overview":
    st.subheader("Executive Overview")
    st.write("A single starting point for the data loaded into the platform, the risk signals calculated from it, and the modules available for learning and testing.")
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

    overview_tab, data_tab, capability_tab, action_tab = st.tabs(["Dashboard", "Data Ingested", "Learning & Testing", "Actions & Report"])

    with overview_tab:
        chart_left, chart_right = st.columns([1.4, 1])
        with chart_left:
            st.plotly_chart(px.histogram(loans, x="expected_loss", nbins=45, title="Expected loss distribution"), width="stretch")
        with chart_right:
            product_ecl = loans.groupby("product_type", as_index=False)["expected_loss"].sum().sort_values("expected_loss", ascending=False)
            st.plotly_chart(px.bar(product_ecl, x="product_type", y="expected_loss", title="Expected loss by product"), width="stretch")
        split_left, split_right = st.columns(2)
        with split_left:
            stage_counts = (
                loans_raw.assign(
                    stage=loans_raw.apply(
                        lambda row: f"Stage {assign_stage(int(row['days_past_due']), default_flag=bool(row['default_flag']))[0]}",
                        axis=1,
                    )
                )["stage"]
                .value_counts()
                .rename_axis("stage")
                .reset_index(name="loans")
            )
            st.plotly_chart(px.pie(stage_counts, names="stage", values="loans", title="IFRS 9 stage mix"), width="stretch")
        with split_right:
            crime_counts = fraud_scored["risk_label"].value_counts().rename_axis("risk_label").reset_index(name="transactions")
            st.plotly_chart(px.bar(crime_counts, x="risk_label", y="transactions", title="Fraud alert distribution"), width="stretch")

    with data_tab:
        st.write("These are the synthetic datasets currently loaded into the app and used across the risk, reporting, financial crime, and governance modules.")
        st.dataframe(dataset_summary(), width="stretch")
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
                loans.groupby("product_type", as_index=False)
                .agg(loans=("loan_id", "count"), ead=("ead", "sum"), expected_loss=("expected_loss", "sum"))
                .sort_values("expected_loss", ascending=False),
                width="stretch",
            )
        with data_right:
            st.subheader("Data Quality Signals")
            st.dataframe(quality_table, width="stretch")
        st.subheader("Field Inventory")
        st.dataframe(field_inventory(), width="stretch", height=420)

    with capability_tab:
        st.write("Use this view as a map of what the platform can help you understand, test, and explain.")
        render_capability_cards()
        capability_frame = pd.DataFrame(CAPABILITY_MAP, columns=["icon", "area", "what_you_can_learn_or_test"])
        st.dataframe(capability_frame[["area", "what_you_can_learn_or_test"]], width="stretch", hide_index=True)
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

elif page == "Credit Risk":
    credit_mode = st.segmented_control("Mode", ["Portfolio Risk View", "Model Development Lab"], default="Portfolio Risk View")
    if credit_mode == "Model Development Lab":
        render_credit_model_development_lab()
    else:
        render_credit_portfolio_view()

elif page == "IFRS 9 ECL":
    ifrs9_mode = st.segmented_control("Mode", ["ECL Calculator", "Scenario ECL Engine"], default="ECL Calculator")
    if ifrs9_mode == "Scenario ECL Engine":
        render_ifrs9_scenario_ecl_engine()
    else:
        render_ifrs9_ecl_calculator()

elif page == "Basel Capital and IRB":
    exposure = st.number_input("Exposure", min_value=1.0, value=1_000_000.0, step=50_000.0)
    risk_weight = st.slider("Standardized risk weight", 0.0, 1.5, 0.75, 0.05)
    pd_input = st.slider("IRB PD", 0.001, 0.5, 0.035, 0.001)
    lgd_input = st.slider("IRB LGD", 0.05, 0.95, 0.45, 0.01)
    std = standardized_rwa(exposure, risk_weight)
    irb_cap = simplified_irb_capital(pd_input, lgd_input, exposure)
    irb_rwa = irb_rwa_equivalent(irb_cap)
    basel_ratios = capital_ratios(120_000, 20_000, 30_000, std)
    metrics_row([("Standardized RWA", f"EUR {std:,.0f}"), ("IRB capital estimate", f"EUR {irb_cap:,.0f}"), ("IRB RWA equivalent", f"EUR {irb_rwa:,.0f}"), ("CET1 ratio", f"{basel_ratios['cet1_ratio']:.2%}")])
    st.warning("IRB output is a simplified educational approximation, not a full regulatory IRB implementation.")
    teaching_block(
        "How do standardized and internal-model capital views differ?",
        "Standardized RWA = exposure x risk weight. Simplified IRB capital = sqrt(PD) x LGD x EAD x 1.06.",
        "IFRS 9 asks what losses are expected; IRB asks how much capital should be held for risk. Similar inputs serve different regulatory objectives.",
        "I compare standardized and internal-model views while clearly labeling the IRB approximation as educational.",
    )

elif page == "CRR3 Basel Final Reforms":
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
    st.plotly_chart(px.bar(pd.DataFrame({"component": ["Binding credit RWA", "Market RWA", "CVA RWA", "Operational RWA"], "amount": [floor["binding_rwa"], market_rwa, cva["cva_rwa"], op_risk["operational_risk_rwa"]]}), x="component", y="amount", title="CRR3 RWA stack"), width="stretch")
    teaching_block(
        "How do final Basel III / CRR3 reforms change capital analysis?",
        "Output floor = max(internal model RWA, standardized RWA x floor rate). Total RWA adds credit, market, CVA, and operational risk.",
        "The final reforms reduce excessive RWA variability by constraining internal models and adding more standardized treatment for CVA and operational risk.",
        "I can explain CRR3 as a capital comparability reform: even if an internal model produces low RWA, the output floor can increase binding capital requirements.",
    )

elif page == "COREP/FINREP Reporting":
    finrep = finrep_metrics(120_000_000, 108_000_000, 3_600_000, portfolio_ecl, 1_800_000)
    corep = corep_metrics(base_cet1 - portfolio_ecl, at1, tier2, base_rwa, portfolio_ead)
    metrics_row([("FINREP profit", f"EUR {finrep['profit']:,.0f}"), ("FINREP equity", f"EUR {finrep['equity']:,.0f}"), ("COREP CET1", f"{corep['cet1_ratio']:.2%}"), ("Capital status", corep["capital_adequacy_status"])])
    rec = reconcile_exposure(portfolio_ead, portfolio_ead * 1.012)
    st.dataframe(rec, width="stretch")
    teaching_block(
        "How do financial reporting and capital reporting connect?",
        "Provision expense lowers FINREP profit; retained earnings are part of CET1, so provisions can reduce COREP capital ratios.",
        "FINREP explains financial performance and position. COREP explains regulatory capital adequacy and risk-weighted exposure.",
        "A PD shock flows through IFRS 9 provisions into profit, retained earnings, CET1, and capital ratio reporting.",
    )

elif page == "Stress Testing":
    pd_mult = st.slider("PD multiplier", 0.5, 3.0, SCENARIOS[scenario]["pd_multiplier"], 0.05)
    lgd_mult = st.slider("LGD multiplier", 0.5, 2.0, SCENARIOS[scenario]["lgd_multiplier"], 0.05)
    revenue_shock = st.slider("Revenue shock", -0.5, 0.2, SCENARIOS[scenario]["revenue_shock"], 0.01)
    result = stress_ecl(portfolio_pd, portfolio_lgd, portfolio_ead, pd_mult, lgd_mult)
    stressed_cet1 = capital_after_provision(base_cet1, result["provision_increase"])
    stressed_ratio = capital_ratios(stressed_cet1, at1, tier2, base_rwa)["cet1_ratio"]
    metrics_row([("Stressed PD", f"{result['stressed_pd']:.2%}"), ("Stressed LGD", f"{result['stressed_lgd']:.2%}"), ("Provision increase", f"EUR {result['provision_increase']:,.0f}"), ("Post-stress CET1 ratio", f"{stressed_ratio:.2%}")])
    waterfall = pd.DataFrame({"step": ["Opening CET1", "Provision increase", "Revenue shock", "Closing CET1"], "amount": [base_cet1, -result["provision_increase"], base_cet1 * revenue_shock, stressed_cet1 + base_cet1 * revenue_shock]})
    st.plotly_chart(px.bar(waterfall, x="step", y="amount", title="Capital impact bridge"), width="stretch")
    teaching_block(
        "What happens to provisions and capital under adverse macroeconomic scenarios?",
        "Stressed ECL = stressed PD x stressed LGD x EAD; provision increase reduces CET1.",
        "Stress testing supports capital planning by showing whether management should reduce dividends, raise capital, slow risky growth, or tighten lending.",
        "I use baseline, adverse, and severe scenarios to connect macro shocks with PD, LGD, ECL, profit, and CET1 ratio impacts.",
    )

elif page == "Geopolitical Reverse Stress":
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

elif page == "Liquidity and Leverage":
    tier1 = st.number_input("Tier 1 capital", min_value=1.0, value=base_cet1 + at1, step=100_000.0)
    total_exposure = st.number_input("Total exposure", min_value=1.0, value=portfolio_ead, step=1_000_000.0)
    hqla = st.number_input("HQLA", min_value=1.0, value=18_000_000.0, step=500_000.0)
    outflows = st.number_input("30-day net cash outflows", min_value=1.0, value=14_500_000.0, step=500_000.0)
    asf = st.number_input("Available stable funding", min_value=1.0, value=74_000_000.0, step=1_000_000.0)
    rsf = st.number_input("Required stable funding", min_value=1.0, value=71_000_000.0, step=1_000_000.0)
    lev, lcr_value, nsfr_value = leverage_ratio(tier1, total_exposure), lcr(hqla, outflows), nsfr(asf, rsf)
    metrics_row([("Leverage ratio", f"{lev:.2%}"), ("LCR", f"{lcr_value:.1%}"), ("NSFR", f"{nsfr_value:.1%}"), ("NSFR status", compliance(nsfr_value, 1.0))])
    teaching_block(
        "Can a bank be solvent but still face liquidity stress?",
        "Leverage = Tier 1 / exposure; LCR = HQLA / 30-day outflows; NSFR = ASF / RSF.",
        "Capital measures solvency. LCR measures 30-day liquidity survival. NSFR measures longer-term stable funding.",
        "A bank can meet capital ratios but still be vulnerable if liquidity buffers or stable funding are weak.",
    )

elif page == "Fraud and AML":
    threshold = st.slider("Fraud threshold", 0.05, 0.95, 0.35, 0.01)
    fraud_scored = alert_queue(transactions, threshold)
    summary = threshold_summary(fraud_scored)
    metrics_row([("Fraud alerts", f"{summary['alerts']:,}"), ("Precision", f"{summary['precision']:.1%}"), ("Recall", f"{summary['recall']:.1%}"), ("AML high priority", f"{int(aml_scored['investigation_priority'].eq('High').sum()):,}")])
    tab1, tab2 = st.tabs(["Fraud queue", "AML queue"])
    tab1.dataframe(fraud_scored.head(25), width="stretch")
    tab2.dataframe(aml_scored.head(25), width="stretch")
    teaching_block(
        "How do fraud detection and AML monitoring differ?",
        "Fraud score prioritizes transaction abuse probability. AML score prioritizes suspicious behavior such as structuring and high-risk jurisdictions.",
        "Fraud models optimize alert thresholds under class imbalance. AML systems often create false positives because rules intentionally cast a wide net for investigation.",
        "Fraud asks whether a transaction may be unauthorized or abusive; AML asks whether behavior may indicate money laundering or sanctions risk.",
    )

elif page == "Forecasting":
    target = st.selectbox("Forecast target", ["loan_balances", "deposit_balances", "net_interest_income", "provisions", "fraud_aml_alerts"])
    macro = st.slider("Macro scenario multiplier", 0.7, 1.3, 1.0, 0.01)
    forecast = twelve_month_forecast(financials[target], macro)
    st.plotly_chart(px.line(forecast, x="month_ahead", y=["forecast", "lower", "upper"], title=f"12-month forecast: {target}"), width="stretch")
    st.dataframe(forecast, width="stretch")
    teaching_block(
        "How do planning forecasts feed stress testing and capital planning?",
        "Forecast = recent trend extrapolation x macro multiplier, with simple uncertainty bands.",
        "Forecasts provide the forward-looking baseline that stress testing can shock for provisions, revenue, capital, and alert volume.",
        "I use a transparent baseline forecast so assumptions are easy to challenge in planning and governance discussions.",
    )

elif page == "BCBS 239 Governance":
    metrics_row([("Data quality score", f"{quality_score:.1f}%"), ("Failed controls", f"{int(quality_table['status'].eq('Fail').sum())}"), ("Open reconciliation", "Yes"), ("Audit events", f"{len(read_events()):,}")])
    st.dataframe(quality_table, width="stretch")
    st.download_button(
        "Download BCBS 239 issue log",
        dataframe_csv_bytes(quality_table),
        file_name="bcbs239_issue_log.csv",
        mime="text/csv",
    )
    st.write("Lineage")
    st.write(" -> ".join(LINEAGE_STEPS))
    st.dataframe(reconcile_exposure(portfolio_ead, portfolio_ead * 1.012), width="stretch")
    if st.button("Log BCBS 239 remediation action"):
        log_event("portfolio-user", "BCBS 239 Governance", "Data quality issue opened", "", "Open", "Missing PD remediation")
        st.success("Audit event written.")
    st.dataframe(read_events(), width="stretch")
    teaching_block(
        "Why does BCBS 239 matter for risk and regulatory reporting?",
        "Quality score combines completeness, accuracy, consistency, timeliness, and traceability controls.",
        "A sophisticated model is not enough if exposure, PD, or customer identifiers are missing, stale, duplicated, or inconsistent between finance and risk.",
        "BCBS 239 ensures risk reports are accurate, complete, timely, consistent, and traceable enough for management and regulators.",
    )

elif page == "Model Risk Management":
    st.dataframe(model_inventory(), width="stretch")
    st.dataframe(validation_findings(), width="stretch")
    drift = mean_drift(loans["pd"].fillna(loans["pd"].median()).iloc[: len(loans) // 2], loans["pd"].fillna(loans["pd"].median()).iloc[len(loans) // 2 :])
    metrics_row([("PD baseline mean", f"{drift['baseline_mean']:.2%}"), ("PD current mean", f"{drift['current_mean']:.2%}"), ("Relative drift", f"{drift['relative_change']:.1%}"), ("Drift status", str(drift["status"]))])
    st.write("Lifecycle: Development -> Validation -> Approval -> Deployment -> Monitoring -> Retirement")
    st.dataframe(issue_queue(), width="stretch")
    teaching_block(
        "How are models governed after development?",
        "Inventory + validation findings + monitoring metrics + issue workflow provide evidence of model control.",
        "Model risk management separates development performance from independent validation and post-deployment monitoring.",
        "A model is not finished when trained; it needs validation, approval, monitoring, explainability, issue management, and auditability.",
    )

elif page == "EU AI Act Governance":
    st.subheader("EU AI Act and High-Risk AI Governance Control Room")
    use_case = st.selectbox("AI use case", ["Credit scoring", "AML monitoring", "Fraud detection", "Customer service triage", "Forecasting"])
    automated = st.checkbox("Automated decision or recommendation", value=True)
    affects_credit = st.checkbox("Affects access to credit or financial services", value=use_case == "Credit scoring")
    tier = ai_risk_tier(use_case, automated, affects_credit)
    st.metric("Illustrative AI risk tier", tier)
    st.write("Control implementation")
    controls = {
        "risk_management": st.checkbox("Risk management system", value=True),
        "data_governance": st.checkbox("Training/validation/test data governance", value=True),
        "technical_documentation": st.checkbox("Technical documentation", value=True),
        "logging_traceability": st.checkbox("Logging and traceability", value=True),
        "transparency_explainability": st.checkbox("Transparency and explainability", value=True),
        "human_oversight": st.checkbox("Human oversight and override", value=False),
        "accuracy_robustness": st.checkbox("Accuracy, robustness, and cybersecurity testing", value=False),
        "post_market_monitoring": st.checkbox("Post-deployment monitoring", value=True),
    }
    control_table, score = ai_act_control_assessment(controls)
    a1, a2 = st.columns(2)
    rate_a = a1.slider("Approval rate group A", 0.0, 1.0, 0.68, 0.01)
    rate_b = a2.slider("Approval rate group B", 0.0, 1.0, 0.55, 0.01)
    fair = fairness_gap(rate_a, rate_b)
    metrics_row([("Control score", f"{score:.0f}/100"), ("Open gaps", f"{int(control_table['status'].eq('Gap').sum())}"), ("Fairness gap", f"{fair['absolute_gap']:.1%}"), ("Fairness status", str(fair["status"]))])
    st.dataframe(control_table, width="stretch")
    if st.button("Log AI governance review"):
        log_event("portfolio-user", "EU AI Act Governance", "AI control review completed", "", f"{score:.0f}/100", tier)
        st.success("AI governance audit event written.")
    teaching_block(
        "What controls are expected around high-risk AI in financial services?",
        "Control score = weighted implementation of risk management, data governance, documentation, logging, explainability, oversight, robustness, and monitoring.",
        "For credit, fraud, and AML models, strong governance means decisions can be explained, challenged, monitored, audited, and overridden by accountable humans.",
        "I treat AI governance as part of model risk management: the model must be accurate, explainable, documented, monitored, fair, and traceable.",
    )

elif page == "DORA Operational Resilience":
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

elif page == "ESG Climate Credit Risk":
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

elif page == "XVA Counterparty Risk":
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

else:
    render_study_guide(loans_raw, base_cet1, base_rwa)

