# End-To-End Walkthroughs

## Walkthrough 1: Credit Risk And Capital Impact

Input: synthetic loan portfolio with PD, LGD and EAD.

Logic:

```text
Loan portfolio -> PD/LGD/EAD -> ECL -> provision -> CET1 -> RWA -> CET1 ratio -> reporting
```

Output: borrower-level expected loss, portfolio ECL, simplified provision impact, CET1 ratio and COREP/FINREP-style reporting.

Limitation: capital impact is a simplified educational bridge, not a regulatory capital calculation.

Interview talking point: I can explain how borrower risk becomes accounting loss and capital pressure.

## Walkthrough 2: BCBS 239 Issue

Input: synthetic portfolio with missing income.

Logic:

```text
30% missing income -> completeness control failure -> sensitivity impact -> issue -> 1LOD remediation -> evidence -> 2LOD review -> closure or rejection -> audit log
```

Output: failed control, issue owner, evidence requirement, downstream model/report impact and audit trail.

Limitation: thresholds and materiality are educational and institution-specific in practice.

Interview talking point: I can explain why data quality is not separate from model and reporting reliability.

## Walkthrough 3: Model-Risk Escalation

Input: synthetic PD model with calibration deterioration.

Logic:

```text
PD calibration deterioration -> red monitoring breach -> finding -> governance issue -> use restriction -> revalidation -> reporting-readiness impact
```

Output: model-risk finding, active restriction, revalidation trigger, executive narrative and model confidence indicator.

Limitation: monitoring metrics do not automatically determine accounting adjustments.

Interview talking point: I can explain why high AUC is not enough if calibration, stability or governance is weak.
