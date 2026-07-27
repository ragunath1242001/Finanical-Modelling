# Data Dictionary

## Customers

- `customer_id`: Synthetic customer key.
- `age`: Customer age.
- `income`: Annual income, with intentional missing values.
- `employment_status`: Employment category.
- `credit_score`: Synthetic credit score.
- `debt_to_income`: Debt service burden.
- `country`: Country code.
- `customer_risk`: KYC-style risk category.

## Loans

- `loan_id`: Synthetic loan key.
- `product_type`: Mortgage, personal loan, credit card, or SME loan.
- `loan_amount`: Original exposure amount, with intentional invalid values.
- `outstanding_balance`: Current balance.
- `ltv`: Loan-to-value ratio.
- `days_past_due`: Delinquency indicator.
- `default_flag`: Synthetic default indicator.
- `pd`, `lgd`, `ead`: Risk parameters for ECL and capital illustrations.

## Transactions

- `amount`, `merchant_category`, `hour`, `country_risk`, `device_mismatch`, `velocity_24h`: Fraud and AML scoring features.
- `fraud_label`: Synthetic label for threshold education.
- `round_amount`, `rapid_in_out`: AML rule indicators.

## Reporting Fields

- `CET1`, `AT1`, `Tier 2`, `RWA`, `LCR`, `NSFR`, `leverage_ratio`: Capital and liquidity indicators.
- `assets`, `liabilities`, `net_interest_income`, `provisions`, `profit`: FINREP-style indicators.

## Synthetic Governance Fields

- `account_id`, `facility_id`: synthetic reconciliation keys used to match Risk and Finance views.
- `model_version`: model version used for traceability and auditability.
- `source_system`: source-system identifier used for lineage.
- `collateral_valuation_date`: collateral freshness date used by stale-collateral controls.
- `origination_pd`: origination PD used for educational SICR analysis.
- `ifrs9_stage`: educational IFRS 9 stage value, expected to be 1, 2 or 3.
- `scenario_weight_total`: total scenario probability, expected to equal 1.
- `lineage_link`: synthetic lineage reference from record to report.
- `issue_owner`, `remediation_due_date`, `issue_status`, `closure_evidence`, `two_lod_conclusion`: workflow fields used to demonstrate 1LOD/2LOD closure controls.
- `risk_value`, `finance_value`, `difference`: reconciliation values where `difference = Risk value - Finance value`.

## Synthetic Model-Risk Fields

- `model_id`, `model_version`: unique model identifier and version.
- `model_family`: model family such as PD, LGD, fraud, AML, forecasting or stress testing.
- `lifecycle_status`: current lifecycle state from proposal through retirement.
- `model_tier`: educational materiality tier.
- `approval_status`: approval, conditional approval, rejection or deferral status.
- `last_validation_date`, `next_validation_date`: validation timeline fields.
- `monitoring_frequency`: expected monitoring cadence.
- `open_issues`, `limitations`, `use_restrictions`: governance controls linked to model use.
- `auc`, `brier_score`, `calibration_error`, `psi`: monitoring metrics for the synthetic PD model.
- `finding_id`, `severity`, `recommendation`, `closure_evidence`: validation finding fields.
