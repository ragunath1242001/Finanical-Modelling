# European Financial Risk, Regulatory, and Governance Platform

This project is a Streamlit-based financial risk platform built with synthetic data. It brings together several areas that are usually discussed separately: credit risk, IFRS 9 expected credit loss, Basel capital, regulatory reporting, liquidity, stress testing, financial crime monitoring, data governance, model governance, operational resilience, climate risk, AI governance, and counterparty risk.

The idea behind the project is simple: if one assumption changes, the effect should be visible across the whole risk and reporting chain. For example, if probability of default increases, expected credit loss increases. Higher expected loss increases provisions. Higher provisions reduce profit and retained earnings. Since retained earnings are part of CET1 capital, capital ratios can also fall.

The project is not intended to be a production banking system. It is a learning and simulation tool that uses simplified formulas so the calculations are transparent.

## What Is Included

The app currently contains these sections:

- Executive Overview
- Credit Risk
- IFRS 9 ECL
- Basel Capital and IRB
- CRR3 Basel Final Reforms
- COREP/FINREP Reporting
- Stress Testing
- Geopolitical Reverse Stress
- Liquidity and Leverage
- Fraud and AML
- Forecasting
- BCBS 239 Governance
- Model Risk Management
- EU AI Act Governance
- DORA Operational Resilience
- ESG Climate Credit Risk
- XVA Counterparty Risk
- Documentation & Study Guide

Most pages follow the same structure: input assumptions, calculated outputs, charts or tables, a calculation trace, and a plain-English explanation.

The `Documentation & Study Guide` page is built into the app as a revision section. It organizes the main topics in a tree structure and includes definitions, how the project uses each concept, formulas, memory hooks, self-test questions with answers, small interactive calculators for selected topics, and a quiz mode with immediate explanations.

The `Credit Risk` and `IFRS 9 ECL` pages include mode selectors for deeper analysis. Credit Risk contains both the portfolio risk view and the model development lab. IFRS 9 contains both the ECL calculator and the scenario ECL engine.

The `End-to-End Risk Case Study` page connects several modules into guided scenarios such as unemployment shock, IFRS 9 data quality issue, model drift, and DORA incident. It shows how a trigger flows through PD/LGD, ECL, profit, CET1, COREP-style ratio impact, and governance actions.

Several pages also include download buttons for reports such as capital summary, model validation summary, IFRS 9 scenario ECL, ECL bridge, BCBS 239 issue log, DORA incident report, and end-to-end case study report.

## Main Concepts

### Credit Risk

Credit risk is the risk that a borrower does not repay as agreed. In this project it is represented using three core parameters:

- `PD`: Probability of Default. The likelihood that a borrower defaults.
- `LGD`: Loss Given Default. The percentage of exposure that may be lost if default happens.
- `EAD`: Exposure at Default. The amount expected to be outstanding at the time of default.

Expected loss is calculated as:

```text
Expected Loss = PD x LGD x EAD
```

The credit risk page lets the user change PD, LGD, and EAD assumptions and see how customer-level and portfolio-level expected loss changes.

### Credit Risk Model Development Lab

The credit model lab is a deeper modelling workflow. It trains a logistic regression baseline and a gradient boosting challenger model on synthetic borrower and loan data.

The lab includes:

- Train/test split
- AUC
- Average precision
- Brier score
- Precision and recall at a selected threshold
- ROC curve
- Calibration table
- Confusion matrix
- Feature importance
- Risk grades
- PSI-based monitoring check

This is the deepest modelling section of the project. It is meant to show how a PD model can be developed, evaluated, explained, graded, and monitored.

### IFRS 9 Expected Credit Loss

IFRS 9 requires banks to estimate expected credit losses before losses actually occur. The project uses a simplified staging approach:

- `Stage 1`: Performing exposure with no significant increase in credit risk.
- `Stage 2`: Significant increase in credit risk, but not defaulted.
- `Stage 3`: Defaulted or credit-impaired exposure.

The simplified staging rules are:

- Stage 3 if the loan is defaulted or 90+ days past due.
- Stage 2 if the loan is 30+ days past due, has material credit score deterioration, or belongs to a severely stressed sector.
- Stage 1 otherwise.

Stage 1 uses 12-month ECL. Stage 2 and Stage 3 use lifetime ECL in this educational version.

