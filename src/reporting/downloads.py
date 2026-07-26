from __future__ import annotations

from io import BytesIO
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def dataframe_csv_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False).encode("utf-8")


def _paragraph_text(text: str) -> str:
    return escape(text).replace("\n", "<br/>")


def pdf_report_bytes(title: str, sections: dict[str, str]) -> bytes:
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
    styles = getSampleStyleSheet()
    story = [Paragraph(_paragraph_text(title), styles["Title"]), Spacer(1, 14)]
    for heading, body in sections.items():
        story.extend([Paragraph(_paragraph_text(heading), styles["Heading2"]), Spacer(1, 6)])
        for block in body.split("\n"):
            text = block.strip()
            if not text:
                story.append(Spacer(1, 6))
                continue
            if text.startswith("- "):
                text = f"&bull; {_paragraph_text(text[2:])}"
            else:
                text = _paragraph_text(text)
            story.append(Paragraph(text, styles["BodyText"]))
        story.append(Spacer(1, 12))
    document.build(story)
    return buffer.getvalue()


def capital_summary_report(cet1_ratio: float, rwa_amount: float, lcr_value: float, nsfr_value: float) -> bytes:
    return pdf_report_bytes(
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
    return pdf_report_bytes(
        f"Model Validation Summary - {model_name}",
        {
            "Metrics": body,
            "Limitations": "Synthetic data only. Metrics are for educational model development and monitoring demonstration.",
            "Recommended Follow-up": "Review calibration, drift, missingness, explainability, and threshold performance before relying on a model.",
        },
    )
