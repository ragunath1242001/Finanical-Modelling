# Model Cards

## Credit PD Model

- Purpose: Estimate borrower default risk.
- Inputs: Age, income, credit score, DTI, loan amount, LTV, days past due.
- Output: Probability of default.
- Method: Logistic regression baseline, with transparent fallback logic in the app.
- Limitations: Synthetic data only; not calibrated to a real bank portfolio.
- Monitoring: AUC, calibration, missingness, and prediction drift.
- Owner: Credit Risk.
- Validation status: Validated with limitations for educational use.

## Fraud Classifier

- Purpose: Prioritize suspicious transactions for fraud review.
- Inputs: Amount, device mismatch, transaction velocity, merchant category.
- Output: Fraud probability and alert label.
- Method: Transparent rule-based probability score.
- Limitations: Simplified class imbalance and no production investigation feedback loop.
- Monitoring: Precision, recall, alert volume, false positive rate.
- Owner: Financial Crime.
- Validation status: Independent review pending.

## Forecasting Baseline

- Purpose: Produce 12-month forecasts for planning metrics.
- Inputs: Monthly financial series and macro multiplier.
- Output: Point forecast and simple uncertainty band.
- Method: Recent trend extrapolation.
- Limitations: Not a full econometric or ARIMA implementation.
- Monitoring: MAPE, residual trend, forecast bias.
- Owner: Finance Planning.
- Validation status: Approved for educational demonstration.

## AI Governance Control Assessment

- Purpose: Demonstrate EU AI Act-style governance controls for high-risk financial AI use cases.
- Inputs: Use case, automation flag, credit-access impact flag, implemented control checklist, group approval rates.
- Output: Illustrative AI risk tier, control score, open gaps, fairness gap.
- Method: Weighted checklist and simple group approval-rate comparison.
- Limitations: Educational control assessment only; not a legal compliance opinion.
- Monitoring: Control gaps, audit events, fairness gap, drift and robustness review status.
- Owner: Model Risk / AI Governance.
- Validation status: Governance framework demonstration.

## Climate Credit Risk Overlay

- Purpose: Translate climate transition and physical risk assumptions into credit risk impacts.
- Inputs: Sector, physical risk category, carbon price, collateral value decline, disorderly transition flag.
- Output: PD multiplier, adjusted PD, adjusted LGD, climate ECL increase.
- Method: Transparent scenario multiplier overlay.
- Limitations: Not calibrated to supervisory climate stress test data.
- Monitoring: Sector concentration, physical risk flags, ECL sensitivity, scenario assumptions.
- Owner: Credit Risk / ESG Risk.
- Validation status: Educational overlay.

## XVA Mini Model

- Purpose: Demonstrate how derivative valuation adjustments relate to counterparty credit and funding risk.
- Inputs: Notional, maturity, volatility proxy, collateral coverage, counterparty PD/LGD, own PD, funding spread, initial margin.
- Output: Exposure profile, CVA, DVA, FVA, MVA, total XVA cost.
- Method: Deterministic expected positive exposure profile and discounted adjustment estimates.
- Limitations: No Monte Carlo simulation, wrong-way risk, netting set engine, CSA details, or production pricing calibration.
- Monitoring: Exposure assumptions, PD/LGD assumptions, collateral coverage, funding spread sensitivity.
- Owner: Counterparty Credit Risk / Model Risk.
- Validation status: Educational approximation.

## DORA Resilience Assessment

- Purpose: Classify ICT incidents and assess operational resilience readiness.
- Inputs: Affected users, downtime, data loss, critical-service flag, third-party flag, RTO/RPO, testing, exit plan.
- Output: Incident severity, reporting action, resilience score.
- Method: Transparent scoring checklist.
- Limitations: Not a legal DORA reporting determination.
- Monitoring: Incident score, provider criticality, RTO/RPO breaches, exit-plan gaps.
- Owner: Operational Risk / Technology Risk.
- Validation status: Governance workflow demonstration.
