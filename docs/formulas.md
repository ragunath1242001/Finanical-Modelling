# Formula Reference

All formulas are educational approximations implemented on synthetic data.

## Point-In-Time Expected Loss

Formula:

```text
EL = PD x LGD x EAD
```

Variables: PD and LGD are percentages between 0 and 1. EAD is exposure amount.

Implementation: `src/risk/expected_loss.py`.

Limitation: not a complete IFRS 9 or IRB methodology.

## Revolving EAD

```text
EAD = drawn amount + CCF x undrawn commitment
```

Variables: CCF is the credit conversion factor.

Implementation: `src/risk/ead.py`.

Limitation: behavioural drawdown modelling is not included.

## Recovery-Based LGD

```text
Collateral recovery = collateral value x (1 - haircut) x recovery rate
NPV recovery = max(collateral recovery + unsecured recovery - recovery cost, 0) x discount factor
LGD = 1 - NPV recovery / EAD + downturn adjustment
```

Implementation: `src/risk/lgd.py`.

Limitation: collateral valuation, legal recovery and workout timing are simplified.

## Marginal PD And Survival

```text
Marginal PD(t) = survival(t-1) x conditional PD(t)
Survival(t) = survival(t-1) x (1 - conditional PD(t))
Cumulative PD(t) = cumulative PD(t-1) + marginal PD(t)
```

Implementation: `src/risk/pd.py`.

Limitation: term structures are educational and not calibrated to a bank portfolio.

## Lifetime ECL

```text
Discounted ECL(t) = marginal PD(t) x LGD(t) x EAD(t) x discount factor(t)
Lifetime ECL = sum discounted ECL(t)
```

Implementation: `src/risk/expected_loss.py` and `src/risk/ifrs9.py`.

Limitation: no full contractual cash-shortfall engine.

## Scenario-Weighted ECL

```text
Scenario-weighted ECL = sum(scenario probability x scenario ECL)
```

Implementation: `src/risk/ifrs9.py` and `src/risk/scenarios.py`.

Limitation: scenario weights are illustrative.

## Provision Bridge

```text
Closing allowance = opening allowance + increases - decreases
```

Implementation: `src/risk/provision_bridge.py`.

Limitation: simplified movement categories only.

## CET1 Bridge

```text
After-tax impairment impact = incremental impairment x (1 - tax rate)
Closing CET1 = opening CET1 + profit before impairment - after-tax impairment - dividends + regulatory adjustments + other movements
```

Implementation: `src/risk/capital_bridge.py`.

Limitation: regulatory capital adjustments are simplified.

## CET1 Ratio

```text
CET1 ratio = CET1 / total RWA
```

Implementation: `src/risk/basel.py`.

Limitation: buffers and jurisdiction-specific rules are not modelled.

## Leverage Ratio

```text
Leverage ratio = Tier 1 capital / total exposure measure
```

Implementation: `src/risk/liquidity.py`.

Limitation: total exposure measure is simplified.

## Standardised RWA

```text
RWA = exposure amount x risk weight
Capital requirement = RWA x 8%
```

Implementation: `src/risk/basel.py`.

Limitation: risk weights are illustrative, not jurisdiction-specific.

## Output Floor

```text
Final RWA = max(model-based RWA, output floor percentage x standardised RWA)
```

Implementation: `src/risk/irb.py` and `src/risk/crr3.py`.

Limitation: not a complete Basel/CRR3 implementation.

## LCR

```text
LCR = High Quality Liquid Assets / 30-day net cash outflows
```

Implementation: `src/risk/liquidity.py`.

Limitation: HQLA classification and outflow rates are simplified.

## NSFR

```text
NSFR = Available Stable Funding / Required Stable Funding
```

Implementation: `src/risk/liquidity.py`.

Limitation: funding-factor granularity is not modelled.

## PSI

```text
PSI = sum((actual proportion - expected proportion) x ln(actual proportion / expected proportion))
```

Implementation: `src/model_risk/drift.py`.

Limitation: thresholds are educational and institution-specific.

## Reconciliation Difference

```text
Difference = Risk value - Finance value
```

Implementation: `src/governance/reconciliation.py`.

Limitation: materiality thresholds are illustrative.
