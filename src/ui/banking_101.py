from __future__ import annotations

import pandas as pd
import streamlit as st

from src.reporting.downloads import pdf_report_bytes


BANKING_101_TOPICS: list[dict[str, object]] = [
    {
        "area": "Banking Basics",
        "topic": "What a Bank Does",
        "beginner_meaning": [
            "A bank is an institution that moves money between people or companies who have surplus cash and people or companies who need funding.",
            "Customers deposit money into the bank. The bank uses part of that funding to make loans, buy safe assets, provide payments, and support financial services.",
            "The bank earns income mainly by charging more interest on loans than it pays on deposits. This difference is called net interest income.",
            "A bank also earns fees from payments, cards, accounts, advisory services, trading, and other financial products.",
            "Because banks use other people's money, they are regulated heavily. Regulators want banks to lend responsibly, hold enough capital, keep enough liquidity, and report their risks clearly.",
        ],
        "why_it_matters": [
            "Almost every risk topic in the platform starts with the bank balance sheet: loans create credit risk, deposits create liquidity risk, and capital absorbs losses.",
            "Understanding what a bank does makes it easier to understand why PD, ECL, CET1, LCR, and COREP matter.",
        ],
        "project_use": [
            "The Executive Overview connects loan losses, provisions, liquidity metrics, capital ratios, financial crime alerts, governance issues, and management actions.",
            "The synthetic datasets represent customers, loans, transactions, and financial statements, which are the core data building blocks of a bank.",
        ],
        "simple_example": [
            "A customer deposits EUR 10,000. The bank may keep some as liquid cash and use some to fund loans.",
            "If the bank lends EUR 8,000 at 6% and pays deposit interest at 2%, the bank earns a spread, but it also takes credit and liquidity risk.",
        ],
        "memory_hook": "Banking is about maturity transformation: deposits are often short-term, while loans are often longer-term.",
        "self_checks": [
            ("Why are banks regulated?", "Because banks use public deposits, support payments, create credit, and can affect the wider economy if they fail."),
            ("What is the basic way a traditional bank earns money?", "It earns a spread between interest charged on loans and interest paid on funding such as deposits."),
        ],
    },
    {
        "area": "Banking Basics",
        "topic": "Bank Balance Sheet",
        "beginner_meaning": [
            "A balance sheet shows what a bank owns, what it owes, and what belongs to shareholders.",
            "Assets are things the bank owns or has claims on. For a bank, loans are usually a major asset because borrowers owe money to the bank.",
            "Liabilities are things the bank owes to others. Customer deposits are liabilities because the bank owes that money back to depositors.",
            "Equity is the owners' stake in the bank. It acts as a loss-absorbing layer after profits and reserves.",
            "The basic accounting identity is: Assets = Liabilities + Equity.",
        ],
        "why_it_matters": [
            "Credit risk affects assets because borrowers may not repay loans.",
            "Liquidity risk affects liabilities because depositors or wholesale funders may withdraw money.",
            "Capital risk affects equity because losses reduce profit, retained earnings, and regulatory capital.",
        ],
        "project_use": [
            "The app uses loan EAD as exposure on the asset side.",
            "The IFRS 9 page shows how provisions reduce profit and can reduce CET1 through retained earnings.",
            "The Liquidity page shows whether liquid assets and stable funding are enough compared with outflows and required funding.",
        ],
        "simple_example": [
            "Assets: EUR 100m loans and securities.",
            "Liabilities: EUR 90m deposits and borrowings.",
            "Equity: EUR 10m capital. If the bank takes EUR 2m of losses, equity may fall from EUR 10m to EUR 8m.",
        ],
        "memory_hook": "Loans sit mainly on the asset side; deposits sit mainly on the liability side; capital sits in equity.",
        "self_checks": [
            ("Why is a customer deposit a liability for the bank?", "Because the bank owes that money back to the customer."),
            ("What happens to equity when losses increase?", "Equity can fall because losses reduce profit and retained earnings."),
        ],
    },
    {
        "area": "Loans",
        "topic": "Basic Loan Concepts",
        "beginner_meaning": [
            "A loan is money given by a lender to a borrower with an agreement that it will be repaid over time.",
            "Principal is the original amount borrowed or the remaining amount owed.",
            "Interest is the cost the borrower pays for using the lender's money.",
            "Tenor or maturity is the time period over which the loan must be repaid.",
            "Repayment can happen through monthly instalments, bullet repayment at maturity, or other structures.",
            "Outstanding balance is the amount still owed today.",
        ],
        "why_it_matters": [
            "Loan structure affects risk. Longer tenor gives more time for borrower circumstances to change.",
            "Higher outstanding balance increases exposure if the borrower defaults.",
            "Interest income is attractive, but credit losses can offset that income if underwriting is weak.",
        ],
        "project_use": [
            "The Credit Risk page lets you select customer loans and view PD, LGD, EAD, expected loss, and reason codes.",
            "The Executive Overview summarizes total exposure, average PD, average LGD, and expected loss from the loan portfolio.",
        ],
        "simple_example": [
            "A borrower takes a EUR 200,000 mortgage at 4% interest for 25 years.",
            "The borrower repays monthly. If the borrower loses income and stops paying, the bank faces credit risk.",
        ],
        "memory_hook": "Loan risk is not only about how much was borrowed; it is also about the borrower's ability and willingness to repay.",
        "self_checks": [
            ("What is outstanding balance?", "The amount the borrower still owes at a point in time."),
            ("Why can longer-tenor loans be riskier?", "There is more time for income, employment, collateral value, and economic conditions to change."),
        ],
    },
    {
        "area": "Loans",
        "topic": "Banking Products",
        "beginner_meaning": [
            "A mortgage is a loan secured by property. If the borrower defaults, the bank may recover money by selling the property.",
            "A personal loan is usually lent to an individual and may be unsecured, meaning there may be no strong collateral.",
            "A credit card gives a customer a revolving credit limit. The customer can borrow, repay, and borrow again within the limit.",
            "An SME loan is given to a small or medium-sized business. It depends on business cash flow, owner strength, collateral, and sector conditions.",
            "A corporate loan is given to a larger company and may depend on financial statements, leverage, cash flow, covenants, and market conditions.",
            "A deposit account is money placed by a customer with the bank. For the bank, deposits are funding and also liabilities.",
        ],
        "why_it_matters": [
            "Different products have different PD, LGD, EAD, data, regulation, and monitoring needs.",
            "Secured products often have lower LGD because collateral can reduce loss.",
            "Unsecured products can have higher LGD because the bank may recover less after default.",
        ],
        "project_use": [
            "The app groups loans by product type and shows which products contribute most to exposure and expected loss.",
            "The Credit Risk and IFRS 9 pages use product-level differences to explain portfolio risk.",
        ],
        "simple_example": [
            "A EUR 300,000 mortgage with property collateral may have lower LGD than a EUR 20,000 unsecured personal loan.",
            "The personal loan is smaller, but if default happens, the recovery may be much lower.",
        ],
        "memory_hook": "Secured loans have a second way out: repayment from the borrower or recovery from collateral.",
        "self_checks": [
            ("Why can a mortgage have lower LGD than a personal loan?", "Because the property collateral may be sold to recover part of the exposure."),
            ("Why are credit cards called revolving credit?", "Because customers can borrow and repay repeatedly within an approved limit."),
        ],
    },
    {
        "area": "Credit Risk",
        "topic": "What Credit Risk Means",
        "beginner_meaning": [
            "Credit risk is the risk that a borrower does not repay as promised.",
            "Default usually means the borrower has missed payments for a defined period, is unlikely to pay, or has entered a formal failure/restructuring process.",
            "Credit risk is not only about default. It also includes early warning signs such as missed payments, falling credit score, high debt burden, weak cash flow, or sector stress.",
            "Banks manage credit risk before lending, while lending, and after lending.",
            "Before lending, banks assess affordability, collateral, credit history, and purpose of borrowing. After lending, they monitor behaviour and update risk estimates.",
        ],
        "why_it_matters": [
            "Credit losses are one of the main reasons banks can lose money.",
            "Credit risk feeds IFRS 9 provisions, Basel capital, stress testing, management actions, and regulatory reporting.",
        ],
        "project_use": [
            "The app estimates expected loss using PD, LGD, and EAD.",
            "It shows how shocks to PD and LGD affect expected loss, provisions, CET1, and capital ratios.",
        ],
        "simple_example": [
            "A borrower with unstable income and high debt may have higher PD than a borrower with stable income and low debt.",
            "If two borrowers owe the same amount, the one with weaker repayment capacity usually creates more credit risk.",
        ],
        "memory_hook": "Credit risk asks: will the borrower pay, and what happens if they do not?",
        "self_checks": [
            ("Is credit risk only about defaulted loans?", "No. It also includes deterioration before default."),
            ("Why does credit risk connect to capital?", "Because unexpected losses can reduce capital, and regulators require banks to hold capital against risky exposures."),
        ],
    },
    {
        "area": "Credit Risk",
        "topic": "PD, LGD, EAD and Expected Loss",
        "beginner_meaning": [
            "PD means Probability of Default. It is the chance that the borrower defaults within a defined period.",
            "LGD means Loss Given Default. It is the percentage of exposure the bank expects to lose if default happens, after collateral and recoveries.",
            "EAD means Exposure at Default. It is the amount the bank expects to be exposed to when default occurs.",
            "Expected Loss converts credit risk into money.",
            "The core formula is: Expected Loss = PD x LGD x EAD.",
        ],
        "why_it_matters": [
            "PD, LGD, and EAD are the foundation of credit risk, IFRS 9, stress testing, IRB capital modelling, and portfolio monitoring.",
            "Changing only one component can materially change loss estimates.",
        ],
        "project_use": [
            "The Credit Risk page shows expected loss for selected loans.",
            "The sidebar PD and LGD shocks let you see how portfolio-level deterioration changes expected loss and executive metrics.",
            "The IFRS 9 page uses PD, LGD, and EAD to calculate 12-month and lifetime expected credit loss.",
        ],
        "simple_example": [
            "PD = 2%, LGD = 40%, EAD = EUR 100,000.",
            "Expected Loss = 0.02 x 0.40 x 100,000 = EUR 800.",
            "This does not mean the bank will definitely lose EUR 800. It is a probability-weighted average loss estimate.",
        ],
        "memory_hook": "PD = chance, LGD = severity, EAD = amount, EL = money impact.",
        "self_checks": [
            ("If PD doubles and LGD/EAD stay the same, what happens to expected loss?", "Expected loss doubles."),
            ("Why is LGD lower for some secured loans?", "Collateral and recoveries can reduce the final loss after default."),
        ],
    },
    {
        "area": "Credit Risk",
        "topic": "Collateral, Mortgage and LTV",
        "beginner_meaning": [
            "Collateral is an asset pledged by the borrower to support the loan.",
            "A mortgage is usually secured by property, which means the property acts as collateral.",
            "If the borrower defaults, the bank may recover money by selling the collateral, subject to legal process, time, market prices, and costs.",
            "Loan-to-value, or LTV, compares the loan amount to the collateral value.",
            "LTV formula: LTV = Loan Amount / Property Value.",
            "A high LTV means the loan is large compared with the collateral value. A low LTV gives the bank more protection if property prices fall.",
        ],
        "why_it_matters": [
            "Collateral can reduce LGD, but it does not remove risk completely.",
            "Property prices can fall, legal recovery can take time, and sale proceeds may be lower than expected.",
            "Recruiters often expect basic understanding of mortgage risk, LTV, collateral valuation, and recovery risk for credit risk roles.",
        ],
        "project_use": [
            "The platform uses LGD to represent loss severity after recoveries.",
            "Climate and stress testing pages show how economic or climate shocks can increase risk, including risk linked to collateral-heavy portfolios.",
        ],
        "simple_example": [
            "Loan amount = EUR 180,000. Property value = EUR 300,000.",
            "LTV = 180,000 / 300,000 = 60%.",
            "If property value falls to EUR 200,000, LTV becomes 90%, so the bank has less protection.",
        ],
        "memory_hook": "LTV tells you how much cushion the collateral gives the bank.",
        "self_checks": [
            ("What does high LTV indicate?", "The loan is large relative to the collateral value, so the bank has less collateral cushion."),
            ("Does collateral remove credit risk?", "No. It reduces loss severity, but recovery can be uncertain, slow, and costly."),
        ],
    },
    {
        "area": "Accounting and Regulation",
        "topic": "Provisioning and IFRS 9",
        "beginner_meaning": [
            "A provision is money the bank recognizes as an expected credit loss expense.",
            "IFRS 9 is an accounting standard that requires banks to recognize expected credit losses before the loss fully happens.",
            "Stage 1 usually means the loan is performing and has not significantly worsened.",
            "Stage 2 means credit risk has increased significantly, but the loan is not defaulted.",
            "Stage 3 means the loan is defaulted or credit-impaired.",
            "Stage 1 uses 12-month expected credit loss. Stage 2 and Stage 3 use lifetime expected credit loss.",
        ],
        "why_it_matters": [
            "IFRS 9 links risk modelling to financial statements.",
            "When expected losses increase, provisions increase. Higher provisions reduce profit.",
            "Lower profit can reduce retained earnings, and retained earnings are part of CET1 capital.",
        ],
        "project_use": [
            "The IFRS 9 page assigns stages and calculates 12-month ECL, lifetime ECL, provisions, profit impact, retained earnings impact, and CET1 impact.",
            "The IFRS 9 Scenario ECL Engine shows scenario-weighted ECL and stage migration.",
        ],
        "simple_example": [
            "A performing loan may be Stage 1 with 12-month ECL of EUR 500.",
            "If the borrower deteriorates and moves to Stage 2, lifetime ECL may become EUR 2,500.",
            "The provision increase can reduce profit immediately.",
        ],
        "memory_hook": "Stage 1 = normal, Stage 2 = worsened, Stage 3 = defaulted.",
        "self_checks": [
            ("Is Stage 2 the same as default?", "No. Stage 2 means significant increase in credit risk before default."),
            ("Why does IFRS 9 matter for capital?", "Higher provisions reduce profit and retained earnings, which can reduce CET1."),
        ],
    },
    {
        "area": "Accounting and Regulation",
        "topic": "Capital, RWA and CET1",
        "beginner_meaning": [
            "Capital is the bank's loss-absorbing financial cushion.",
            "CET1 means Common Equity Tier 1. It is the highest-quality regulatory capital and mainly includes common equity and retained earnings after regulatory adjustments.",
            "RWA means Risk-Weighted Assets. It adjusts exposures by riskiness instead of treating every asset as equally risky.",
            "A safer exposure receives a lower risk weight. A riskier exposure receives a higher risk weight.",
            "CET1 ratio formula: CET1 Ratio = CET1 Capital / RWA.",
            "Regulators monitor capital ratios to judge whether a bank has enough cushion to absorb losses.",
        ],
        "why_it_matters": [
            "A bank can have a large balance sheet but still be safe if it has enough high-quality capital relative to risk.",
            "Losses, provisions, and RWA increases can weaken capital ratios.",
            "Risk roles often require understanding how credit risk turns into capital impact.",
        ],
        "project_use": [
            "The Basel Capital and IRB page calculates simplified capital ratios and RWA.",
            "The CRR3 page adds Basel final reform concepts such as output floor and capital impact.",
            "The Executive Overview shows how ECL and stress losses can reduce CET1 ratios.",
        ],
        "simple_example": [
            "CET1 = EUR 10m. RWA = EUR 100m.",
            "CET1 Ratio = 10m / 100m = 10%.",
            "If losses reduce CET1 to EUR 8m while RWA stays EUR 100m, the CET1 ratio falls to 8%.",
        ],
        "memory_hook": "CET1 is the cushion; RWA is the risk-adjusted denominator.",
        "self_checks": [
            ("Why do banks use RWA instead of total assets only?", "Because different assets have different risk levels."),
            ("What happens to CET1 ratio if CET1 falls and RWA stays constant?", "The CET1 ratio falls."),
        ],
    },
    {
        "area": "Liquidity",
        "topic": "Liquidity, LCR and NSFR",
        "beginner_meaning": [
            "Liquidity is the bank's ability to meet cash obligations when they come due.",
            "A bank can be profitable on paper but still fail if it cannot pay deposit withdrawals or funding obligations on time.",
            "LCR means Liquidity Coverage Ratio. It checks whether the bank has enough high-quality liquid assets to survive short-term stress outflows.",
            "NSFR means Net Stable Funding Ratio. It checks whether longer-term assets are funded with stable funding.",
            "LCR focuses more on short-term survival. NSFR focuses more on structural funding stability.",
        ],
        "why_it_matters": [
            "Liquidity risk can move faster than credit risk because depositors and funders can withdraw quickly.",
            "Credit losses can damage confidence, and confidence problems can become liquidity problems.",
            "Recruiters value candidates who understand that capital and liquidity are different but connected.",
        ],
        "project_use": [
            "The Liquidity and Leverage page calculates LCR, NSFR, leverage ratio, and compliance interpretation.",
            "The Executive Overview shows liquidity metrics next to credit and capital metrics to show management-level risk connections.",
        ],
        "simple_example": [
            "A bank has EUR 120m high-quality liquid assets and stressed 30-day net cash outflows of EUR 100m.",
            "LCR = 120m / 100m = 120%.",
            "This suggests the bank has a buffer above 100% in this simplified example.",
        ],
        "memory_hook": "Capital absorbs losses; liquidity pays the bills.",
        "self_checks": [
            ("Can a profitable bank have liquidity problems?", "Yes. Profit does not guarantee immediate cash availability."),
            ("What is the simple purpose of LCR?", "To test whether the bank can survive short-term stressed cash outflows."),
        ],
    },
    {
        "area": "Controls",
        "topic": "Fraud, AML and Financial Crime",
        "beginner_meaning": [
            "Fraud is intentional deception for financial gain, such as stolen cards, false applications, identity theft, or unusual transaction behaviour.",
            "AML means Anti-Money Laundering. It focuses on detecting and preventing criminals from using the financial system to hide illegal money.",
            "Financial crime monitoring often uses rules, thresholds, customer risk profiles, transaction patterns, and investigation workflows.",
            "An alert is a signal that something may need review. An alert is not automatically proof of crime.",
            "A false positive is an alert that looks suspicious but is actually legitimate. A false negative is suspicious activity that the system misses.",
        ],
        "why_it_matters": [
            "Banks must protect customers, comply with law, and avoid being used for criminal activity.",
            "Financial crime teams need to balance detection strength with operational workload.",
            "Thresholds that are too strict can create too many false positives; thresholds that are too loose can miss real risk.",
        ],
        "project_use": [
            "The Fraud and AML page scores transactions, creates alerts, summarizes thresholds, and provides downloadable alert evidence.",
            "The governance parts of the app connect alerts to auditability and control thinking.",
        ],
        "simple_example": [
            "A customer usually spends EUR 50 locally, then suddenly makes several high-value cross-border transactions at night.",
            "The system may create an alert for review. An investigator then decides whether it is legitimate or suspicious.",
        ],
        "memory_hook": "Fraud protects against direct deception; AML protects the financial system from dirty money flows.",
        "self_checks": [
            ("Is every AML alert a confirmed crime?", "No. It is a signal for review."),
            ("What is a false positive?", "A legitimate activity that was incorrectly flagged as suspicious."),
        ],
    },
    {
        "area": "Models and Governance",
        "topic": "Model Risk",
        "beginner_meaning": [
            "A model is a simplified representation of reality used to estimate or support a decision.",
            "In banking, models estimate things like PD, ECL, fraud risk, liquidity stress, valuation adjustments, and capital requirements.",
            "Model risk is the risk that a model is wrong, misused, poorly monitored, or no longer suitable.",
            "A model can fail because data quality is poor, assumptions are outdated, relationships changed, or users interpret outputs incorrectly.",
            "Banks manage model risk through development standards, independent validation, monitoring, documentation, governance, and issue remediation.",
        ],
        "why_it_matters": [
            "A wrong model can create wrong lending decisions, wrong provisions, wrong capital estimates, or wrong management actions.",
            "Recruiters increasingly ask about model validation, drift, monitoring, explainability, and governance.",
        ],
        "project_use": [
            "The Credit Risk Model Development Lab trains baseline and challenger models and shows AUC, calibration, Brier score, feature importance, PSI, and confusion matrix.",
            "The Model Risk page shows model inventory, validation findings, drift, and monitoring concepts.",
        ],
        "simple_example": [
            "A PD model trained during stable economic conditions may perform poorly during a recession.",
            "If unemployment rises and borrower behaviour changes, model drift monitoring should detect that the model population or performance has shifted.",
        ],
        "memory_hook": "A model is useful only if it is accurate enough, monitored, explainable, and used for the right purpose.",
        "self_checks": [
            ("Why is AUC alone not enough for a PD model?", "AUC measures ranking, but PD models also need calibration and stable performance."),
            ("What is model drift?", "A change in data, population, or performance that makes the model less reliable over time."),
        ],
    },
    {
        "area": "Regulation and Resilience",
        "topic": "Key Regulations in This Platform",
        "beginner_meaning": [
            "Basel rules focus on bank capital, risk-weighted assets, leverage, and liquidity standards.",
            "IFRS 9 focuses on accounting for expected credit losses.",
            "COREP and FINREP are regulatory reporting frameworks used in Europe for capital and financial reporting.",
            "BCBS 239 focuses on risk data aggregation and risk reporting principles.",
            "DORA focuses on digital operational resilience, ICT risk, third-party risk, and incident reporting.",
            "The EU AI Act focuses on AI risk classification, governance, transparency, and controls for certain AI use cases.",
            "XVA connects derivative valuation with counterparty credit risk, funding cost, collateral, and margin effects.",
        ],
        "why_it_matters": [
            "Banking risk jobs often require connecting business risk, accounting, regulation, data, models, technology, and governance.",
            "You do not need to memorize every regulation first. You need to understand what problem each framework is trying to solve.",
        ],
        "project_use": [
            "The platform contains pages for IFRS 9, Basel capital, CRR3, COREP/FINREP, BCBS 239, DORA, EU AI Act, climate risk, and XVA.",
            "The End-to-End Case Study in the study guide shows how one shock can flow through PD, ECL, profit, CET1, COREP ratios, actions, and audit trail.",
        ],
        "simple_example": [
            "A borrower portfolio deteriorates. IFRS 9 increases ECL provisions. Basel capital ratios fall. COREP reporting reflects capital impact. BCBS 239 checks data quality. Management actions are recorded for governance.",
        ],
        "memory_hook": "Each framework answers a different question: accounting loss, capital strength, data quality, operational resilience, AI controls, or valuation adjustment.",
        "self_checks": [
            ("What does IFRS 9 mainly deal with?", "Expected credit loss accounting and staging."),
            ("What does DORA mainly deal with?", "Digital operational resilience, ICT risk, third-party risk, and incident handling."),
        ],
    },
    {
        "area": "Beginner Story",
        "topic": "End-to-End Banking Risk Story",
        "beginner_meaning": [
            "A customer takes a mortgage. At first, the borrower pays on time and the loan is performing.",
            "The economy weakens. Unemployment rises, property prices fall, and some borrowers begin missing payments.",
            "The bank updates borrower risk. PD increases because default is more likely. LGD may increase if collateral values fall. EAD remains the amount exposed.",
            "Expected loss increases because PD, LGD, or EAD increased.",
            "Under IFRS 9, some loans may move from Stage 1 to Stage 2 if credit risk increased significantly.",
            "Higher ECL means higher provisions. Higher provisions reduce profit. Lower profit can reduce CET1.",
            "If CET1 ratio falls, management may tighten lending, increase collections, raise capital, reduce dividends, or improve collateral monitoring.",
            "If data quality is weak, governance teams must fix it because wrong data can cause wrong ECL, wrong capital ratios, and wrong regulatory reports.",
        ],
        "why_it_matters": [
            "This is the chain recruiters want you to explain: borrower risk affects accounting, capital, reporting, governance, and management decisions.",
            "It turns separate formulas into one practical banking story.",
        ],
        "project_use": [
            "Use Executive Overview to see the full chain.",
            "Use Credit Risk to understand PD/LGD/EAD.",
            "Use IFRS 9 to understand stage migration and provisions.",
            "Use Basel and COREP pages to understand capital impact.",
            "Use BCBS 239 and audit trail features to understand data and governance controls.",
        ],
        "simple_example": [
            "Macro shock -> PD increase -> Stage 2 migration -> ECL increase -> profit reduction -> CET1 reduction -> COREP ratio impact -> management action -> audit trail.",
        ],
        "memory_hook": "Borrower stress becomes bank stress through ECL, profit, capital, liquidity confidence, and governance.",
        "self_checks": [
            ("Why does a PD increase matter beyond the credit page?", "It can increase ECL, provisions, capital pressure, regulatory reporting impact, and management actions."),
            ("Why is data quality important in this story?", "Bad data can cause wrong risk estimates, wrong provisions, wrong reports, and weak governance evidence."),
        ],
    },
]


