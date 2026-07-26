import pandas as pd


def model_inventory() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["Credit PD model", "1.0", "Credit Risk", "Validated with limitations", "Approved", "AUC, calibration, drift", "Synthetic portfolio only"],
            ["Fraud classifier", "1.0", "Financial Crime", "Independent review pending", "Monitoring", "Precision, recall, alert rate", "Class imbalance"],
            ["Forecast baseline", "1.0", "Finance Planning", "Developer review", "Approved for education", "MAPE, residual trend", "Simple moving average/regression"],
        ],
        columns=["model", "version", "owner", "validation_status", "approval_status", "monitoring_metrics", "known_limitations"],
    )


def validation_findings() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["PD-001", "Medium", "Calibration should be benchmarked against observed default rates", "Open"],
            ["FR-001", "High", "Fraud model threshold must be reviewed for false positives", "In remediation"],
            ["DQ-001", "Medium", "Missing PD values can distort IFRS 9 provisions", "Open"],
        ],
        columns=["finding_id", "severity", "finding", "status"],
    )
