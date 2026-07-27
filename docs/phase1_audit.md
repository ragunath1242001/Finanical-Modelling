# Phase 1 Repository Audit

Date: 2026-07-27

## Scope

This audit compares the current repository against `Upgrade_build_spec.md` and establishes the Phase 1 baseline. Phase 1 is limited to repository audit and stabilisation, naming and disclaimer correction, existing test execution, and technical-debt documentation.

## Repository Snapshot

- Main app: `app.py`
- Source modules: `src/`
- Tests: `tests/`
- Documentation: `docs/`
- Synthetic data: `data/synthetic/`
- Streamlit config: `.streamlit/config.toml`

Current implementation already includes credit risk, IFRS 9, Basel/CRR3, COREP/FINREP-style reporting, stress testing, liquidity, fraud/AML, BCBS 239 governance, model risk, AI governance, DORA, climate risk, XVA, Banking 101, documentation, case studies, reports, and tests.

## Baseline Checks

- `python -m pytest`: 49 tests passed before Phase 1 edits.
- `python -m compileall -q app.py src tests`: passed before Phase 1 edits.
- `ruff`: not installed in the project environment.
- `mypy`: not installed in the project environment.

No broken imports were found during baseline compile and import checks.

## Stabilisation Actions

- Centralised the preferred product name as `European Banking Risk & Governance Lab`.
- Added a shared portfolio disclaimer constant.
- Updated visible app naming and README positioning.
- Added the exact independent educational portfolio disclaimer required by the build specification.

## Key Gaps Against Specification

- `app.py` is still monolithic and should be refactored in Phase 2.
- Page-level modelling-depth labels are not yet consistently displayed.
- Not every module follows the required Concept, Inputs, Live calculation, Calculation breakdown, and Interpretation structure.
- A global Learning Mode toggle does not yet exist.
- IFRS 9 lifetime ECL remains simplified and does not yet show a period-by-period discounted survival table.
- PD, LGD, and EAD engines need deeper validation and dedicated UI.
- 1LOD/2LOD/3LOD workflow is not yet complete with full statuses, evidence, role views, and audit history.
- Required financial invariant, boundary, integration, and regression tests are only partially covered.
- Documentation still needs `financial_assumptions.md`, `interview_guide.md`, and fuller formula documentation.

## Phase 1 Conclusion

The repository is stable enough to proceed. Existing tests pass, imports compile, and the main risk-learning functionality is intact. The largest remaining issue is architecture: the active Streamlit application needs to be decomposed into smaller page modules without losing current functionality.
