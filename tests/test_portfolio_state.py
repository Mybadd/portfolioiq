import pytest

from backend.portfolio.portfolio_service import (
    PortfolioService,
)


@pytest.fixture
def portfolio_service():
    return PortfolioService()


def test_create_portfolio_state(
    portfolio_service,
    monkeypatch,
):
    prices = {
        "NFLX": 100.0,
        "PEP": 200.0,
        "WMT": 50.0,
    }

    def mock_get_current_price(symbol):
        return prices[symbol]

    monkeypatch.setattr(
        portfolio_service.market_data_service,
        "get_current_price",
        mock_get_current_price,
    )

    holdings = {
        "nflx": 10,
        "PEP": 5,
        "WMT": 20,
    }

    portfolio_state = (
        portfolio_service.create_portfolio_state(
            holdings
        )
    )

    assert portfolio_state.holdings == {
        "NFLX": 10.0,
        "PEP": 5.0,
        "WMT": 20.0,
    }

    assert portfolio_state.latest_prices == {
        "NFLX": 100.0,
        "PEP": 200.0,
        "WMT": 50.0,
    }

    assert portfolio_state.position_values == {
        "NFLX": 1000.0,
        "PEP": 1000.0,
        "WMT": 1000.0,
    }

    assert (
        portfolio_state.total_portfolio_value
        == pytest.approx(3000.0)
    )

    assert (
        portfolio_state.weights["NFLX"]
        == pytest.approx(1 / 3)
    )

    assert (
        portfolio_state.weights["PEP"]
        == pytest.approx(1 / 3)
    )

    assert (
        portfolio_state.weights["WMT"]
        == pytest.approx(1 / 3)
    )

    assert sum(
        portfolio_state.weights.values()
    ) == pytest.approx(1.0)


def test_create_portfolio_state_rejects_empty_holdings(
    portfolio_service,
):
    with pytest.raises(ValueError):
        portfolio_service.create_portfolio_state({})


def test_create_portfolio_state_rejects_zero_shares(
    portfolio_service,
):
    holdings = {
        "NFLX": 0,
    }

    with pytest.raises(ValueError):
        portfolio_service.create_portfolio_state(
            holdings
        )


def test_create_portfolio_state_rejects_negative_shares(
    portfolio_service,
):
    holdings = {
        "NFLX": -10,
    }

    with pytest.raises(ValueError):
        portfolio_service.create_portfolio_state(
            holdings
        )


def test_create_portfolio_state_rejects_non_numeric_shares(
    portfolio_service,
):
    holdings = {
        "NFLX": "ten",
    }

    with pytest.raises(TypeError):
        portfolio_service.create_portfolio_state(
            holdings
        )


def test_create_portfolio_state_rejects_unsupported_stock(
    portfolio_service,
):
    holdings = {
        "INVALID": 10,
    }

    with pytest.raises(ValueError):
        portfolio_service.create_portfolio_state(
            holdings
        )


def test_create_portfolio_state_rejects_invalid_price(
    portfolio_service,
    monkeypatch,
):
    def mock_get_current_price(symbol):
        return None

    monkeypatch.setattr(
        portfolio_service.market_data_service,
        "get_current_price",
        mock_get_current_price,
    )

    holdings = {
        "NFLX": 10,
    }

    with pytest.raises(ValueError):
        portfolio_service.create_portfolio_state(
            holdings
        )