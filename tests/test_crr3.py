from src.risk.crr3 import cva_lite_capital, operational_risk_sma, output_floor


def test_output_floor_binds_when_internal_rwa_too_low():
    result = output_floor(50, 100, 0.725)
    assert result["floor_rwa"] == 72.5
    assert result["binding_rwa"] == 72.5
    assert result["is_floor_binding"] is True


def test_operational_risk_sma_returns_capital_and_rwa():
    result = operational_risk_sma(100, 50, 50, 1.0)
    assert result["business_indicator"] == 200
    assert result["operational_risk_capital"] == 24
    assert result["operational_risk_rwa"] == 300


def test_cva_lite_collateral_reduces_exposure():
    result = cva_lite_capital(1000, 0.02, 0.6, 2, collateral_coverage=0.25)
    assert result["effective_exposure"] == 750
    assert result["cva_lite"] > 0
    assert result["cva_rwa"] == result["cva_capital"] * 12.5
