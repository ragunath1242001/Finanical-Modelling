# Data Quality Controls

The Phase 4 control engine defines structured controls with control ID, name, data element, quality dimension, type, severity, threshold, owner, source system and downstream process.

Implemented controls include:

- Missing customer income.
- Missing customer ID.
- Duplicate customer ID.
- PD outside `[0, 1]`.
- LGD outside `[0, 1]`.
- Negative EAD.
- Invalid risk grade.
- Missing model version.
- Missing source-system identifier.
- Stale collateral valuation.
- Missing origination PD.
- Invalid IFRS 9 stage.
- Scenario weights not totalling 100%.
- Finance exposure differing from Risk exposure.
- Missing lineage link.
- Inconsistent reporting date.
- Missing issue owner.
- Overdue remediation date.
- Closed issue without closure evidence.
- 2LOD-rejected issue incorrectly marked as closed.

Each execution returns records tested, records failed, failure rate, pass/fail status, severity, sample failed records, affected data elements and downstream impact.

Material failed controls create educational governance issues.
