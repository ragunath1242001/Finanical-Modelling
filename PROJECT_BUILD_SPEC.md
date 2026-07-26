# European Financial Risk, Regulatory, and Governance Platform

Implementation-ready agent document for Codex CLI.

This document can be used as `AGENTS.md` or `PROJECT_BUILD_SPEC.md`. It is written for an AI coding agent that must build an interactive portfolio platform while also teaching the user how each financial model works in real time.

## 1. Project Vision

Build an interactive European Financial Risk, Regulatory, and Governance Platform that simulates how a financial institution connects risk models, regulatory reporting, governance controls, and executive decision-making.

The platform must not be a collection of disconnected notebooks. It should feel like a simplified enterprise risk intelligence system with linked modules:

- Credit risk modeling using PD, LGD, and EAD.
- IFRS 9 expected credit loss and staging.
- Basel III capital adequacy, RWA, leverage ratio, LCR, and NSFR.
- IRB versus standardized capital comparison.
- COREP-style capital reporting.
- FINREP-style financial reporting.
- EBA/ECB-style stress testing and capital planning.
- Fraud detection and AML transaction monitoring.
- Financial forecasting.
- BCBS 239 data quality, lineage, reconciliation, and governance.
- Model risk management, explainability, drift monitoring, and audit logs.
- 1LOD and 2LOD workflows.
- Executive dashboards and interview-ready explanations.

The app must be educational. Every module should expose:

- Inputs.
- Assumptions.
- Formula or model logic.
- Intermediate calculations.
- Final business impact.
- Plain-English explanation.
- Interview-style narrative.

The user should be able to adjust assumptions in real time and observe how risk, provisions, capital, liquidity, regulatory ratios, and governance indicators change.

## 2. Target Roles

The platform is designed to support applications and interviews for:

- Risk Analyst.
- Credit Risk Analyst.
- Risk Data Scientist.
- Regulatory Reporting Analyst.
- IFRS 9 Analyst.
- Basel/Capital Reporting Analyst.
- Model Risk Analyst.
- Data Governance Analyst.
- Financial Crime Analyst.
- Financial Services Consultant.
- Risk and Finance Transformation Consultant.
- AI Governance or Model Governance Analyst in financial services.

## 3. Learning Outcomes

By building and using the platform, the user should be able to explain:

- How a bank balance sheet works.
- Why loans are assets and deposits are liabilities.
- How loan losses reduce profit, retained earnings, CET1, and capital ratios.
- How PD, LGD, and EAD drive expected credit loss.
- How IFRS 9 stages 1, 2, and 3 differ.
- How IFRS 9 provisions affect FINREP and capital.
- How Basel III uses CET1, RWA, leverage, LCR, and NSFR.
- How IRB differs from the standardized approach.
- How COREP and FINREP serve different regulatory reporting purposes.
- How stress scenarios affect credit losses and capital planning.
- How AML and fraud models differ.
- Why BCBS 239 matters for risk data aggregation and reporting.
- How data quality issues can undermine IFRS 9, IRB, COREP, and executive reporting.
- How 1LOD owns and manages risk while 2LOD provides independent oversight and challenge.
- Why model risk management, explainability, monitoring, and auditability are critical in finance.

## 4. Truthfulness and Career Positioning

Strict rule: the user must not present this portfolio project as production work performed at Mu Sigma unless it was actually performed there.

The project may be described truthfully as:

> Leveraging my BFSI data governance experience at Mu Sigma and my research interest in observability and governance, I independently developed a European Financial Risk, Regulatory, and Governance Platform covering credit risk, IFRS 9, Basel III, COREP/FINREP-style reporting, stress testing, AML/fraud analytics, BCBS 239 controls, and model governance.

Do not write README text, resume bullets, or interview narratives that falsely claim:

- The user built production credit risk models at Mu Sigma.
- The user implemented IFRS 9, IRB, COREP, FINREP, or Basel systems at Mu Sigma.
- The user worked as a senior risk specialist if that was not the role.

Acceptable framing:

