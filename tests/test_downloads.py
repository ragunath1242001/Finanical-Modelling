import pandas as pd

from src.reporting.downloads import capital_summary_report, dataframe_csv_bytes, pdf_report_bytes, validation_report


def test_dataframe_csv_bytes():
    data = dataframe_csv_bytes(pd.DataFrame({"a": [1], "b": [2]}))
    assert b"a,b" in data


def test_pdf_report_bytes():
    data = pdf_report_bytes("Title", {"Section": "Body"})
    assert data.startswith(b"%PDF")
    assert len(data) > 100


def test_summary_reports_return_bytes():
    assert capital_summary_report(0.12, 1000, 1.1, 1.0)
    assert validation_report({"auc": 0.7}, "Model")
