import pandas as pd


def issue_queue() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["DQ-101", "Missing PD values", "1LOD Data Steward", "Impact assessment", "2LOD challenge pending"],
            ["REC-204", "Risk/finance exposure mismatch", "1LOD Finance Owner", "Root cause analysis", "Open"],
            ["MRM-077", "Fraud threshold monitoring", "Model Owner", "Remediation plan submitted", "2LOD review"],
        ],
        columns=["issue_id", "issue", "owner", "1lod_status", "2lod_status"],
    )
