def rwa(exposure: float, risk_weight: float) -> float:
    return float(exposure) * float(risk_weight)


def capital_ratios(cet1: float, at1: float, tier2: float, rwa_amount: float) -> dict[str, float]:
    if rwa_amount <= 0:
        raise ValueError("RWA must be positive")
    return {
        "cet1_ratio": cet1 / rwa_amount,
        "tier1_ratio": (cet1 + at1) / rwa_amount,
        "total_capital_ratio": (cet1 + at1 + tier2) / rwa_amount,
    }


def capital_after_provision(cet1: float, provision_shock: float) -> float:
    return max(0.0, cet1 - max(0.0, provision_shock))
