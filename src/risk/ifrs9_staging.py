"""Educational IFRS 9 staging rules with explicit rule triggers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from src.risk.validation import validate_non_negative


class IFRS9Stage(IntEnum):
    STAGE_1 = 1
    STAGE_2 = 2
    STAGE_3 = 3


@dataclass(frozen=True)
class StagingRequest:
    days_past_due: int = 0
    default_flag: bool = False
    unlikely_to_pay: bool = False
    watchlist: bool = False
    forbearance: bool = False
    rating_deterioration_notches: int = 0
    pd_increase_since_origination: float = 0.0
    sector_stress: str = "normal"
    manual_override_stage: int | None = None
    manual_override_reason: str | None = None


@dataclass(frozen=True)
class StagingResult:
    stage: IFRS9Stage
    triggered_rules: tuple[str, ...]
    rule_priority: tuple[str, ...]
    explanation: str
    warnings: tuple[str, ...]
    override_details: str | None = None


DISCLAIMER = "Staging rules are educational and institution-specific IFRS 9 policies may differ."


def assign_ifrs9_stage(request: StagingRequest) -> StagingResult:
    validate_non_negative(request.days_past_due, "Days past due")
    warnings = (DISCLAIMER,)
    priority = ("Stage 3 credit-impaired indicators", "Stage 2 significant increase in credit risk", "Stage 1 performing")

    if request.manual_override_stage is not None:
        if request.manual_override_stage not in {1, 2, 3}:
            raise ValueError("Manual override stage must be 1, 2 or 3.")
        return StagingResult(
            IFRS9Stage(request.manual_override_stage),
            ("Manual override",),
            priority,
            f"Manual override assigned Stage {request.manual_override_stage}.",
            warnings,
            request.manual_override_reason,
        )

    stage3_rules = []
    if request.default_flag:
        stage3_rules.append("Default flag")
    if request.unlikely_to_pay:
        stage3_rules.append("Unlikely-to-pay indicator")
    if request.days_past_due >= 90:
        stage3_rules.append("90+ days past due")
    if stage3_rules:
        return StagingResult(IFRS9Stage.STAGE_3, tuple(stage3_rules), priority, "Stage 3 assigned because credit-impaired/default indicators take precedence.", warnings)

    stage2_rules = []
    if request.days_past_due >= 30:
        stage2_rules.append("30+ days past due")
    if request.watchlist:
        stage2_rules.append("Watchlist")
    if request.forbearance:
        stage2_rules.append("Forbearance")
    if request.rating_deterioration_notches >= 2:
        stage2_rules.append("Rating deterioration")
    if request.pd_increase_since_origination >= 2.0:
        stage2_rules.append("PD has doubled since origination")
    if request.sector_stress.lower() in {"high", "severe"}:
        stage2_rules.append("High or severe sector stress")
    if stage2_rules:
        return StagingResult(IFRS9Stage.STAGE_2, tuple(stage2_rules), priority, "Stage 2 assigned because significant increase in credit risk indicators are present.", warnings)

    return StagingResult(IFRS9Stage.STAGE_1, ("No SICR or default trigger",), priority, "Stage 1 assigned because no significant deterioration or default trigger is present.", warnings)
