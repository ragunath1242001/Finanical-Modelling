def leverage_ratio(tier1_capital: float, total_exposure: float) -> float:
    return tier1_capital / total_exposure


def lcr(hqla: float, net_cash_outflows_30d: float) -> float:
    return hqla / net_cash_outflows_30d


def nsfr(available_stable_funding: float, required_stable_funding: float) -> float:
    return available_stable_funding / required_stable_funding


def compliance(value: float, threshold: float) -> str:
    return "Compliant" if value >= threshold else "Action required"
