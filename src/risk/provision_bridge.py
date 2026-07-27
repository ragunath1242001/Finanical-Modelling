"""Provision movement bridge with reconciliation."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.risk.validation import RiskValidationError


@dataclass(frozen=True)
class ProvisionBridgeInput:
    opening_allowance: float
    new_originations: float = 0.0
    repayments: float = 0.0
    derecognitions: float = 0.0
    stage1_to_stage2: float = 0.0
    stage2_to_stage3: float = 0.0
    cures: float = 0.0
    parameter_changes: float = 0.0
    scenario_changes: float = 0.0
    write_offs: float = 0.0
    recoveries: float = 0.0
    other_adjustments: float = 0.0


@dataclass(frozen=True)
class ProvisionBridgeResult:
    closing_allowance: float
    table: pd.DataFrame
    reconciles: bool
    steps: tuple[str, ...]


def provision_movement_bridge(inputs: ProvisionBridgeInput, tolerance: float = 1e-6) -> ProvisionBridgeResult:
    movements = [
        ("Opening allowance", inputs.opening_allowance),
        ("New originations", inputs.new_originations),
        ("Repayments", -inputs.repayments),
        ("Derecognitions", -inputs.derecognitions),
        ("Stage 1 to Stage 2 transfers", inputs.stage1_to_stage2),
        ("Stage 2 to Stage 3 transfers", inputs.stage2_to_stage3),
        ("Cures", -inputs.cures),
        ("Parameter changes", inputs.parameter_changes),
        ("Scenario changes", inputs.scenario_changes),
        ("Write-offs", -inputs.write_offs),
        ("Recoveries", -inputs.recoveries),
        ("Other adjustments", inputs.other_adjustments),
    ]
    closing = sum(amount for _, amount in movements)
    table = pd.DataFrame([{"component": name, "amount": amount} for name, amount in movements] + [{"component": "Closing allowance", "amount": closing}])
    expected = inputs.opening_allowance + sum(amount for _, amount in movements[1:])
    reconciles = abs(closing - expected) <= tolerance
    if not reconciles:
        raise RiskValidationError("Provision bridge does not reconcile.")
    return ProvisionBridgeResult(closing, table, reconciles, ("Closing allowance = opening allowance + increases - decreases.",))
