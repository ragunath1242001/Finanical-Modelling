"""Simplified educational CET1 capital bridge."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.risk.validation import RiskValidationError, validate_probability


@dataclass(frozen=True)
class CapitalBridgeInput:
    opening_cet1: float
    profit_before_impairment: float = 0.0
    incremental_impairment: float = 0.0
    tax_rate: float = 0.0
    dividends: float = 0.0
    regulatory_adjustments: float = 0.0
    other_capital_movements: float = 0.0


@dataclass(frozen=True)
class CapitalBridgeResult:
    closing_cet1: float
    after_tax_impairment_impact: float
    table: pd.DataFrame
    reconciles: bool
    assumptions: tuple[str, ...]
    warnings: tuple[str, ...]


def capital_movement_bridge(inputs: CapitalBridgeInput, tolerance: float = 1e-6) -> CapitalBridgeResult:
    tax_rate = validate_probability(inputs.tax_rate, "Tax rate")
    after_tax_impairment = inputs.incremental_impairment * (1 - tax_rate)
    movements = [
        ("Opening CET1", inputs.opening_cet1),
        ("Profit before impairment", inputs.profit_before_impairment),
        ("After-tax impairment impact", -after_tax_impairment),
        ("Dividends", -inputs.dividends),
        ("Regulatory adjustments", inputs.regulatory_adjustments),
        ("Other capital movements", inputs.other_capital_movements),
    ]
    closing = sum(amount for _, amount in movements)
    table = pd.DataFrame([{"component": name, "amount": amount} for name, amount in movements] + [{"component": "Closing CET1", "amount": closing}])
    expected = inputs.opening_cet1 + sum(amount for _, amount in movements[1:])
    reconciles = abs(closing - expected) <= tolerance
    if not reconciles:
        raise RiskValidationError("Capital bridge does not reconcile.")
    return CapitalBridgeResult(
        closing_cet1=closing,
        after_tax_impairment_impact=after_tax_impairment,
        table=table,
        reconciles=reconciles,
        assumptions=("Simplified educational CET1 impact.", "After-tax impairment impact = incremental impairment x (1 - tax rate)."),
        warnings=("This is not a regulatory capital calculation engine.",),
    )
