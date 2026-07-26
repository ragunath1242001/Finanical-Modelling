from __future__ import annotations

import pandas as pd


def run_quality_checks(loans: pd.DataFrame, customers: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    checks = [
        ("Missing PD", int(loans["pd"].isna().sum()), "Completeness"),
        ("Invalid loan amount", int((loans["loan_amount"] <= 0).sum()), "Accuracy"),
        ("Duplicate customer ID", int(customers["customer_id"].duplicated().sum()), "Consistency"),
        ("Stale loan record > 45 days", int((loans["last_update_days"] > 45).sum()), "Timeliness"),
        ("Missing customer ID on loan", int(loans["customer_id"].isna().sum()), "Traceability"),
    ]
    result = pd.DataFrame(checks, columns=["control", "failed_records", "dimension"])
    result["status"] = result["failed_records"].apply(lambda x: "Pass" if x == 0 else "Fail")
    total_failures = result["failed_records"].sum()
    denominator = max(1, len(loans) * len(result))
    score = max(0.0, 1 - total_failures / denominator)
    return result, round(score * 100, 2)


def missing_pd_count(loans: pd.DataFrame) -> int:
    return int(loans["pd"].isna().sum())