- "Inspired by BFSI data governance experience."
- "Independent portfolio project."
- "Simulated regulatory reporting and risk analytics platform."
- "Built to deepen practical understanding of financial risk and governance."

## 5. Recommended Technology Stack

Use a stack that is fast to build, easy to explain, and portfolio-friendly.

Preferred stack:

- Python 3.11+.
- Streamlit for interactive dashboard.
- pandas and numpy for data processing.
- scikit-learn for modeling.
- xgboost if available; otherwise use GradientBoostingClassifier/Regressor.
- statsmodels or scikit-learn for forecasting baseline.
- plotly for interactive charts.
- shap for explainability if installable; otherwise use model feature importance and permutation importance.
- great-expectations optional; if too heavy, implement lightweight data quality checks manually.
- evidently optional; if too heavy, implement drift metrics manually.
- SQLite for local persistence and audit logs.
- pytest for tests.
- ruff or black for formatting if configured.

Avoid overengineering. The first complete version should run locally with:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 6. Repository Structure

Create the repository with this structure:

```text
efrg-platform/
  app.py
  requirements.txt
  README.md
  PROJECT_BUILD_SPEC.md
  data/
    raw/
    synthetic/
    processed/
  docs/
    architecture.md
    data_dictionary.md
    model_cards.md
    regulatory_mapping.md
    interview_narratives.md
    truthfulness_guidance.md
  notebooks/
    01_data_generation.ipynb
    02_credit_risk_exploration.ipynb
    03_stress_testing_exploration.ipynb
  src/
    __init__.py
    config.py
    data/
      __init__.py
      generate_synthetic_data.py
      loaders.py
      schemas.py
    risk/
      __init__.py
      credit_pd.py
      lgd_ead.py
      ifrs9.py
      basel.py
      irb.py
      stress_testing.py
      liquidity.py
    financial_crime/
      __init__.py
      fraud.py
      aml.py
    forecasting/
      __init__.py
      forecasting.py
    governance/
      __init__.py
      data_quality.py
      lineage.py
      reconciliation.py
      model_risk.py
      lod_workflows.py
      audit.py
      drift.py
      explainability.py
    reporting/
      __init__.py
      corep.py
      finrep.py
      executive.py
    ui/
      __init__.py
      components.py
      pages/
        01_overview.py
        02_credit_risk.py
        03_ifrs9.py
        04_basel_capital.py
        05_regulatory_reporting.py
        06_stress_testing.py
        07_liquidity.py
        08_financial_crime.py
        09_forecasting.py
        10_governance.py
        11_model_risk.py
        12_interview_mode.py
  tests/
    test_ifrs9.py
    test_basel.py
    test_irb.py
    test_liquidity.py
    test_data_quality.py
    test_reconciliation.py
    test_audit.py
```

If the project is kept small, pages may be implemented inside `app.py`, but keep business logic in `src/`.

## 7. Data Strategy

Use synthetic data by default. The platform should not depend on private or confidential data.

Synthetic datasets:

- Customers.
- Loans.
- Collateral.
- Transactions.
- Bank balance sheet.
- Income statement.
- Regulatory capital data.
- Model prediction logs.
- Data quality issue logs.
- Audit events.

Optional public datasets:

- Credit card fraud public datasets if the user downloads them manually.
- Public macroeconomic sample data from static CSV files if included.

Do not require network access at runtime.

Synthetic data must include realistic imperfections:

- Missing income.
- Missing PD.
- Duplicate customer IDs.
- Invalid loan amounts.
- Stale records.
- Mismatched exposure between risk and finance.
- Suspicious transactions.
- Fraud labels.
- Segment-level macro sensitivity.
- Model prediction history for drift analysis.

## 8. Core App UX

The app should have a left navigation sidebar and these pages:

1. Executive Overview.
2. Credit Risk.
3. IFRS 9 ECL.
4. Basel Capital and IRB.
5. COREP/FINREP Reporting.
6. Stress Testing.
7. Liquidity and Leverage.
8. Fraud and AML.
9. Forecasting.
10. BCBS 239 Governance.
11. Model Risk Management.
12. Interview Mode.

