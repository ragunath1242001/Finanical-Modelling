"""Exposure-at-default engine."""

from __future__ import annotations

from dataclasses import dataclass

from src.risk.validation import RiskValidationError, validate_equal_lengths, validate_non_negative, validate_probability


@dataclass(frozen=True)
class EADResult:
    base_ead: float
    stressed_ead: float
    steps: tuple[str, ...]


def term_loan_ead(outstanding_balance: float) -> EADResult:
    balance = validate_non_negative(outstanding_balance, "Outstanding balance")
    return EADResult(balance, balance, (f"Term loan EAD = outstanding balance = {balance:,.2f}",))


def revolving_ead(drawn_amount: float, undrawn_commitment: float, ccf: float) -> EADResult:
    drawn = validate_non_negative(drawn_amount, "Drawn amount")
    undrawn = validate_non_negative(undrawn_commitment, "Undrawn commitment")
    ccf = validate_probability(ccf, "CCF")
    ead = drawn + ccf * undrawn
    if ead < drawn:
        raise RiskValidationError("EAD cannot be below drawn amount.")
    return EADResult(ead, ead, (f"Revolving EAD = drawn {drawn:,.2f} + CCF {ccf:.4f} x undrawn {undrawn:,.2f} = {ead:,.2f}",))


def amortising_ead_schedule(
    opening_balance: float,
    contractual_repayments: list[float],
    additional_drawings: list[float] | None = None,
    prepayments: list[float] | None = None,
    interest_capitalisation: list[float] | None = None,
) -> list[float]:
    opening = validate_non_negative(opening_balance, "Opening balance")
    additional_drawings = additional_drawings or [0.0] * len(contractual_repayments)
    prepayments = prepayments or [0.0] * len(contractual_repayments)
    interest_capitalisation = interest_capitalisation or [0.0] * len(contractual_repayments)
    validate_equal_lengths(
        {
            "contractual_repayments": contractual_repayments,
            "additional_drawings": additional_drawings,
            "prepayments": prepayments,
            "interest_capitalisation": interest_capitalisation,
        }
    )
    balance = opening
    schedule = []
    for repayment, drawing, prepayment, interest in zip(contractual_repayments, additional_drawings, prepayments, interest_capitalisation):
        repayment = validate_non_negative(repayment, "Contractual repayment")
        drawing = validate_non_negative(drawing, "Additional drawing")
        prepayment = validate_non_negative(prepayment, "Prepayment")
        interest = validate_non_negative(interest, "Interest capitalisation")
        balance = max(balance + drawing + interest - repayment - prepayment, 0.0)
        schedule.append(balance)
    return schedule


def scenario_adjusted_ead(base_ead: float, multiplier: float) -> EADResult:
    base = validate_non_negative(base_ead, "Base EAD")
    validate_non_negative(multiplier, "EAD multiplier")
    stressed = base * float(multiplier)
    return EADResult(base, stressed, (f"Scenario EAD = base EAD {base:,.2f} x multiplier {float(multiplier):.4f} = {stressed:,.2f}",))
