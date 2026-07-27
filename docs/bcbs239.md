# BCBS 239 Governance

This project uses BCBS 239 as an educational framework for risk data aggregation and risk reporting. It does not claim regulatory compliance.

The governance workflow is:

```text
Source data -> data-quality control -> model/report impact -> issue creation -> 1LOD remediation -> 2LOD challenge -> closure evidence -> audit trail
```

## Quality Dimensions

- Completeness: required fields are populated.
- Accuracy: values reflect the intended business meaning.
- Consistency: values agree across systems and reports.
- Timeliness: data is available within the required period.
- Validity: values follow allowed ranges, formats and business rules.
- Uniqueness: identifiers are not duplicated unexpectedly.
- Integrity: relationships and workflow requirements are preserved.
- Traceability: data can be traced from source to report.

## Educational Limitation

The controls run on synthetic data and use simplified thresholds. In a real institution, thresholds, owners, materiality, escalation and closure requirements would be policy-specific.
