# Model Drift

The project distinguishes:

- Data drift: input distributions change.
- Prediction drift: output score distributions change.
- Target drift: observed outcomes change.
- Concept drift: the relationship between inputs and outcomes changes.
- Performance deterioration: predictive performance worsens.

Population Stability Index is calculated as:

```text
PSI = sum((Actual proportion - Expected proportion) x ln(Actual proportion / Expected proportion))
```

An epsilon is used for zero-frequency bins. PSI thresholds are educational only.
