# Technical Debt Register

This register tracks known issues identified during Phase 1. Items are intentionally explicit so later phases can improve the project without removing useful existing functionality.

## High Priority

1. `app.py` is too large.
   - Current issue: active Streamlit logic is concentrated in the root app file.
   - Risk: harder maintenance, harder testing of page UI, and higher chance of accidental regressions.
   - Recommended phase: Phase 2.

2. Page classification metadata is missing.
   - Current issue: pages do not consistently declare `Model Lab`, `Analytical Engine`, or `Concept Simulator`.
   - Risk: users may misread simplified modules as production-grade implementations.
   - Recommended phase: Phase 2.

3. Input validation is inconsistent.
   - Current issue: some controls use Streamlit bounds, but calculation functions do not consistently validate invalid direct inputs.
   - Risk: hidden incorrect outputs if functions are reused outside the UI.
   - Recommended phase: Phase 3.

4. IFRS 9 lifetime ECL is simplified.
   - Current issue: lifetime ECL uses an approximation rather than a period-by-period survival, marginal PD, LGD, EAD, discount factor table.
   - Risk: reduced modelling depth for one of the core project modules.
   - Recommended phase: Phase 3.

5. Governance workflow depth is incomplete.
   - Current issue: 1LOD/2LOD/3LOD concepts exist, but workflow statuses, evidence, rejection handling, and role views need expansion.
   - Risk: governance capability looks thinner than the analytical modules.
   - Recommended phase: Phase 4.

## Medium Priority

6. Test suite does not cover every required invariant.
   - Current issue: existing tests cover many formulas, but not all boundary, integration, and regression cases listed in the upgrade spec.
   - Risk: future refactors may silently change core outputs.
   - Recommended phases: Phase 3 onward.

7. Documentation is not yet complete against the upgrade spec.
   - Current issue: README and supporting docs exist, but `financial_assumptions.md`, `interview_guide.md`, and formula-specific docs need to be added.
   - Risk: project is harder to explain consistently in interviews.
   - Recommended phase: Phase 6.

8. Synthetic data strategy needs richer states.
   - Current issue: synthetic data includes defects, but there is no explicit clean, defective, baseline, monitoring, and stressed dataset split.
   - Risk: limits monitoring and governance demonstrations.
   - Recommended phase: Phase 4 or Phase 5.

9. Model cards are mostly document-based.
   - Current issue: model cards exist in docs but are not fully integrated as downloadable app outputs for each statistical model.
   - Risk: model governance story is less interactive.
   - Recommended phase: Phase 5.

## Lower Priority

10. Some extended modules are intentionally concept simulators.
    - Current issue: XVA, DORA, AI governance, climate risk, CRR3, and regulatory reporting are simplified.
    - Risk: acceptable if labelled clearly, misleading if not labelled.
    - Recommended phase: Phase 2 for labels, later phases only if deeper implementation is required.

11. Static analysis tooling is not configured.
    - Current issue: `ruff` and `mypy` are not installed or configured.
    - Risk: style/type issues may be missed.
    - Recommended phase: Phase 6, unless introduced earlier with clean configuration.
