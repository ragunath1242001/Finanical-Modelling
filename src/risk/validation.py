"""Domain validation helpers for educational risk engines."""

from __future__ import annotations


class RiskValidationError(ValueError):
    """Raised when a risk-engine input fails domain validation."""


def validate_probability(value: float, name: str) -> float:
    value = float(value)
    if not 0 <= value <= 1:
        raise RiskValidationError(f"{name} must be between 0 and 1.")
    return value


def validate_non_negative(value: float, name: str) -> float:
    value = float(value)
    if value < 0:
        raise RiskValidationError(f"{name} must be non-negative.")
    return value


def validate_positive(value: float, name: str) -> float:
    value = float(value)
    if value <= 0:
        raise RiskValidationError(f"{name} must be greater than zero.")
    return value


def validate_rate(value: float, name: str, lower: float = -1.0) -> float:
    value = float(value)
    if value < lower:
        raise RiskValidationError(f"{name} must be at least {lower}.")
    return value


def validate_equal_lengths(name_to_values: dict[str, list[float]]) -> int:
    lengths = {name: len(values) for name, values in name_to_values.items()}
    if not lengths:
        raise RiskValidationError("At least one term structure is required.")
    unique_lengths = set(lengths.values())
    if len(unique_lengths) != 1:
        raise RiskValidationError(f"Term structures must have equal lengths: {lengths}.")
    length = unique_lengths.pop()
    if length == 0:
        raise RiskValidationError("Term structures must contain at least one period.")
    return length


def validate_weights(weights: list[float], tolerance: float = 1e-6) -> None:
    for weight in weights:
        validate_probability(weight, "Scenario probability")
    if abs(sum(weights) - 1.0) > tolerance:
        raise RiskValidationError("Scenario weights must total 1.")
