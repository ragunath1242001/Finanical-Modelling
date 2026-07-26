# European Financial Risk, Regulatory, and Governance Platform

This is an independent educational portfolio project. It simulates how a financial institution connects credit risk, IFRS 9, Basel III, regulatory reporting, stress testing, liquidity, financial crime monitoring, BCBS 239 controls, and model governance.

## Why This Project Exists

The goal is to make financial risk concepts explainable and interactive. Users can change assumptions and see how PD, LGD, EAD, provisions, profit, CET1, capital ratios, liquidity ratios, fraud alerts, AML alerts, data quality, and governance indicators move together.

## Target Roles

Risk Analyst, Credit Risk Analyst, Risk Data Scientist, Regulatory Reporting Analyst, IFRS 9 Analyst, Basel/Capital Reporting Analyst, Model Risk Analyst, Data Governance Analyst, Financial Crime Analyst, and Financial Services Consultant.

## Architecture

```text
Synthetic data
  -> Credit PD/LGD/EAD
  -> IFRS 9 ECL and staging
  -> Basel III / IRB / COREP / FINREP
  -> Stress, liquidity, fraud, AML, forecasting
  -> BCBS 239 controls, model risk, drift, audit, 1LOD/2LOD
  -> Executive dashboard and interview mode
```

Business logic lives in `src/`. The runnable Streamlit UI is in `app.py`.

## Modules

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
- Interview Mode

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Generate Data

```powershell
python -m src.data.generate_synthetic_data
```

The app also generates synthetic data automatically if the CSV files do not exist.

## Run

```powershell
streamlit run app.py
```

## Test

```powershell
pytest
```

## Data Strategy

The project uses synthetic data by default and does not require private or confidential data. The generator intentionally introduces missing PD values, missing income, duplicate customer IDs, invalid loan amounts, stale records, fraud labels, suspicious transaction features, and risk/finance reconciliation differences.

## Regulatory Caveats

The platform is educational. Basel, CRR3, IRB, COREP, FINREP, IFRS 9, stress testing, fraud, AML, DORA, ESG/climate risk, XVA, drift, AI governance, and governance logic are simplified approximations designed for explanation and interview preparation. The IRB, CVA-lite, operational risk SMA, output floor, reverse stress, climate ECL, and XVA calculations are not production regulatory capital or pricing engines.

## Truthfulness Statement

This is an independent educational portfolio project. It is inspired by BFSI data governance experience and financial risk learning, but it must not be represented as production work performed for any employer unless that is factually true.

## Screenshots

Run the Streamlit app and capture screenshots from the Executive Overview, IFRS 9, Basel Capital, BCBS 239 Governance, and Model Risk pages.

## Interview Narrative

When credit risk deteriorates, PD increases. Higher PD increases expected credit loss under IFRS 9. This increases provisions, which reduces profit and retained earnings. Since retained earnings are part of CET1 capital, CET1 can decrease. That reduction then affects capital ratios reported through COREP.

CRR3 and the final Basel III reforms make capital ratios more comparable by constraining internal model outputs through the output floor and by strengthening standardized treatments for credit risk, CVA, and operational risk.

Reverse stress testing starts from a defined failure outcome, such as a 300 basis point CET1 depletion, and asks what geopolitical, credit, market, funding, or operational shock could plausibly cause it.

EU AI Act-style governance requires high-risk AI systems to be explainable, documented, monitored, traceable, subject to human oversight, and supported by strong data governance.

DORA operational resilience connects ICT incidents, third-party providers, RTO/RPO, resilience testing, exit planning, and reporting workflows.

Climate credit risk translates transition and physical risks into PD, LGD, ECL, provisions, and capital planning effects.

XVA connects derivatives valuation with counterparty credit risk, collateral, funding spreads, margin costs, and model validation.

## Roadmap

- Add richer calibration charts for the PD model.
- Add downloadable COREP/FINREP-style templates.
- Add more detailed SHAP explainability when optional dependencies are available.
- Add persistent user scenario storage.
- Add Monte Carlo exposure simulation for the XVA page.
- Add downloadable DORA incident and third-party oversight reports.
