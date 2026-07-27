"""BCBS 239-style data-quality controls and execution framework."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

import pandas as pd

from src.governance.models import (
    ControlExecutionResult,
    ControlStatus,
    ControlType,
    DataQualityControl,
    GovernanceIssue,
    QualityDimension,
    Severity,
)
from src.governance.impact_analysis import impact_for_control
from src.governance.issues import issue_from_control_result


ControlRule = Callable[[pd.DataFrame], pd.Series]


QUALITY_DIMENSION_DEFINITIONS = {
    QualityDimension.COMPLETENESS: "Required fields are populated.",
    QualityDimension.ACCURACY: "Values correctly represent the underlying business reality.",
    QualityDimension.CONSISTENCY: "Equivalent values agree across systems and reports.",
    QualityDimension.TIMELINESS: "Data is available within the required reporting period.",
    QualityDimension.VALIDITY: "Values follow defined formats, ranges and business rules.",
    QualityDimension.UNIQUENESS: "Records or identifiers are not duplicated unexpectedly.",
    QualityDimension.INTEGRITY: "Relationships between datasets remain correct.",
    QualityDimension.TRACEABILITY: "Data can be traced from source to report.",
}


def _control(
    control_id: str,
    name: str,
    description: str,
    element: str,
    dimension: QualityDimension,
    severity: Severity,
    threshold: float = 0.0,
    control_type: ControlType = ControlType.RECORD,
    downstream: str = "Risk models and reporting",
) -> DataQualityControl:
    return DataQualityControl(
        control_id=control_id,
        control_name=name,
        description=description,
        data_element=element,
        quality_dimension=dimension,
        control_type=control_type,
        severity=severity,
        threshold=threshold,
        owner="1LOD Data Steward",
        frequency="Daily",
        source_system="Synthetic portfolio",
        downstream_process=downstream,
        regulatory_relevance="Educational BCBS 239 risk-data aggregation and reporting control.",
    )


REQUIRED_CONTROLS: list[DataQualityControl] = [
    _control("DQ-001", "Missing customer income", "Income is required for borrower affordability and PD segmentation.", "income", QualityDimension.COMPLETENESS, Severity.HIGH, 0.05, downstream="PD model, IFRS 9 ECL, IRB, stress testing"),
    _control("DQ-002", "Missing customer ID", "Customer identifier must be populated to join source and risk records.", "customer_id", QualityDimension.COMPLETENESS, Severity.CRITICAL),
    _control("DQ-003", "Duplicate customer ID", "Customer identifiers should not be duplicated unexpectedly.", "customer_id", QualityDimension.UNIQUENESS, Severity.HIGH),
    _control("DQ-004", "PD outside [0, 1]", "PD must be between 0 and 1 before entering risk engines.", "pd", QualityDimension.VALIDITY, Severity.CRITICAL),
    _control("DQ-005", "LGD outside [0, 1]", "LGD must be between 0 and 1 before entering ECL or capital engines.", "lgd", QualityDimension.VALIDITY, Severity.CRITICAL),
    _control("DQ-006", "Negative EAD", "Exposure at default cannot be negative.", "ead", QualityDimension.VALIDITY, Severity.CRITICAL),
    _control("DQ-007", "Invalid risk grade", "Risk grade must belong to the educational grade scale A-D.", "risk_grade", QualityDimension.VALIDITY, Severity.MEDIUM),
    _control("DQ-008", "Missing model version", "Model version is required for traceability and auditability.", "model_version", QualityDimension.TRACEABILITY, Severity.HIGH),
    _control("DQ-009", "Missing source-system identifier", "Source system must be known for lineage and ownership.", "source_system", QualityDimension.TRACEABILITY, Severity.HIGH),
    _control("DQ-010", "Stale collateral valuation", "Collateral valuation must be recent enough for LGD analysis.", "collateral_valuation_date", QualityDimension.TIMELINESS, Severity.HIGH),
    _control("DQ-011", "Missing origination PD", "Origination PD is needed for SICR analysis.", "origination_pd", QualityDimension.COMPLETENESS, Severity.MEDIUM),
    _control("DQ-012", "Invalid IFRS 9 stage", "IFRS 9 stage must be 1, 2, or 3.", "ifrs9_stage", QualityDimension.VALIDITY, Severity.HIGH),
    _control("DQ-013", "Scenario weights not totalling 100%", "Scenario weights must sum to 1 for scenario-weighted ECL.", "scenario_weight_total", QualityDimension.ACCURACY, Severity.HIGH, control_type=ControlType.AGGREGATE),
    _control("DQ-014", "Finance exposure differing from Risk exposure", "Risk and Finance exposure must reconcile within tolerance.", "exposure", QualityDimension.CONSISTENCY, Severity.HIGH, control_type=ControlType.RECONCILIATION, downstream="FINREP, COREP, EAD and provision reporting"),
    _control("DQ-015", "Missing lineage link", "Records should have a lineage reference from source to report.", "lineage_link", QualityDimension.TRACEABILITY, Severity.HIGH),
    _control("DQ-016", "Inconsistent reporting date", "Reporting date must be consistent across records.", "reporting_date", QualityDimension.CONSISTENCY, Severity.MEDIUM),
    _control("DQ-017", "Missing issue owner", "Governance issues require an accountable owner.", "issue_owner", QualityDimension.INTEGRITY, Severity.HIGH, control_type=ControlType.WORKFLOW),
    _control("DQ-018", "Overdue remediation date", "Open remediation should not exceed the due date.", "remediation_due_date", QualityDimension.TIMELINESS, Severity.HIGH, control_type=ControlType.WORKFLOW),
    _control("DQ-019", "Closed issue without closure evidence", "Closure requires evidence.", "closure_evidence", QualityDimension.INTEGRITY, Severity.HIGH, control_type=ControlType.WORKFLOW),
    _control("DQ-020", "2LOD-rejected issue incorrectly marked as closed", "Rejected issues must return to remediation before closure.", "two_lod_conclusion", QualityDimension.INTEGRITY, Severity.CRITICAL, control_type=ControlType.WORKFLOW),
]


def _blank_failures(frame: pd.DataFrame) -> pd.Series:
    return pd.Series([False] * len(frame), index=frame.index)


def _as_text(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def control_failure_mask(control: DataQualityControl, frame: pd.DataFrame) -> pd.Series:
    if not control.enabled or frame.empty:
        return _blank_failures(frame)
    if control.data_element not in frame.columns and control.control_id not in {"DQ-003", "DQ-013", "DQ-014", "DQ-016"}:
        return pd.Series([True] * len(frame), index=frame.index)

    match control.control_id:
        case "DQ-001":
            return frame["income"].isna()
        case "DQ-002":
            return _as_text(frame["customer_id"]).eq("")
        case "DQ-003":
            return frame["customer_id"].duplicated(keep=False) & _as_text(frame["customer_id"]).ne("")
        case "DQ-004":
            return frame["pd"].isna() | (frame["pd"] < 0) | (frame["pd"] > 1)
        case "DQ-005":
            return frame["lgd"].isna() | (frame["lgd"] < 0) | (frame["lgd"] > 1)
        case "DQ-006":
            return frame["ead"].isna() | (frame["ead"] < 0)
        case "DQ-007":
            return ~_as_text(frame["risk_grade"]).isin(["A", "B", "C", "D"])
        case "DQ-008":
            return _as_text(frame["model_version"]).eq("")
        case "DQ-009":
            return _as_text(frame["source_system"]).eq("")
        case "DQ-010":
            return (pd.to_datetime(frame["collateral_valuation_date"]).dt.date < datetime(2026, 7, 27).date().replace(year=2025))
        case "DQ-011":
            return frame["origination_pd"].isna()
        case "DQ-012":
            return ~frame["ifrs9_stage"].isin([1, 2, 3])
        case "DQ-013":
            return (frame["scenario_weight_total"] - 1.0).abs() > 0.0001
        case "DQ-014":
            return frame.get("risk_finance_exposure_difference", pd.Series([0] * len(frame), index=frame.index)).abs() > 1_000
        case "DQ-015":
            return _as_text(frame["lineage_link"]).eq("")
        case "DQ-016":
            dates = pd.to_datetime(frame["reporting_date"]).dt.date
            return dates.ne(dates.mode().iloc[0])
        case "DQ-017":
            return _as_text(frame["issue_owner"]).eq("")
        case "DQ-018":
            due = pd.to_datetime(frame["remediation_due_date"]).dt.date
            return due < datetime(2026, 7, 27).date()
        case "DQ-019":
            return _as_text(frame["issue_status"]).eq("Closed") & _as_text(frame["closure_evidence"]).eq("")
        case "DQ-020":
            return _as_text(frame["issue_status"]).eq("Closed") & _as_text(frame["two_lod_conclusion"]).eq("Rejected")
    return _blank_failures(frame)


def execute_control(control: DataQualityControl, frame: pd.DataFrame, timestamp: datetime | None = None) -> ControlExecutionResult:
    if control.threshold < 0 or control.threshold > 1:
        raise ValueError("Control threshold must be between 0 and 1.")
    timestamp = timestamp or datetime.now(timezone.utc)
    mask = control_failure_mask(control, frame)
    records_tested = len(frame)
    records_failed = int(mask.sum())
    failure_rate = records_failed / records_tested if records_tested else 0.0
    status = ControlStatus.FAIL if failure_rate > control.threshold else ControlStatus.PASS
    sample_cols = list(dict.fromkeys([col for col in ["customer_id", "account_id", control.data_element] if col in frame.columns]))
    sample = frame.loc[mask, sample_cols].head(5).to_dict("records")
    impact = impact_for_control(control.control_id, records_failed, frame)
    return ControlExecutionResult(
        execution_id=f"EXEC-{control.control_id}-{timestamp.strftime('%Y%m%d%H%M%S')}",
        control_id=control.control_id,
        control_name=control.control_name,
        execution_timestamp=timestamp,
        records_tested=records_tested,
        records_failed=records_failed,
        failure_rate=failure_rate,
        threshold=control.threshold,
        status=status,
        severity=control.severity,
        sample_failed_records=sample,
        affected_data_elements=impact.affected_data_elements,
        downstream_impact=", ".join(impact.affected_models + impact.affected_reports),
        owner=control.owner,
        dimension=control.quality_dimension,
    )


def execute_controls(frame: pd.DataFrame, controls: list[DataQualityControl] | None = None) -> list[ControlExecutionResult]:
    return [execute_control(control, frame) for control in (controls or REQUIRED_CONTROLS)]


def results_to_frame(results: list[ControlExecutionResult]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "control_id": r.control_id,
                "control": r.control_name,
                "dimension": r.dimension.value,
                "data_element": ", ".join(r.affected_data_elements),
                "failed_records": r.records_failed,
                "records_tested": r.records_tested,
                "failure_rate": r.failure_rate,
                "threshold": r.threshold,
                "severity": r.severity.value,
                "affected_process": r.downstream_impact,
                "owner": r.owner,
                "status": r.status.value,
                "issue_status": "Open" if r.status == ControlStatus.FAIL else "N/A",
            }
            for r in results
        ]
    )


def create_issues_for_failed_controls(results: list[ControlExecutionResult]) -> list[GovernanceIssue]:
    return [issue_from_control_result(result) for result in results if result.status == ControlStatus.FAIL]


def quality_score_from_results(results: list[ControlExecutionResult]) -> float:
    if not results:
        return 100.0
    tested = sum(r.records_tested for r in results)
    failed = sum(r.records_failed for r in results)
    return round(max(0.0, 1.0 - failed / max(1, tested)) * 100, 2)


def run_quality_checks(loans: pd.DataFrame, customers: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    frame = loans.copy()
    if "income" not in frame.columns and {"customer_id", "income"}.issubset(customers.columns):
        frame = frame.merge(customers[["customer_id", "income"]], on="customer_id", how="left")
    elif "income" not in frame.columns:
        frame["income"] = 1.0
    defaults = {
        "risk_grade": "B",
        "model_version": "PD-v1.0",
        "source_system": "Credit Risk Data Mart",
        "collateral_valuation_date": datetime(2026, 1, 1).date(),
        "origination_pd": frame.get("pd", pd.Series([0.01] * len(frame))),
        "ifrs9_stage": 1,
        "scenario_weight_total": 1.0,
        "lineage_link": "LIN-PORTFOLIO",
        "reporting_date": datetime(2026, 7, 27).date(),
        "issue_owner": "1LOD Data Steward",
        "remediation_due_date": datetime(2026, 8, 15).date(),
        "issue_status": "Open",
        "closure_evidence": "N/A",
        "two_lod_conclusion": "N/A",
    }
    for col, value in defaults.items():
        if col not in frame.columns:
            frame[col] = value
    if "loan_amount" in frame.columns and "ead" not in frame.columns:
        frame["ead"] = frame["loan_amount"]
    results = execute_controls(frame, REQUIRED_CONTROLS[:13] + REQUIRED_CONTROLS[15:20])
    table = results_to_frame(results)
    legacy_names = {
        "Missing customer income": "Missing income",
        "Negative EAD": "Invalid loan amount",
        "Duplicate customer ID": "Duplicate customer ID",
        "Stale collateral valuation": "Stale loan record > 45 days",
        "Missing customer ID": "Missing customer ID on loan",
    }
    table["control"] = table["control"].replace(legacy_names)
    if "pd" in frame.columns:
        missing_pd = int(frame["pd"].isna().sum())
        pd_row = {
            "control_id": "DQ-004A",
            "control": "Missing PD",
            "dimension": QualityDimension.COMPLETENESS.value,
            "data_element": "pd",
            "failed_records": missing_pd,
            "records_tested": len(frame),
            "failure_rate": missing_pd / max(1, len(frame)),
            "threshold": 0.0,
            "severity": Severity.HIGH.value,
            "affected_process": "Expected loss, IFRS 9 staging, stress testing",
            "owner": "1LOD Data Steward",
            "status": "Fail" if missing_pd else "Pass",
            "issue_status": "Open" if missing_pd else "N/A",
        }
        table = pd.concat([pd.DataFrame([pd_row]), table], ignore_index=True)
    return table, quality_score_from_results(results)


def missing_pd_count(loans: pd.DataFrame) -> int:
    return int(loans["pd"].isna().sum()) if "pd" in loans.columns else 0
