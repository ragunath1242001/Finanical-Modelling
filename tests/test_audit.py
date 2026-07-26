from pathlib import Path

import src.governance.audit as audit


def test_audit_log_event_written(tmp_path):
    audit.AUDIT_DB = Path(tmp_path) / "audit.sqlite"
    audit.log_event("tester", "IFRS 9", "PD shock changed", "0", "30%", "unit test")
    events = audit.read_events()
    assert len(events) == 1
    assert events["action"].iloc[0] == "PD shock changed"