Each page must include:

- "What this module answers" section.
- Interactive controls.
- Output metrics.
- Visualizations.
- Calculation trace.
- Plain-English explanation.
- Interview answer box.

Example teaching pattern:

```text
Input changed:
PD shock increased from 0% to 30%.

Calculation:
ECL = PD x LGD x EAD.

Business impact:
Higher PD increases ECL, which increases IFRS 9 provisions. Higher provisions reduce profit, retained earnings, CET1 capital, and therefore the COREP CET1 ratio.
```

## 9. Module Specifications

### 9.1 Credit Risk Module

Purpose:

- Estimate borrower default risk.
- Teach PD, LGD, EAD, risk segmentation, and expected loss.

Inputs:

- Customer age.
- Income.
- Employment status.
- Credit score.
- Debt-to-income ratio.
- Loan amount.
- Loan-to-value.
- Product type.
- Delinquency history.
- Macro scenario.

Outputs:

- PD.
- LGD.
- EAD.
- Risk grade.
- Expected loss.
- Top risk drivers.

Implementation:

- Train a baseline logistic regression PD model.
- Optional: train tree-based model for comparison.
- LGD can be rule-based using collateral type, LTV, and segment.
- EAD can be current outstanding balance plus credit conversion assumptions.

Teaching requirements:

- Show why a higher loan amount alone does not always mean higher risk.
- Show how PD, LGD, and EAD interact multiplicatively.
- Show customer-level and portfolio-level risk.

Acceptance criteria:

- User can adjust PD/LGD/EAD assumptions.
- App calculates customer ECL and portfolio ECL.
- App ranks customers by expected loss.
- App explains risk grade assignment.

### 9.2 IFRS 9 ECL and Staging Module

Purpose:

- Calculate provisions under IFRS 9.
- Teach Stage 1, Stage 2, Stage 3, SICR, 12-month ECL, and lifetime ECL.

Inputs:

- PD.
- LGD.
- EAD.
- Days past due.
- Credit score change.
- Industry stress flag.
- Macroeconomic scenario.

Stage rules:

- Stage 1: performing, no significant increase in credit risk.
- Stage 2: significant increase in credit risk but not defaulted.
- Stage 3: defaulted or credit-impaired.

Use simplified rules:

- Stage 3 if days past due >= 90 or default flag true.
- Stage 2 if days past due >= 30, credit score deterioration exceeds threshold, or industry stress is severe.
- Otherwise Stage 1.

Outputs:

- Stage.
- 12-month ECL.
- Lifetime ECL.
- Provision amount.
- Profit impact.
- Retained earnings impact.
- CET1 impact.

Acceptance criteria:

- User can see why a loan moved from Stage 1 to Stage 2.
- App explains that Stage 2 is based on SICR, not only missed payments.
- App shows the chain from provision increase to CET1 reduction.

### 9.3 Basel III Capital and RWA Module

Purpose:

- Teach capital adequacy and risk-weighted assets.

Inputs:

- Asset class.
- Exposure amount.
- Risk weight.
- CET1.
- AT1.
- Tier 2.
- Provision shock.

Outputs:

- RWA.
- CET1 ratio.
- Tier 1 ratio.
- Total capital ratio.
- Capital buffer impact.

Simplified formulas:

```text
RWA = exposure x risk_weight
CET1 Ratio = CET1 / RWA
Tier 1 Ratio = (CET1 + AT1) / RWA
Total Capital Ratio = (CET1 + AT1 + Tier 2) / RWA
```

Acceptance criteria:

- App shows total assets versus RWA.
- App demonstrates why risk composition matters.
- App shows how IFRS 9 provisions can reduce CET1.

### 9.4 IRB Comparison Module

Purpose:

- Compare standardized approach versus IRB.
- Teach how PD/LGD/EAD serve both IFRS 9 and Basel capital purposes.

Inputs:

- Exposure.
- Standardized risk weight.
- PD.
- LGD.
- EAD.
- Maturity adjustment placeholder.

