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
from src.reporting.executive import management_actions
from src.reporting.finrep import finrep_metrics
from src.risk.basel import capital_after_provision, capital_ratios, rwa
from src.risk.climate import climate_adjusted_credit_risk, climate_portfolio_table
from src.risk.crr3 import crr3_total_rwa, cva_lite_capital, operational_risk_sma, output_floor
from src.risk.ifrs9 import assign_stage, calculate_ifrs9, expected_credit_loss
from src.risk.irb import irb_rwa_equivalent, simplified_irb_capital, standardized_rwa
from src.risk.liquidity import compliance, lcr, leverage_ratio, nsfr
from src.risk.reverse_stress import required_loss_for_target, reverse_stress_solver
from src.risk.stress_testing import SCENARIOS, stress_ecl
from src.risk.xva import xva_summary
from src.ui.components import teaching_block
from src.ui.study_guide import render_study_guide


st.set_page_config(page_title="European Financial Risk Platform", layout="wide")


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return load_customers(), load_loans(), load_transactions(), load_financials()


customers, loans_raw, transactions, financials = load_data()
loans = loans_raw.copy()
portfolio_pd = float(loans["pd"].fillna(loans["pd"].median()).mean())
portfolio_lgd = float(loans["lgd"].mean())
portfolio_ead = float(loans["ead"].sum())

st.sidebar.title("Risk Platform")
page = st.sidebar.radio(
    "Navigation",
    [
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
        "Documentation & Study Guide",
    ],
)

pd_shock = st.sidebar.slider("Portfolio PD shock", -20, 100, 0, 5) / 100
lgd_shock = st.sidebar.slider("Portfolio LGD shock", -20, 80, 0, 5) / 100
scenario = st.sidebar.selectbox("Scenario", list(SCENARIOS))
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

st.title("European Financial Risk, Regulatory, and Governance Platform")
st.caption("Independent educational portfolio project using synthetic data and simplified regulatory approximations.")


def metrics_row(items: list[tuple[str, str]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


if page == "Executive Overview":
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
    st.plotly_chart(px.histogram(loans, x="expected_loss", nbins=45, title="Expected loss distribution"), width="stretch")
    st.write("Management actions")
    for action in management_actions(ratios["cet1_ratio"], liq_lcr, liq_nsfr, quality_score):
        st.write(f"- {action}")
    teaching_block(
        "How do risk, capital, liquidity, financial crime, and governance connect in one executive view?",
        "Higher PD/LGD -> higher ECL -> higher provisions -> lower profit and CET1 -> lower COREP capital ratios.",
        "The dashboard turns model outputs into management decisions: capital planning, liquidity actions, collections, and data remediation.",
        "I built the platform to show the end-to-end chain from borrower risk to regulatory ratios, governance controls, and executive decisions.",
    )

elif page == "Credit Risk":
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

elif page == "IFRS 9 ECL":
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
    render_study_guide()

