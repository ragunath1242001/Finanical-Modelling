"""Model limitations register."""

from __future__ import annotations

from datetime import date

import pandas as pd

from src.data.synthetic_model_risk import synthetic_limitations
from src.model_risk.models import Limitation, ModelRiskError


def validate_limitation(limitation: Limitation) -> None:
    if not limitation.owner or not limitation.expiry_date:
        raise ModelRiskError("Limitation requires owner and review/expiry date.")


def limitation_expired(limitation: Limitation, as_of: date | None = None) -> bool:
    as_of = as_of or date(2026, 7, 27)
    return limitation.expiry_date < as_of


def limitations_frame(limitations: list[Limitation] | None = None) -> pd.DataFrame:
    rows = []
    for item in limitations or synthetic_limitations():
        validate_limitation(item)
        rows.append(item.__dict__ | {"severity": item.severity.value, "expired": limitation_expired(item)})
    return pd.DataFrame(rows)
