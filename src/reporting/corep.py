from src.risk.basel import capital_ratios
from src.risk.liquidity import leverage_ratio


def corep_metrics(cet1: float, at1: float, tier2: float, rwa_amount: float, total_exposure: float) -> dict[str, float | str]:
    ratios = capital_ratios(cet1, at1, tier2, rwa_amount)
    ratios["leverage_ratio"] = leverage_ratio(cet1 + at1, total_exposure)
    ratios["capital_adequacy_status"] = "Compliant" if ratios["cet1_ratio"] >= 0.045 and ratios["total_capital_ratio"] >= 0.08 else "Action required"
    return ratios
