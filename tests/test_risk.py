import numpy as np
import pandas as pd
import pytest

from backend.risk.risk_service import RiskService
from backend.models.portfolio import Portfolio
from backend.models.stress_test import StressScenario


@pytest.fixture
def risk_service():
    return RiskService()


@pytest.fixture
def portfolio_returns():
    return pd.Series(
        [
            0.01,
            -0.005,
            0.02,
            -0.01,
            0.015,
            -0.02,
            0.005,
            0.01,
            -0.005,
            0.02,
        ]
    )


def test_calculate_volatility(
    risk_service,
    portfolio_returns,
):
    volatility = (
        risk_service.calculate_volatility(
            portfolio_returns
        )
    )

    assert isinstance(volatility, float)
    assert volatility > 0


def test_calculate_volatility_rejects_empty_series(
    risk_service,
):
    returns = pd.Series(dtype=float)

    with pytest.raises(ValueError):
        risk_service.calculate_volatility(
            returns
        )


def test_calculate_maximum_drawdown(
    risk_service,
    portfolio_returns,
):
    maximum_drawdown = (
        risk_service.calculate_maximum_drawdown(
            portfolio_returns
        )
    )

    assert isinstance(maximum_drawdown, float)
    assert maximum_drawdown <= 0


def test_calculate_maximum_drawdown_rejects_empty_series(
    risk_service,
):
    returns = pd.Series(dtype=float)

    with pytest.raises(ValueError):
        risk_service.calculate_maximum_drawdown(
            returns
        )


def test_calculate_sharpe_ratio(
    risk_service,
    portfolio_returns,
):
    sharpe_ratio = (
        risk_service.calculate_sharpe_ratio(
            portfolio_returns
        )
    )

    assert isinstance(sharpe_ratio, float)
    assert np.isfinite(sharpe_ratio)


def test_calculate_sharpe_ratio_rejects_empty_series(
    risk_service,
):
    returns = pd.Series(dtype=float)

    with pytest.raises(ValueError):
        risk_service.calculate_sharpe_ratio(
            returns
        )


def test_calculate_sharpe_ratio_rejects_negative_risk_free_rate(
    risk_service,
    portfolio_returns,
):
    with pytest.raises(ValueError):
        risk_service.calculate_sharpe_ratio(
            portfolio_returns,
            risk_free_rate=-0.01,
        )


def test_calculate_historical_var(
    risk_service,
    portfolio_returns,
):
    value_at_risk = (
        risk_service.calculate_historical_value_at_risk(
            portfolio_returns
        )
    )

    assert isinstance(value_at_risk, float)
    assert value_at_risk <= 0


def test_calculate_historical_var_rejects_invalid_confidence(
    risk_service,
    portfolio_returns,
):
    with pytest.raises(ValueError):
        risk_service.calculate_historical_value_at_risk(
            portfolio_returns,
            confidence_level=1.5,
        )


def test_calculate_expected_shortfall(
    risk_service,
    portfolio_returns,
):
    expected_shortfall = (
        risk_service.calculate_expected_shortfall(
            portfolio_returns
        )
    )

    assert isinstance(expected_shortfall, float)
    assert expected_shortfall <= 0


def test_calculate_expected_shortfall_rejects_invalid_confidence(
    risk_service,
    portfolio_returns,
):
    with pytest.raises(ValueError):
        risk_service.calculate_expected_shortfall(
            portfolio_returns,
            confidence_level=0,
        )


def test_calculate_risk_contribution(
    risk_service,
):
    asset_returns = pd.DataFrame(
        {
            "NFLX": [
                0.01,
                -0.005,
                0.02,
                -0.01,
                0.015,
            ],
            "PEP": [
                0.005,
                0.002,
                -0.003,
                0.004,
                0.006,
            ],
        }
    )

    weights = {
        "NFLX": 0.60,
        "PEP": 0.40,
    }

    risk_contribution = (
        risk_service.calculate_risk_contribution(
            asset_returns=asset_returns,
            weights=weights,
        )
    )

    assert isinstance(
        risk_contribution,
        pd.Series,
    )

    assert set(
        risk_contribution.index
    ) == {"NFLX", "PEP"}

    assert sum(
        risk_contribution
    ) == pytest.approx(1.0)


def test_calculate_risk_contribution_rejects_empty_data(
    risk_service,
):
    asset_returns = pd.DataFrame()

    weights = {
        "NFLX": 1.0,
    }

    with pytest.raises(ValueError):
        risk_service.calculate_risk_contribution(
            asset_returns=asset_returns,
            weights=weights,
        )


def test_calculate_risk_contribution_rejects_missing_symbol(
    risk_service,
):
    asset_returns = pd.DataFrame(
        {
            "NFLX": [
                0.01,
                0.02,
                -0.01,
            ]
        }
    )

    weights = {
        "NFLX": 0.50,
        "PEP": 0.50,
    }

    with pytest.raises(ValueError):
        risk_service.calculate_risk_contribution(
            asset_returns=asset_returns,
            weights=weights,
        )


def test_calculate_stress_test(
    risk_service,
):
    portfolio = Portfolio(
        weights={
            "NFLX": 0.60,
            "PEP": 0.40,
        }
    )

    scenario = StressScenario(
        name="Market Crash",
        asset_shocks={
            "NFLX": -0.20,
            "PEP": -0.10,
        },
    )

    impact = risk_service.calculate_stress_test(
        portfolio=portfolio,
        scenario=scenario,
    )

    expected_impact = (
        0.60 * -0.20
        + 0.40 * -0.10
    )

    assert impact == pytest.approx(
        expected_impact
    )