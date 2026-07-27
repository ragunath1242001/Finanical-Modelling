# Portfolio Talking Points

## 30-Second Explanation

I built an independent educational banking risk and governance platform in Python and Streamlit using synthetic data. It connects credit risk, IFRS 9 ECL, Basel capital, stress testing, BCBS 239 data governance, model monitoring and audit workflows in one interactive app.

## Two-Minute Explanation

The project starts with synthetic customers, loans, transactions and financial trends. It calculates PD, LGD, EAD, expected loss, lifetime ECL, capital ratios, liquidity ratios and stress impacts. Then it adds the governance layer: data-quality controls, reconciliation, lineage, issue ownership, 1LOD remediation, 2LOD challenge and audit logging. Finally it adds model-risk management: inventory, validation, monitoring, drift, restrictions and revalidation.

## Five-Minute Technical Walkthrough

Show Executive Overview, then Credit Risk, IFRS 9, Basel, BCBS 239 and Model Risk. Explain how the root `app.py` dispatches to modular Streamlit pages, while calculations live in `src/risk`, governance logic in `src/governance`, model-risk logic in `src/model_risk`, and reporting helpers in `src/reporting`.

## Recruiter-Friendly Summary

This project demonstrates practical Python, Streamlit, financial modelling, data governance, model monitoring and documentation skills for banking-risk roles.

## Banking-Risk-Manager Summary

The strongest point is the end-to-end connection from borrower risk to provisions, capital, reporting readiness, controls and management actions.

## Data-Governance Summary

The app shows how missing or invalid data affects risk models, reporting confidence, issue ownership, evidence and auditability.

## Model-Risk Summary

The app shows why model development is not enough: models need inventory, validation, monitoring, limitations, restrictions and revalidation.

## Honest Limitations

The platform is synthetic, simplified and educational. It is not calibrated to a real bank and does not produce valid regulatory or accounting outputs.

## Questions To Ask The Interviewer

- How does your team connect model monitoring with issue management?
- What data-quality controls matter most for IFRS 9 or capital reporting?
- How do 1LOD and 2LOD interact in model-risk remediation?
