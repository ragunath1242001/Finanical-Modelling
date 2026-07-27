# Model Risk Management

Phase 5 adds an educational model-risk lifecycle:

```text
Model inventory -> classification -> development evidence -> independent validation -> approval -> monitoring -> finding -> use restriction -> revalidation -> retirement
```

The implementation uses synthetic models and metrics. It is not a formal model-risk policy or production approval system.

## Roles

- Model Developer: builds the model and provides development evidence.
- Model Owner: owns use, monitoring, limitations and remediation.
- Independent Validator: challenges design, implementation, performance and intended use.
- Model Risk Manager: oversees inventory, tiering, approvals and aggregate risk.
- Business User: interprets outputs within approved use.
- Internal Audit: reviews lifecycle evidence and control operation.
- Executive Risk Committee: reviews material findings and restrictions.

## Key Distinction

Model development builds the model. Independent validation challenges whether the model is conceptually sound, correctly implemented and fit for intended use. Monitoring does not replace validation; it checks ongoing performance and drift.
