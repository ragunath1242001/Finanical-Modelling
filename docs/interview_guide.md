# Interview Guide

## How To Explain Phase 4

I added a BCBS 239-style governance workflow showing that risk models are only reliable when source data is complete, valid, consistent, timely and traceable. The app runs controls on synthetic data, creates issues for failed material controls, assigns owners, routes remediation through 1LOD, challenges closure through 2LOD, and preserves an audit trail.

## Example Answer

If 30% of borrower income is missing, the PD model may still run, but the output is less reliable because an important affordability signal is incomplete. The governance workflow detects the missing data, creates an issue, assigns it to 1LOD for remediation, asks 1LOD to assess model and reporting impact, and requires evidence before 2LOD accepts closure.

## Questions

- Who owns a data-quality issue?
- Can 2LOD fix the issue directly?
- Why can a technically accurate model still be unreliable?
- How does BCBS 239 affect IFRS 9 and capital reporting?
- What evidence is required before closure?
- What is the difference between validation and audit?

## Model-Risk Questions

- What is model risk?
- What is the difference between discrimination and calibration?
- Can a model have strong AUC but poor calibration?
- What causes model drift?
- When should a model be revalidated?
- What is a use restriction?
- Why should developers not validate their own model independently?
- What is the difference between a finding and a limitation?
- Why is the highest-performing challenger not always preferred?
- How does data quality create model risk?

Strong answer pattern: explain the concept, link it to the model lifecycle, then connect it to the app. Example: a challenger model with better AUC is not automatically promoted if calibration, stability, explainability or operational cost is worse.
