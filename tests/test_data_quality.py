import pandas as pd

from src.governance.data_quality import missing_pd_count, run_quality_checks


def test_missing_pd_quality_rule():
    loans = pd.DataFrame(
        {
            "pd": [0.01, None],
            "loan_amount": [100, 200],
            "last_update_days": [1, 2],
            "customer_id": ["C1", "C2"],
        }
    )
    customers = pd.DataFrame({"customer_id": ["C1", "C2"]})
    checks, score = run_quality_checks(loans, customers)
    assert missing_pd_count(loans) == 1
    assert checks.loc[checks["control"].eq("Missing PD"), "failed_records"].iloc[0] == 1
    assert score < 100
