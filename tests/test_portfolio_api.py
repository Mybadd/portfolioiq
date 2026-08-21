import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.api.portfolio_routes import portfolio_service


client = TestClient(app)


@pytest.fixture
def mock_prices(monkeypatch):
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


def test_create_portfolio_state_api_success(
    mock_prices,
):
    response = client.post(
        "/api/portfolio/state",
        json={
            "holdings": {
                "nflx": 10,
                "PEP": 5,
                "WMT": 20,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["holdings"] == {
        "NFLX": 10.0,
        "PEP": 5.0,
        "WMT": 20.0,
    }

    assert data["latest_prices"] == {
        "NFLX": 100.0,
        "PEP": 200.0,
        "WMT": 50.0,
    }

    assert data["position_values"] == {
        "NFLX": 1000.0,
        "PEP": 1000.0,
        "WMT": 1000.0,
    }

    assert (
        data["total_portfolio_value"]
        == pytest.approx(3000.0)
    )

    assert data["asset_count"] == 3

    assert sum(
        data["weights"].values()
    ) == pytest.approx(1.0)


def test_create_portfolio_state_api_rejects_empty_holdings():
    response = client.post(
        "/api/portfolio/state",
        json={
            "holdings": {}
        },
    )

    assert response.status_code == 400


def test_create_portfolio_state_api_rejects_invalid_shares():
    response = client.post(
        "/api/portfolio/state",
        json={
            "holdings": {
                "NFLX": -10
            }
        },
    )

    assert response.status_code == 400


def test_create_portfolio_state_api_rejects_unsupported_stock():
    response = client.post(
        "/api/portfolio/state",
        json={
            "holdings": {
                "INVALID": 10
            }
        },
    )

    assert response.status_code == 400


def test_create_portfolio_state_api_returns_required_fields(
    mock_prices,
):
    response = client.post(
        "/api/portfolio/state",
        json={
            "holdings": {
                "NFLX": 10,
                "PEP": 5,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    required_fields = {
        "holdings",
        "latest_prices",
        "position_values",
        "total_portfolio_value",
        "weights",
        "asset_count",
    }

    assert required_fields.issubset(
        data.keys()
    )