Outputs:

- Standardized RWA.
- Simplified IRB capital estimate.
- Simplified IRB RWA equivalent.
- Difference between approaches.

Important caveat:

- Do not claim to implement the full regulatory IRB formula unless it is fully implemented and documented. Use a simplified educational approximation unless implementing a validated formula.

Teaching requirements:

- IFRS 9 asks: "What losses do we expect?"
- IRB asks: "How much capital should we hold?"
- Same risk parameters may feed different regulatory objectives.

Acceptance criteria:

- User can compare standardized and internal-model views.
- App clearly labels simplified calculations as educational approximations.

### 9.5 COREP and FINREP-Style Reporting Module

Purpose:

- Show difference between financial reporting and capital reporting.

FINREP-style metrics:

- Assets.
- Liabilities.
- Equity.
- Net interest income.
- Provisions.
- Profit.

COREP-style metrics:

- CET1.
- AT1.
- Tier 2.
- RWA.
- CET1 ratio.
- Leverage ratio.
- Capital adequacy status.

Acceptance criteria:

- App shows how provisions affect FINREP profit.
- App shows how retained earnings affect COREP CET1.
- App includes a reconciliation note between finance and risk numbers.

### 9.6 EBA/ECB-Style Stress Testing Module

Purpose:

- Simulate baseline, adverse, and severe scenarios.

Inputs:

- GDP shock.
- Unemployment shock.
- Interest rate shock.
- Housing price shock.
- PD multiplier.
- LGD multiplier.
- Revenue shock.

Outputs:

- Stressed PD.
- Stressed LGD.
- Stressed ECL.
- Provision increase.
- Profit impact.
- CET1 impact.
- CET1 ratio after stress.
- Management action suggestions.

Management actions:

- Reduce dividends.
- Reduce risky asset growth.
- Raise capital.
- Tighten lending criteria.
- Improve collections.

Acceptance criteria:

- User can compare baseline, adverse, and severe scenarios.
- App shows a waterfall from ECL increase to capital ratio decrease.
- App explains capital planning implications.

### 9.7 Liquidity Ratios and Leverage Module

Purpose:

- Teach that a bank can be capitalized but still fail due to liquidity or funding stress.

Metrics:

```text
Leverage Ratio = Tier 1 Capital / Total Exposure
LCR = High Quality Liquid Assets / Net Cash Outflows over 30 Days
NSFR = Available Stable Funding / Required Stable Funding
```

Inputs:

- Tier 1 capital.
- Total exposure.
- HQLA.
- 30-day net cash outflows.
- ASF.
- RSF.

Outputs:

- Leverage ratio.
- LCR.
- NSFR.
- Compliance status.

Acceptance criteria:

- App explains the difference between solvency and liquidity.
- App demonstrates why NSFR below 100% is a concern.
- App explains LCR as 30-day survival and NSFR as long-term funding stability.

### 9.8 Fraud Detection Module

Purpose:

- Detect potentially fraudulent transactions.

Inputs:

- Transaction amount.
- Merchant category.
- Time of day.
- Country.
- Customer history.
- Device mismatch.
- Velocity features.

Outputs:

- Fraud probability.
- Risk label.
- Alert queue.
- Precision/recall style summary.

Implementation:

- Use synthetic labeled transactions.
- Train baseline classifier.
- Use threshold slider to show false positive/false negative tradeoff.

Acceptance criteria:

- User can adjust threshold and see alert volume change.
- App explains class imbalance.
- App distinguishes fraud from AML.

### 9.9 AML Transaction Monitoring Module

Purpose:

- Monitor suspicious transaction behavior using rules and risk scoring.

Inputs:

- Customer risk category.
- Transaction amount.
- Counterparty country risk.
- Frequency.
- Round amount flag.
- Rapid movement of funds.

Outputs:

- AML risk score.
- Alert reason.
- Investigation priority.

Rules:

- Large unusual transfer.
- High-risk jurisdiction.
- Structuring pattern.
- Rapid in-out movement.
- Multiple transactions below threshold.

