"""Champion-challenger comparison with governance-aware recommendation."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ChampionChallengerResult:
    comparison: pd.DataFrame
    recommendation: str
    rationale: str


def compare_champion_challenger(frame: pd.DataFrame) -> ChampionChallengerResult:
    if set(frame["role"]) != {"Champion", "Challenger"}:
        raise ValueError("Comparison requires one champion and one challenger on a common dataset.")
    champion = frame.loc[frame["role"].eq("Champion")].iloc[0]
    challenger = frame.loc[frame["role"].eq("Challenger")].iloc[0]
    if challenger["auc"] > champion["auc"] and challenger["brier_score"] <= champion["brier_score"] and challenger["psi"] <= champion["psi"]:
        rec = "promote challenger"
        rationale = "Challenger improves ranking without weaker calibration or stability."
    elif challenger["auc"] > champion["auc"]:
        rec = "continue parallel run"
        rationale = "Challenger has better AUC but weaker calibration or stability, so highest AUC alone is not enough."
    else:
        rec = "retain champion"
        rationale = "Champion remains stronger after calibration, stability and governance considerations."
    return ChampionChallengerResult(frame.copy(), rec, rationale)
