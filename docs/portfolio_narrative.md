# Portfolio Narrative

The synthetic portfolio is designed to feel like a compact European retail and SME banking book. It is not random demo data only for charts. The datasets are connected so that a user can follow the chain from customer profile to loan risk, transaction monitoring, financial reporting, governance checks, and management actions.

## Business Context

The bank serves individual borrowers, card customers, mortgage customers, and small business borrowers. Each customer has demographic and risk information such as income, employment status, credit score, debt-to-income ratio, country, and KYC-style customer risk category.

Loan records represent the credit portfolio. They include product type, loan amount, outstanding balance, loan-to-value, days past due, default flag, PD, LGD, and EAD. These fields support expected loss, IFRS 9 staging, capital, stress testing, climate sensitivity, and model development workflows.

Transaction records represent payment activity. They include transaction amount, merchant category, country risk, device mismatch, velocity, round amount indicators, rapid in/out indicators, and fraud labels. These fields support fraud and AML alert scoring.

Financial time series represent the management and reporting layer. They include loan balances, deposit balances, net interest income, provisions, and alert volumes. These fields support forecasting and executive-level interpretation.

## Built-In Data Issues

The data intentionally contains realistic imperfections:

- Missing income and missing PD values
- Invalid loan amount examples
- Duplicate customer identifiers
- Stale records
- Risk and finance exposure mismatches
- Suspicious transaction patterns
- Fraud labels for threshold testing

These issues make the governance pages meaningful. The platform can show how bad data affects risk aggregation, reconciliation, reporting confidence, and audit evidence.

## End-to-End Story

A borrower portfolio deteriorates during a macro shock. PD increases because borrowers are more likely to default. LGD may increase if collateral values fall or recoveries weaken. EAD defines the exposure amount at risk.

Higher PD, LGD, or EAD increases expected credit loss. IFRS 9 staging may move some exposures from Stage 1 to Stage 2 or Stage 3. Provisions increase, profit falls, retained earnings fall, and CET1 can fall. COREP-style ratios then show the capital impact.

At the same time, the governance layer checks whether the underlying data is complete, accurate, consistent, timely, and traceable. If data quality is weak, the platform highlights remediation actions before relying on the output.

## How To Explore It

Start with Banking 101 if the concepts are new. Then use Executive Overview to understand the whole portfolio. Move into Credit Risk, IFRS 9, Basel Capital, Liquidity, Fraud/AML, and Governance pages depending on the question you want to answer. Use Documentation & Study Guide for deeper revision and end-to-end case studies.
