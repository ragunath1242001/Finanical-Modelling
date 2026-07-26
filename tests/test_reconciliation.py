from src.governance.reconciliation import reconcile_exposure


def test_reconciliation_difference():
    result = reconcile_exposure(100, 112)
    assert result["difference"].iloc[0] == 12
    assert result["status"].iloc[0] == "Open"
