# Risk-Versus-Finance Reconciliation

The reconciliation engine matches synthetic Risk and Finance datasets on:

- customer ID;
- account ID;
- facility ID;
- reporting date.

It compares exposure and provision values using:

```text
Reconciliation difference = Risk value - Finance value
```

Differences are classified as immaterial, moderate, material or critical using configurable tolerances. The engine also reports unmatched Risk records, unmatched Finance records, total difference and whether an explanation is required.

The reporting page uses this output to label report-production readiness as Ready, Ready with limitations, Not ready or Under review.