Acceptance criteria:

- App explains why AML systems create false positives.
- App shows alert prioritization.
- App includes KYC/customer risk factors.

### 9.10 Financial Forecasting Module

Purpose:

- Forecast financial metrics relevant to planning.

Forecast targets:

- Loan balances.
- Deposit balances.
- Net interest income.
- Provisions.
- Fraud/AML alert volume.

Implementation:

- Use synthetic monthly time series.
- Use baseline moving average and regression/ARIMA-like method.
- Show forecast uncertainty bands if feasible.

Acceptance criteria:

- App produces 12-month forecast.
- User can apply macro scenario assumptions.
- App explains how forecasts feed stress testing and capital planning.

### 9.11 BCBS 239 Data Quality, Lineage, and Reconciliation Module

Purpose:

- Show how risk data governance supports reliable reporting.

Data quality dimensions:

- Accuracy.
- Completeness.
- Consistency.
- Timeliness.
- Traceability.

Controls:

- Missing customer ID.
- Missing PD.
- Invalid loan amount.
- Duplicate account.
- Stale data feed.
- Exposure mismatch between risk and finance.

Reconciliation:

```text
Risk Exposure
Finance Exposure
Difference
Adjustment reason
Owner
Status
```

Lineage:

Show simplified flow:

```text
Loan Origination System
  -> Risk Data Mart
  -> PD Model
  -> IFRS 9 Engine
  -> COREP/FINREP Dashboards
  -> Executive Report
```

Acceptance criteria:

- App calculates data quality score.
- App flags failed controls.
- App shows lineage for ECL and capital ratio.
- App includes reconciliation table and adjustment reasons.

### 9.12 Model Risk Management Module

Purpose:

- Teach model lifecycle, validation, monitoring, and governance.

Model lifecycle:

```text
Development -> Validation -> Approval -> Deployment -> Monitoring -> Retirement
```

Track:

- Model owner.
- Model version.
- Training date.
- Validation status.
- Approval status.
- Performance metrics.
- Known limitations.
- Open findings.

Acceptance criteria:

- App shows model inventory.
- App has model cards.
- App separates development metrics from monitoring metrics.
- App shows validation findings and remediation status.

### 9.13 1LOD and 2LOD Workflow Module

Purpose:

- Explain operational ownership and independent oversight.

Definitions:

1LOD:

> Business and operational teams that own, manage, and are accountable for risks arising from their activities.

2LOD:

> Independent risk, compliance, and governance functions that provide oversight, challenge, monitoring, and guidance.

Workflow example:

```text
Data quality issue detected
  -> 1LOD data steward investigates
  -> 1LOD model owner assesses impact
  -> 1LOD proposes remediation
  -> 2LOD challenges root cause and remediation
  -> 2LOD tracks closure
  -> Audit log records decision
```

Acceptance criteria:

- App shows issue queues for 1LOD and 2LOD.
- User can mark issue status changes.
- Audit log records status changes.
- App explains ownership versus oversight.

### 9.14 Explainability Module

Purpose:

- Explain model decisions to users, managers, and validators.

Include:

- Feature importance.
- Customer-level reason codes.
- SHAP if available.
- Fallback: top contributing features from simpler model.

Acceptance criteria:

- Every high-risk prediction has a reason.
- App can explain why a customer has high PD or fraud risk.
- Explanation is understandable to non-technical stakeholders.

### 9.15 Drift Monitoring Module

Purpose:

- Show model monitoring after deployment.

Track:

- Data drift.
- Prediction drift.
- Performance drift.
- Missingness drift.

Simple drift metrics:

- Population Stability Index for numeric bands if implemented.
- Distribution comparison.
- Change in mean/median.
- Change in missing rate.

Acceptance criteria:

- App compares baseline data versus current data.
- App flags drift thresholds.
- App explains why drift matters for IFRS 9, IRB, and model risk.

### 9.16 Audit Logs

Purpose:

- Show traceability and governance.

Record:

- Timestamp.
- User/action actor.
- Module.
- Action.
- Old value.
- New value.
- Reason.

