def calculate_lgd(product_type: str, ltv: float, collateral_discount: float = 0.0) -> float:
    base = {"mortgage": 0.22, "personal loan": 0.58, "credit card": 0.72, "SME loan": 0.48}.get(product_type, 0.5)
    ltv_addon = max(0.0, ltv - 0.75) * 0.45
    return round(min(0.95, max(0.05, base + ltv_addon - collateral_discount)), 4)


def calculate_ead(product_type: str, outstanding_balance: float, loan_amount: float) -> float:
    ccf = {"mortgage": 0.02, "personal loan": 0.08, "credit card": 0.55, "SME loan": 0.25}.get(product_type, 0.1)
    undrawn = max(loan_amount - outstanding_balance, 0)
    return round(outstanding_balance + ccf * undrawn, 2)
