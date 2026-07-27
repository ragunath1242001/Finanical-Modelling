"""Data ownership catalogue for material risk data elements."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class DataElementOwnership:
    data_element: str
    definition: str
    owner: str
    steward: str
    source_system: str
    quality_controls: list[str]
    downstream_use: list[str]


OWNERSHIP_CATALOGUE = [
    DataElementOwnership("customer_id", "Synthetic customer join key.", "Business Owner", "1LOD Data Steward", "Customer Master", ["DQ-002", "DQ-003"], ["Lineage", "risk aggregation", "reporting"]),
    DataElementOwnership("income", "Annual borrower income used as an affordability and PD signal.", "Lending Business Owner", "1LOD Data Steward", "Loan Origination System", ["DQ-001"], ["PD model", "IFRS 9 ECL", "stress testing"]),
    DataElementOwnership("pd", "Probability of default used in ECL, IRB and stress testing.", "Model Owner", "Model Risk Steward", "Credit Risk Data Mart", ["DQ-004", "DQ-008"], ["ECL", "IRB", "COREP-style report"]),
    DataElementOwnership("lgd", "Loss given default used in expected loss and capital analysis.", "Model Owner", "Model Risk Steward", "Collateral/Risk Data Mart", ["DQ-005", "DQ-010"], ["ECL", "IRB"]),
    DataElementOwnership("ead", "Exposure at default used in ECL and capital reporting.", "Risk Data Owner", "Risk Data Steward", "Credit Risk Data Mart", ["DQ-006", "DQ-014"], ["ECL", "COREP", "FINREP"]),
    DataElementOwnership("ifrs9_stage", "Educational IFRS 9 stage 1, 2 or 3.", "Finance/Risk Owner", "IFRS 9 Steward", "IFRS 9 ECL Engine", ["DQ-012"], ["FINREP provisions", "CET1 bridge"]),
]


def ownership_catalogue_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "data_element": item.data_element,
                "definition": item.definition,
                "owner": item.owner,
                "steward": item.steward,
                "source_system": item.source_system,
                "quality_controls": ", ".join(item.quality_controls),
                "downstream_use": ", ".join(item.downstream_use),
            }
            for item in OWNERSHIP_CATALOGUE
        ]
    )
