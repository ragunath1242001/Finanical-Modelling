# Financial Assumptions

This project uses synthetic data and educational approximations. It is not a production IFRS 9, Basel, IRB, stress-testing or regulatory-reporting engine.

## PD

PD means probability of default over a defined horizon. The PD engine supports direct point-in-time PD, scenario-adjusted PD and annual conditional PD term structures.

```text
Marginal PD(t) = survival at start of period t x conditional PD(t)
Cumulative PD(t) = sum of marginal PD values up to t
```

## LGD

LGD is the proportion of exposure expected to be lost after recoveries.

```text
LGD = 1 - NPV recoveries / EAD + downturn adjustment
```

Recoveries may include collateral value after haircut, recovery rate, unsecured recovery, recovery cost and time-to-recovery discounting.

## EAD

```text
Term loan EAD = outstanding balance
Revolving EAD = drawn amount + CCF x undrawn commitment
```

EAD must not be below drawn exposure.

## Expected Credit Loss

```text
Expected Loss = PD x LGD x EAD
Discounted ECL(t) = marginal PD(t) x LGD(t) x EAD(t) x discount factor(t)
Lifetime ECL = sum discounted ECL(t)
```

## IFRS 9

The IFRS 9 staging rules are educational:

- Stage 3 takes priority when default or credit-impaired indicators are present.
- Stage 2 is used when significant increase in credit risk indicators are present.
- Stage 1 is used when no SICR/default trigger is present.

Stage 1 uses an educational 12-month ECL approximation based on the first period. Stage 2 and Stage 3 use lifetime ECL.

## Scenario Weighting

```text
Scenario-weighted ECL = sum(scenario probability x scenario ECL)
```

Scenario probabilities must total 1.

## Basel and IRB

```text
RWA = exposure amount x risk weight
Final RWA = max(model-based RWA, output floor percentage x standardised RWA)
```

Risk weights are illustrative and configurable. The IRB comparison is a simplified corporate IRB-style worked example and does not cover all regulatory adjustments.

## Stress Testing

```text
Scenario -> PD/LGD/EAD shock -> ECL -> provision increase -> CET1 bridge -> capital ratio
```

Management actions are represented as simplified inputs such as dividend reduction, capital raise, RWA reduction and provision overlay.

## Phase 4 Governance Assumptions

- Data-quality thresholds are illustrative and policy-specific in real institutions.
- Missing-income impact is shown as a sensitivity by applying a conservative PD uplift to affected valid records.
- Invalid PD, invalid LGD and negative EAD records are prevented from entering the financial sensitivity calculation.
- Risk-versus-Finance differences are classified using configurable tolerances, not formal regulatory materiality.
- CET1 impact from data issues is illustrative and uses the existing simplified after-tax impairment bridge.
- Issue workflow timestamps and users are synthetic or local demo values.

## Phase 5 Model-Risk Assumptions

- Model-risk impacts are labelled as illustrative sensitivity impacts.
- PD calibration deterioration can increase ECL uncertainty, but monitoring metrics do not automatically determine accounting adjustments.
- LGD data-quality findings can restrict use of secured-exposure LGD outputs until collateral data is refreshed.
- Champion-challenger recommendations consider calibration, stability, explainability and operating cost, not AUC alone.
- Monitoring thresholds and tiering scores are educational and institution-specific in practice.
