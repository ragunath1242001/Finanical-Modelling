# Interview Narratives

## Tell me about this project

I built an independent European Financial Risk, Regulatory, and Governance Platform to understand how risk analytics, regulatory reporting, data governance, and model governance connect in financial institutions. The platform simulates credit risk, IFRS 9 expected credit loss, Basel III capital adequacy, COREP/FINREP-style reporting, EBA-style stress testing, AML/fraud monitoring, BCBS 239 controls, and model risk management.

## How does IFRS 9 connect to Basel III?

When credit risk deteriorates, PD increases. Higher PD increases expected credit loss under IFRS 9. This increases provisions, which reduces profit and retained earnings. Since retained earnings are part of CET1 capital, CET1 can decrease. That reduction then affects capital ratios reported through COREP.

## How did you go deeper than a basic credit risk dashboard?

I added a model development lab and an IFRS 9 scenario ECL engine. The model lab trains a logistic regression baseline and gradient boosting challenger, evaluates AUC, average precision, Brier score, calibration, confusion matrix, feature importance, risk grades, and PSI monitoring. The IFRS 9 engine calculates scenario-weighted ECL, stage migration, lifetime PD approximation, and an ECL bridge.

## How do PD, LGD, and EAD feed both IFRS 9 and IRB?

IFRS 9 asks what credit losses are expected, so PD, LGD, and EAD drive provisions. IRB asks how much regulatory capital should be held against credit risk. Similar parameters can feed both processes, but the objective and regulatory treatment are different.

## Why is BCBS 239 important?

BCBS 239 is important because risk calculations are only reliable if the underlying data is accurate, complete, timely, consistent, and traceable. A sophisticated PD model is not enough if exposure, income, default history, or customer identifiers are missing or inconsistent.

## What is the role of 1LOD and 2LOD?

The First Line of Defense owns and manages risk in day-to-day operations, including data stewardship, model operation, and remediation. The Second Line of Defense provides independent oversight, challenge, monitoring, and guidance through risk, compliance, validation, and governance functions.

## How does model risk management apply here?

Model risk management covers the lifecycle from development through validation, approval, deployment, monitoring, and retirement. In this platform, model cards, validation findings, reason codes, drift checks, and audit logs show how model outputs are controlled and challenged.

## What did you add for CRR3 and final Basel III reforms?

I added an educational CRR3 lab covering the output floor, operational risk standardized measurement approximation, and CVA-lite counterparty risk. The point is to show how final Basel III reforms constrain internal model RWA and make capital ratios more comparable across banks.

## What is reverse stress testing?

Reverse stress testing starts with a target failure outcome, such as a 300 basis point CET1 depletion, and asks what scenario could plausibly cause it. In the platform, geopolitical shocks transmit through credit losses, market losses, operational or cyber disruption, and funding cost pressure.

## How does EU AI Act governance apply here?

For high-risk financial AI use cases such as credit scoring, fraud detection, and AML monitoring, governance must cover data quality, documentation, logging, explainability, human oversight, robustness, fairness, monitoring, and auditability. The platform turns those expectations into a control checklist and evidence trail.

## What is DORA and why did you add it?

DORA focuses on digital operational resilience. I added an incident and third-party risk module to show how banks assess ICT incidents, critical provider dependency, RTO/RPO performance, resilience testing, exit plans, and evidence for oversight.

## How does climate risk connect to credit risk?

Climate risk can affect borrower cash flows and collateral values. Transition risk can raise PD for exposed sectors, while physical risk and collateral decline can raise LGD. The platform translates those scenario assumptions into ECL and capital planning impacts.

## What is XVA?

XVA is a family of valuation adjustments for derivatives. CVA estimates counterparty credit loss on positive exposure, FVA captures funding cost, MVA captures initial margin funding cost, and DVA represents own-credit effects. I implemented a simplified XVA lab to show the core drivers without claiming production derivatives pricing.

## How is this related to BFSI data governance experience?

BFSI data governance experience helped me understand why data quality, lineage, reconciliation, and auditability matter in financial services. I built this independent project to extend that foundation into credit risk, IFRS 9, Basel III, stress testing, and model governance.