### IFRS 9 Scenario ECL Engine

The IFRS 9 scenario engine adds a more realistic forward-looking provision workflow. It calculates ECL under upside, baseline, and downside scenarios and then combines them using scenario weights.

The engine includes:

- Loan-level stage assignment
- 12-month PD for Stage 1
- Lifetime PD approximation for Stage 2 and Stage 3
- Scenario PD and LGD multipliers
- Scenario-weighted ECL
- Stage migration table
- Provision movement bridge

The simplified weighted ECL formula is:

```text
Weighted ECL =
  Upside ECL x Upside Weight
  + Baseline ECL x Baseline Weight
  + Downside ECL x Downside Weight
```

### Basel Capital

Basel capital rules focus on whether a bank has enough capital for its risk profile. The main capital measure used here is `CET1`, or Common Equity Tier 1 capital.

The simplified formulas used in the app are:

```text
RWA = Exposure x Risk Weight
CET1 Ratio = CET1 / RWA
Tier 1 Ratio = (CET1 + AT1) / RWA
Total Capital Ratio = (CET1 + AT1 + Tier 2) / RWA
```

`RWA` means risk-weighted assets. A low-risk asset receives a lower risk weight, while a riskier asset receives a higher risk weight.

### IRB

IRB means Internal Ratings-Based approach. It allows banks, subject to regulatory approval, to use internal risk parameters such as PD, LGD, and EAD for regulatory capital calculations.

This project does not implement the full regulatory IRB formula. It uses a simplified approximation to show the difference between standardized and internal-model views.

### CRR3 and Basel Final Reforms

The CRR3 page shows simplified versions of concepts from the final Basel III reforms:

- `Output floor`: A lower bound on internal-model RWA based on standardized RWA.
- `Operational risk SMA`: A simplified standardized measurement approach for operational risk.
- `CVA-lite`: A simplified counterparty credit valuation adjustment capital component.

These calculations are meant to show why internal models may still be constrained by standardized capital floors.

### COREP and FINREP

COREP and FINREP are regulatory reporting concepts used in Europe.

- `COREP`: Capital reporting. It focuses on capital resources, RWA, leverage, and capital adequacy.
- `FINREP`: Financial reporting. It focuses on assets, liabilities, equity, income, provisions, and profit.

The app shows how IFRS 9 provisions can reduce profit and retained earnings, which can then affect CET1 capital in COREP-style reporting.

### Stress Testing

Stress testing applies adverse assumptions to understand how a portfolio or bank might behave under difficult conditions. The app includes baseline, adverse, and severe scenarios.

The stress testing page adjusts PD, LGD, revenue, provisions, and CET1 ratio to show how capital planning can be affected.

### Reverse Stress Testing

Normal stress testing asks:

```text
What happens if this scenario occurs?
```

Reverse stress testing asks:

```text
What scenario would be severe enough to cause a specific failure outcome?
```

The reverse stress page starts with a target CET1 depletion, such as 300 basis points, and then shows how credit losses, market losses, operational losses, and funding shocks can combine to reach that outcome.

### Liquidity and Leverage

Capital and liquidity are different problems. A bank can appear well capitalized but still face liquidity stress.

The app includes:

```text
Leverage Ratio = Tier 1 Capital / Total Exposure
LCR = High Quality Liquid Assets / 30-day Net Cash Outflows
NSFR = Available Stable Funding / Required Stable Funding
```

`LCR` focuses on short-term liquidity survival. `NSFR` focuses on longer-term funding stability.

### Fraud and AML

Fraud detection and AML monitoring are related but not the same.

- Fraud detection looks for unauthorized or abusive transactions.
- AML monitoring looks for suspicious behavior that may indicate money laundering, sanctions risk, structuring, or unusual fund movement.

The project uses synthetic transaction data and simple scoring rules to create alert queues.

### Forecasting

The forecasting page creates simple 12-month forecasts for loan balances, deposit balances, net interest income, provisions, and alert volumes.

The method is intentionally simple: recent trend extrapolation with a macro multiplier and uncertainty bands.

### BCBS 239 Governance

BCBS 239 is about risk data aggregation and risk reporting. The project includes checks for:

- Completeness
- Accuracy
- Consistency
- Timeliness
- Traceability

