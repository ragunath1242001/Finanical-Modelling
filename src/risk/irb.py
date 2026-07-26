from src.risk.basel import rwa


def standardized_rwa(exposure: float, risk_weight: float) -> float:
    return rwa(exposure, risk_weight)


def simplified_irb_capital(pd: float, lgd: float, ead: float, maturity_adjustment: float = 1.0) -> float:
    unexpected_loss_factor = 1.06
    return pd**0.5 * lgd * ead * unexpected_loss_factor * maturity_adjustment


def irb_rwa_equivalent(capital: float) -> float:
    return capital * 12.5
