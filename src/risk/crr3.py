from __future__ import annotations


def output_floor(internal_model_rwa: float, standardized_rwa: float, floor_rate: float = 0.55) -> dict[str, float]:
    floor_rwa = standardized_rwa * floor_rate
    binding_rwa = max(internal_model_rwa, floor_rwa)
    return {
        "internal_model_rwa": internal_model_rwa,
        "standardized_rwa": standardized_rwa,
        "floor_rate": floor_rate,
        "floor_rwa": floor_rwa,
        "binding_rwa": binding_rwa,
        "rwa_add_on": max(0.0, binding_rwa - internal_model_rwa),
        "is_floor_binding": binding_rwa > internal_model_rwa,
    }


def operational_risk_sma(
    interest_component: float,
    services_component: float,
    financial_component: float,
    internal_loss_multiplier: float = 1.0,
) -> dict[str, float]:
    business_indicator = max(0.0, interest_component) + max(0.0, services_component) + max(0.0, financial_component)
    marginal_coefficient = 0.12 if business_indicator <= 1_000_000_000 else 0.15
    capital_requirement = business_indicator * marginal_coefficient * internal_loss_multiplier
    return {
        "business_indicator": business_indicator,
        "marginal_coefficient": marginal_coefficient,
        "internal_loss_multiplier": internal_loss_multiplier,
        "operational_risk_capital": capital_requirement,
        "operational_risk_rwa": capital_requirement * 12.5,
    }


def cva_lite_capital(
    expected_positive_exposure: float,
    counterparty_pd: float,
    loss_given_default: float,
    maturity_years: float,
    discount_factor: float = 0.97,
    collateral_coverage: float = 0.0,
) -> dict[str, float]:
    effective_exposure = expected_positive_exposure * max(0.0, 1 - collateral_coverage)
    cva = effective_exposure * counterparty_pd * loss_given_default * maturity_years * discount_factor
    capital = cva * 1.5
    return {
        "effective_exposure": effective_exposure,
        "cva_lite": cva,
        "cva_capital": capital,
        "cva_rwa": capital * 12.5,
    }


def crr3_total_rwa(
    credit_rwa: float,
    market_rwa: float,
    cva_rwa: float,
    operational_rwa: float,
    internal_model_rwa: float,
    standardized_rwa: float,
    floor_rate: float,
) -> dict[str, float]:
    floor = output_floor(internal_model_rwa, standardized_rwa, floor_rate)
    total = floor["binding_rwa"] + market_rwa + cva_rwa + operational_rwa
    return {
        **floor,
        "credit_rwa_before_floor": credit_rwa,
        "market_rwa": market_rwa,
        "cva_rwa": cva_rwa,
        "operational_rwa": operational_rwa,
        "total_rwa": total,
    }