Example events:

- PD shock changed.
- Scenario changed.
- Data quality issue opened.
- 1LOD remediation submitted.
- 2LOD challenge recorded.
- Model status changed to approved.

Acceptance criteria:

- Audit log persists in SQLite or CSV.
- User can view recent audit events in app.
- Major scenario/model/governance actions are logged.

### 9.17 Executive Dashboard

Purpose:

- Give senior management a single view of risk, capital, financial crime, and governance.

Metrics:

- Portfolio ECL.
- High-risk customers.
- Stressed CET1 ratio.
- RWA.
- LCR.
- NSFR.
- Leverage ratio.
- Fraud alerts.
- AML alerts.
- Data quality score.
- Model health score.
- Open 1LOD/2LOD issues.

Acceptance criteria:

- Dashboard updates when assumptions change.
- Includes management interpretation.
- Includes "what should management do?" section.

## 10. Four-Week Build Plan

### Week 1: Foundation, Data, Credit Risk, IFRS 9

Goals:

- Set up repository.
- Generate synthetic data.
- Build credit risk module.
- Build IFRS 9 staging and ECL module.

Deliverables:

- Running Streamlit app.
- Synthetic customer and loan data.
- PD baseline model.
- LGD/EAD calculations.
- IFRS 9 staging rules.
- ECL dashboard.
- First tests for ECL.

Acceptance criteria:

- User can calculate ECL interactively.
- User can see Stage 1/2/3 logic.
- README explains PD, LGD, EAD, and IFRS 9.

### Week 2: Basel III, IRB, COREP/FINREP, Liquidity

Goals:

- Build Basel capital module.
- Build IRB comparison module.
- Build COREP/FINREP-style dashboards.
- Add leverage ratio, LCR, and NSFR.

Deliverables:

- Capital dashboard.
- RWA calculator.
- Standardized versus IRB comparison.
- FINREP profit/provision/equity view.
- COREP capital ratio view.
- Liquidity and leverage dashboard.

Acceptance criteria:

- App explains total assets versus RWA.
- App shows IFRS 9 provision impact on CET1.
- App demonstrates NSFR and LCR separately.

### Week 3: Stress Testing, Forecasting, Fraud, AML

Goals:

- Build EBA/ECB-style stress scenario engine.
- Build financial forecasting module.
- Build fraud detection module.
- Build AML monitoring module.

Deliverables:

- Baseline/adverse/severe stress dashboard.
- Capital impact waterfall.
- 12-month forecast view.
- Fraud alert queue.
- AML alert queue.

Acceptance criteria:

- User can change macro shocks and see capital impact.
- App explains PD/LGD/EAD stress behavior.
- Fraud and AML are clearly differentiated.

### Week 4: BCBS 239, Model Risk, 1LOD/2LOD, Explainability, Drift, Polish

Goals:

- Build governance dashboard.
- Build data quality controls.
- Build lineage and reconciliation views.
- Build model risk management module.
- Add explainability, drift, audit logs.
- Add interview mode and documentation.

Deliverables:

- BCBS 239 dashboard.
- Data quality score.
- Reconciliation table.
- Lineage visualization.
- Model inventory and model cards.
- 1LOD/2LOD issue workflow.
- Audit log.
- Interview narratives.
- Final README and docs.

Acceptance criteria:

- User can explain end-to-end chain from PD increase to COREP ratio decrease.
- App demonstrates governance issues and remediation workflow.
- Documentation is portfolio-ready and truthful.

## 11. Codex CLI System Prompt

Use this prompt to start the Codex CLI build:

