def finrep_metrics(assets: float, liabilities: float, net_interest_income: float, provisions: float, operating_costs: float) -> dict[str, float]:
    equity = assets - liabilities
    profit = net_interest_income - provisions - operating_costs
    return {
        "assets": assets,
        "liabilities": liabilities,
        "equity": equity,
        "net_interest_income": net_interest_income,
        "provisions": provisions,
        "profit": profit,
    }