The governance page flags missing PD values, invalid loan amounts, duplicate customer IDs, stale records, and exposure mismatches between risk and finance views.

### Model Risk Management

Model risk management covers the full model lifecycle:

```text
Development -> Validation -> Approval -> Deployment -> Monitoring -> Retirement
```

The app includes a model inventory, validation findings, drift checks, reason codes, and issue queues.

### EU AI Act Governance

The EU AI Act governance page is a simplified control room for high-risk AI-style use cases such as credit scoring, fraud detection, and AML monitoring.

The page checks whether controls exist for:

- Risk management
- Data governance
- Technical documentation
- Logging and traceability
- Transparency and explainability
- Human oversight
- Accuracy and robustness
- Post-deployment monitoring

It also includes a simple fairness-gap calculation based on group approval rates.

### DORA Operational Resilience

DORA focuses on digital operational resilience in financial services. The DORA page includes:

- ICT incident classification
- Critical service impact
- Third-party provider involvement
- Recovery time objective (`RTO`)
- Recovery point objective (`RPO`)
- Resilience testing
- Exit planning for critical providers

The page produces a resilience score and a suggested reporting action.

### ESG Climate Credit Risk

The climate page translates transition and physical climate risk into credit risk effects.

- Transition risk can increase PD for sectors exposed to policy, carbon pricing, or business model changes.
- Physical risk can affect collateral values and therefore LGD.

The page calculates climate-adjusted PD, LGD, and ECL.

### XVA Counterparty Risk

XVA refers to valuation adjustments used in derivatives and counterparty risk.

The project includes simplified versions of:

- `CVA`: Credit Valuation Adjustment, based on counterparty credit risk.
- `DVA`: Debit Valuation Adjustment, based on own credit risk.
- `FVA`: Funding Valuation Adjustment, based on funding spread.
- `MVA`: Margin Valuation Adjustment, based on initial margin funding cost.

This is not a derivatives pricing engine. It is a simplified explanation of the main drivers: exposure, collateral, counterparty PD, LGD, funding spread, margin, and maturity.

## Data

The project uses synthetic data only. The generated datasets include:

- Customers
- Loans
- Transactions
- Financial time series

The synthetic data intentionally includes imperfections:

- Missing income
- Missing PD
- Duplicate customer IDs
- Invalid loan amounts
- Stale records
- Risk and finance exposure mismatch
- Suspicious transaction patterns
- Fraud labels

This makes the governance and reconciliation pages more realistic.

## Project Structure

```text
app.py
requirements.txt
PROJECT_BUILD_SPEC.md
data/
  synthetic/
docs/
notebooks/
src/
  data/
  risk/
  financial_crime/
  forecasting/
  governance/
  reporting/
  ui/
tests/
```

Business logic is kept under `src/`. The Streamlit application is in `app.py`. Tests are under `tests/`.

## Installation

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Generate Synthetic Data

```powershell
python -m src.data.generate_synthetic_data
```

The app also generates data automatically if the synthetic CSV files are missing.

## Run the App

```powershell
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Run Tests

```powershell
pytest
```

The tests cover the main formulas and checks, including IFRS 9 ECL, staging, Basel ratios, liquidity ratios, reconciliation, audit logging, CRR3, reverse stress testing, AI governance, DORA, climate risk, and XVA.

## Limitations

This project is educational and uses simplified formulas. It should not be treated as:

- A production credit risk model
- A regulatory capital engine
- A full IFRS 9 impairment engine
- A COREP or FINREP reporting solution
- A derivatives pricing or XVA engine
- A legal interpretation of EU AI Act, DORA, CRR3, Basel, or ESG requirements

The purpose is to make the relationships between risk, finance, regulation, governance, and reporting easier to understand.

## Independent Project Statement

This is an independent educational project using synthetic data. It should not be represented as production work performed for any employer unless that is factually true.

## Possible Improvements

- Add downloadable COREP and FINREP-style report templates.
- Add better model performance charts for the PD and fraud models.
- Add calibration and backtesting views.
- Add Monte Carlo exposure simulation for XVA.
- Add richer climate scenario assumptions by sector and geography.
- Add downloadable DORA incident and third-party oversight reports.
- Add persistent scenario storage for comparing multiple stress runs.
- Add more topic-specific exercises to the in-app documentation page.
- Add PDF formatting for downloadable reports.