```text
You are a senior AI coding agent building an educational portfolio application called the European Financial Risk, Regulatory, and Governance Platform.

Your goal is to build a runnable Streamlit application that teaches and demonstrates credit risk, IFRS 9 ECL, Basel III capital, IRB comparison, COREP/FINREP-style reporting, stress testing, liquidity ratios, fraud detection, AML monitoring, financial forecasting, BCBS 239 governance, model risk management, explainability, drift monitoring, audit logs, and 1LOD/2LOD workflows.

Prioritize a complete, understandable, interactive system over regulatory perfection. Clearly label simplified educational approximations. Keep business logic in src modules and UI in Streamlit pages. Use synthetic data by default. Do not require private data or network access at runtime.

Every module must teach the user by showing inputs, assumptions, calculations, outputs, plain-English interpretation, and interview-ready narrative. Include tests for core formulas and data quality checks.

Strict truthfulness requirement: do not write any README, resume bullet, or narrative that claims this was production work at Mu Sigma. Frame it as an independent portfolio project inspired by BFSI data governance experience.

Before editing, inspect the repository. Then implement incrementally, run tests, and keep documentation updated.
```

## 12. Per-Phase Agent Prompts

### Phase 1 Prompt

```text
Build the foundation of the platform. Create the repository structure, synthetic data generator, Streamlit shell, credit risk module, and IFRS 9 module. Implement PD baseline modeling, LGD/EAD calculations, Stage 1/2/3 rules, ECL calculation, and an interactive page that explains every calculation. Add tests for ECL and staging.
```

### Phase 2 Prompt

```text
Add Basel III, IRB, COREP/FINREP, leverage, LCR, and NSFR modules. Show RWA, CET1 ratio, Tier 1 ratio, total capital ratio, leverage ratio, liquidity coverage ratio, and net stable funding ratio. Add simplified standardized versus IRB comparison with clear educational caveats. Connect IFRS 9 provisions to profit, retained earnings, CET1, and COREP-style capital ratios.
```

### Phase 3 Prompt

```text
Add EBA/ECB-style stress testing, financial forecasting, fraud detection, and AML transaction monitoring. Include baseline, adverse, and severe scenarios. Show how macro shocks affect PD, LGD, ECL, profit, CET1, and capital ratios. Build fraud and AML alert queues with threshold controls and plain-English explanations.
```

### Phase 4 Prompt

```text
Add BCBS 239 governance, data quality controls, lineage, reconciliation, model risk management, 1LOD/2LOD workflows, explainability, drift monitoring, audit logs, and interview mode. Ensure all dashboards update consistently. Add model cards, regulatory mapping, interview narratives, and truthfulness guidance. Run tests and finalize README.
```

## 13. Commands

Expected commands:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.data.generate_synthetic_data
pytest
streamlit run app.py
```

Windows PowerShell equivalents:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.data.generate_synthetic_data
pytest
streamlit run app.py
```

If using optional packages like xgboost, shap, great-expectations, or evidently causes installation problems, provide graceful fallbacks and document them.

## 14. Testing Requirements

Core tests:

- ECL equals PD x LGD x EAD.
- Stage 3 triggered by default or 90+ days past due.
- Stage 2 triggered by SICR indicators.
- RWA equals exposure x risk weight.
- CET1 ratio equals CET1 / RWA.
- Leverage ratio equals Tier 1 / total exposure.
- LCR equals HQLA / 30-day net cash outflows.
- NSFR equals ASF / RSF.
- Data quality completeness score detects missing PD.
- Reconciliation detects finance versus risk exposure mismatch.
- Audit log records key actions.

Example test names:

```text
test_ecl_formula_basic
test_ifrs9_stage_three_default
test_ifrs9_stage_two_sicr
test_basel_rwa_standardized
test_cet1_ratio_after_provision
test_lcr_calculation
test_nsfr_calculation
test_missing_pd_quality_rule
test_reconciliation_difference
test_audit_log_event_written
```

## 15. README Requirements

The README must include:

- Project overview.
- Why this project exists.
- Target roles.
- Architecture diagram.
- Module list.
- How to install.
- How to run.
- How to run tests.
- Data strategy.
- Regulatory caveats.
- Truthfulness statement.
- Screenshots or placeholders.
- Interview narratives.
- Roadmap.

Required truthfulness statement:

```text
This is an independent educational portfolio project. It is inspired by BFSI data governance experience and financial risk learning, but it must not be represented as production work performed for any employer unless that is factually true.
```

