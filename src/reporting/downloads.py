from __future__ import annotations

import pandas as pd


def dataframe_csv_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False).encode("utf-8")


def markdown_report_bytes(title: str, sections: dict[str, str]) -> bytes:
    lines = [f"# {title}", ""]
    for heading, body in sections.items():
        lines.extend([f"## {heading}", "", body, ""])
    return "\n".join(lines).encode("utf-8")


def capital_summary_report(cet1_ratio: float, rwa_amount: float, lcr_value: float, nsfr_value: float) -> bytes:
    return markdown_report_bytes(
        "Capital and Liquidity Summary",
        {
            "Capital": f"CET1 ratio: {cet1_ratio:.2%}\n\nRWA: EUR {rwa_amount:,.0f}",
            "Liquidity": f"LCR: {lcr_value:.1%}\n\nNSFR: {nsfr_value:.1%}",
            "Interpretation": "This report is generated from simplified educational calculations in the Streamlit platform.",
        },
    )


def validation_report(metrics: pd.Series | dict[str, float], model_name: str) -> bytes:
    values = dict(metrics)
    body = "\n".join(f"- {key}: {value:.4f}" if isinstance(value, float) else f"- {key}: {value}" for key, value in values.items())
    return markdown_report_bytes(
        f"Model Validation Summary - {model_name}",
        {
            "Metrics": body,
            "Limitations": "Synthetic data only. Metrics are for educational model development and monitoring demonstration.",
            "Recommended Follow-up": "Review calibration, drift, missingness, explainability, and threshold performance before relying on a model.",
        },
    )