def banking_101_summary() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "area": str(topic["area"]),
                "topic": str(topic["topic"]),
                "why_it_matters": " ".join(topic["why_it_matters"]),  # type: ignore[arg-type]
            }
            for topic in BANKING_101_TOPICS
        ]
    )


def _topic_report_sections(topic: dict[str, object]) -> dict[str, str]:
    checks = "\n\n".join(
        f"Question: {question}\nAnswer: {answer}"
        for question, answer in topic["self_checks"]  # type: ignore[index]
    )
    return {
        "Area": str(topic["area"]),
        "Beginner Meaning": "\n".join(f"- {item}" for item in topic["beginner_meaning"]),  # type: ignore[index]
        "Why It Matters": "\n".join(f"- {item}" for item in topic["why_it_matters"]),  # type: ignore[index]
        "How This Project Uses It": "\n".join(f"- {item}" for item in topic["project_use"]),  # type: ignore[index]
        "Simple Example": "\n".join(f"- {item}" for item in topic["simple_example"]),  # type: ignore[index]
        "Memory Hook": str(topic["memory_hook"]),
        "Self-Check Questions": checks,
    }


def render_banking_101() -> None:
    st.subheader("Banking 101")
    st.write(
        "Start here if banking, credit risk, mortgages, provisions, capital, liquidity, or regulation are new to you. "
        "This guide explains the business concepts first, then connects them to the platform."
    )

    summary = banking_101_summary()
    overview_tab, learn_tab, path_tab = st.tabs(["Overview", "Learn Topic", "Beginner Path"])

    with overview_tab:
        st.write("Use this as a beginner map before going into the detailed risk modules.")
        st.dataframe(summary, width="stretch", hide_index=True)
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Beginner Topics", len(BANKING_101_TOPICS))
        with col_b:
            st.metric("Core Formula", "PD x LGD x EAD")
        with col_c:
            st.metric("Main Story", "Risk -> ECL -> Capital")

    topic_names = [str(topic["topic"]) for topic in BANKING_101_TOPICS]
    with learn_tab:
        selected_topic = st.selectbox("Select topic", topic_names)
        topic = next(item for item in BANKING_101_TOPICS if item["topic"] == selected_topic)
        st.markdown(f"### {topic['topic']}")
        st.caption(str(topic["area"]))

        left, right = st.columns([1.2, 0.8])
        with left:
            st.markdown("#### Beginner Meaning")
            for item in topic["beginner_meaning"]:  # type: ignore[index]
                st.write(f"- {item}")
            st.markdown("#### Why We Need It")
            for item in topic["why_it_matters"]:  # type: ignore[index]
                st.write(f"- {item}")
            st.markdown("#### How This Project Uses It")
            for item in topic["project_use"]:  # type: ignore[index]
                st.write(f"- {item}")

        with right:
            with st.container(border=True):
                st.markdown("#### Simple Example")
                for item in topic["simple_example"]:  # type: ignore[index]
                    st.write(f"- {item}")
            with st.container(border=True):
                st.markdown("#### Easy Way to Remember")
                st.info(str(topic["memory_hook"]))

        st.markdown("#### Self-Check Questions")
        for idx, (question, answer) in enumerate(topic["self_checks"], start=1):  # type: ignore[index]
            with st.expander(f"Q{idx}. {question}"):
                st.write(answer)

        st.download_button(
            "Download this topic as PDF",
            data=pdf_report_bytes(f"Banking 101 - {topic['topic']}", _topic_report_sections(topic)),
            file_name=f"banking_101_{str(topic['topic']).lower().replace(' ', '_').replace(',', '').replace('/', '_')}.pdf",
            mime="application/pdf",
        )

    with path_tab:
        st.write("Follow this order if you are starting from zero.")
        path = [
            ("1", "What a Bank Does", "Understand deposits, loans, interest spread, and why banks are regulated."),
            ("2", "Bank Balance Sheet", "Learn assets, liabilities, equity, and why loans and deposits sit on opposite sides."),
            ("3", "Basic Loan Concepts", "Understand principal, interest, tenor, repayment, and outstanding balance."),
            ("4", "Banking Products", "Compare mortgage, personal loan, credit card, SME loan, corporate loan, and deposits."),
            ("5", "What Credit Risk Means", "Learn what default and early warning deterioration mean."),
            ("6", "PD, LGD, EAD and Expected Loss", "Learn the first formula used across the platform."),
            ("7", "Provisioning and IFRS 9", "Connect borrower deterioration to ECL, provisions, and profit impact."),
            ("8", "Capital, RWA and CET1", "Connect losses and RWA to regulatory capital ratios."),
            ("9", "Liquidity, LCR and NSFR", "Understand why cash survival is different from profit and capital."),
            ("10", "End-to-End Banking Risk Story", "Put the full chain together before using the advanced modules."),
        ]
        for step, title, description in path:
            with st.container(border=True):
                st.markdown(f"#### Step {step}: {title}")
                st.write(description)