## 16. Documentation Requirements

Create these docs:

### docs/architecture.md

Explain:

- Data flow.
- Module dependencies.
- How risk outputs feed reporting.
- How governance wraps around the platform.

### docs/data_dictionary.md

Define:

- Customer fields.
- Loan fields.
- Transaction fields.
- Risk fields.
- Reporting fields.

### docs/model_cards.md

For each model:

- Purpose.
- Inputs.
- Output.
- Method.
- Limitations.
- Monitoring metrics.
- Owner.
- Validation status.

### docs/regulatory_mapping.md

Map modules to concepts:

```text
IFRS 9 -> ECL, staging, provisions
Basel III -> CET1, RWA, leverage, LCR, NSFR
IRB -> PD/LGD/EAD for regulatory capital
COREP -> capital reporting
FINREP -> financial reporting
BCBS 239 -> risk data aggregation and reporting
EBA/ECB stress testing -> scenario analysis and capital planning
AMLD/KYC -> financial crime monitoring
EU AI governance concepts -> explainability, auditability, monitoring
```

### docs/interview_narratives.md

Include concise answers for:

- "Tell me about this project."
- "How does IFRS 9 connect to Basel III?"
- "How do PD, LGD, and EAD feed both IFRS 9 and IRB?"
- "Why is BCBS 239 important?"
- "What is the role of 1LOD and 2LOD?"
- "How does model risk management apply here?"
- "How is this related to your BFSI data governance background?"

### docs/truthfulness_guidance.md

Include:

- What the user can say.
- What the user must not say.
- Resume-safe phrasing.
- Interview-safe phrasing.

## 17. Sample Interview Narratives

### Project Summary

> I built an independent European Financial Risk, Regulatory, and Governance Platform to understand how risk analytics, regulatory reporting, data governance, and model governance connect in financial institutions. The platform simulates credit risk, IFRS 9 expected credit loss, Basel III capital adequacy, COREP/FINREP-style reporting, EBA-style stress testing, AML/fraud monitoring, BCBS 239 data quality controls, and model risk management.

### IFRS 9 to COREP Flow

> When credit risk deteriorates, PD increases. Higher PD increases expected credit loss under IFRS 9. This increases provisions, which reduces profit and retained earnings. Since retained earnings are part of CET1 capital, CET1 can decrease. That reduction then affects capital ratios reported through COREP.

### BCBS 239 Narrative

> BCBS 239 is important because risk calculations are only reliable if the underlying data is accurate, complete, timely, consistent, and traceable. A sophisticated PD model is not enough if key fields such as income, exposure, or default history are missing or inconsistent across systems.

### 1LOD/2LOD Narrative

> The First Line of Defense owns and manages risk in day-to-day operations, including data stewardship, model operation, and issue remediation. The Second Line of Defense provides independent oversight and challenge through risk management, compliance, model validation, and data governance functions.

### Truthful Mu Sigma Connection

> My BFSI data governance experience helped me understand why data quality, lineage, and reconciliation matter in financial services. I built this independent project to extend that foundation into credit risk, IFRS 9, Basel III, stress testing, and model governance.

## 18. Final Acceptance Criteria

The project is complete when:

- `streamlit run app.py` launches successfully.
- Synthetic data is generated locally.
- All major modules are accessible from the UI.
- Credit risk, IFRS 9, Basel, IRB, COREP/FINREP, stress testing, liquidity, fraud, AML, forecasting, BCBS 239, model risk, 1LOD/2LOD, explainability, drift, and audit logs are represented.
- The app includes teaching explanations for each module.
- Core tests pass.
- README is complete.
- Documentation is complete.
- The project is truthfully described as an independent portfolio project.

## 19. Build Philosophy

Build in this order:

1. Correct formulas.
2. Clear explanations.
3. Working interactivity.
4. Tests.
5. Documentation.
6. Visual polish.

Do not chase regulatory perfection at the cost of clarity. The goal is a credible, transparent, educational portfolio platform that helps the user learn and explain how financial risk, regulatory reporting, and governance connect.

