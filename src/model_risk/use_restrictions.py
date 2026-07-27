"""Use restriction helpers."""

from __future__ import annotations

from datetime import date

import pandas as pd

from src.data.synthetic_model_risk import synthetic_restrictions
from src.model_risk.models import UseRestriction


def restriction_active(restriction: UseRestriction, as_of: date | None = None) -> bool:
    as_of = as_of or date(2026, 7, 27)
    return restriction.active_status and (restriction.expiry_date is None or restriction.expiry_date >= as_of)


def restrictions_frame(restrictions: list[UseRestriction] | None = None) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "restriction_id": item.restriction_id,
                "model_id": item.model_id,
                "restriction": item.restriction,
                "reason": item.reason,
                "expiry_date": item.expiry_date.isoformat() if item.expiry_date else "",
                "approving_role": item.approving_role,
                "linked_finding": item.linked_finding,
                "linked_issue": item.linked_issue,
                "active": restriction_active(item),
            }
            for item in (restrictions or synthetic_restrictions())
        ]
    )
