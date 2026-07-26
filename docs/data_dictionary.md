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
