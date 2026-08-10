import pytest

from backend.models.investor_profile import InvestorProfile
from backend.portfolio.portfolio_service import PortfolioService


@pytest.fixture
def portfolio_service():
    return PortfolioService()


@pytest.fixture
def investor():
    return InvestorProfile(
        investment_amount=1_000_000,
        investment_horizon_years=7,
        risk_tolerance="MODERATE",
        maximum_acceptable_loss=0.20,
        investment_objective="LONG_TERM_GROWTH",
    )


def test_create_portfolio(portfolio_service):
    weights = {
        "NFLX": 0.30,
        "PEP": 0.25,
        "WMT": 0.20,
        "UNH": 0.15,
        "DIS": 0.10,
    }

    portfolio = (
        portfolio_service
        .create_portfolio(weights)
    )

    assert portfolio.weights == weights
    assert sum(portfolio.weights.values()) == pytest.approx(1.0)


def test_create_portfolio_from_amounts(
    portfolio_service,
):
    amounts = {
        "NFLX": 200_000,
        "PEP": 250_000,
        "WMT": 200_000,
        "UNH": 150_000,
        "DIS": 200_000,
    }

    portfolio = (
        portfolio_service
        .create_portfolio_from_amounts(
            amounts
        )
    )

    assert portfolio.weights["NFLX"] == pytest.approx(0.20)
    assert portfolio.weights["PEP"] == pytest.approx(0.25)
    assert portfolio.weights["WMT"] == pytest.approx(0.20)
    assert portfolio.weights["UNH"] == pytest.approx(0.15)
    assert portfolio.weights["DIS"] == pytest.approx(0.20)

    assert sum(
        portfolio.weights.values()
    ) == pytest.approx(1.0)


def test_create_portfolio_rejects_empty_weights(
    portfolio_service,
):
    with pytest.raises(ValueError):
        portfolio_service.create_portfolio({})


def test_create_portfolio_rejects_invalid_total_weight(
    portfolio_service,
):
    weights = {
        "NFLX": 0.50,
        "PEP": 0.30,
    }

    with pytest.raises(ValueError):
        portfolio_service.create_portfolio(
            weights
        )


def test_create_portfolio_rejects_negative_weight(
    portfolio_service,
):
    weights = {
        "NFLX": 0.60,
        "PEP": -0.10,
        "WMT": 0.50,
    }

    with pytest.raises(ValueError):
        portfolio_service.create_portfolio(
            weights
        )


def test_create_portfolio_rejects_unsupported_stock(
    portfolio_service,
):
    weights = {
        "NFLX": 0.50,
        "INVALID": 0.50,
    }

    with pytest.raises(ValueError):
        portfolio_service.create_portfolio(
            weights
        )


def test_validate_investment_amount(
    portfolio_service,
    investor,
):
    amounts = {
        "NFLX": 200_000,
        "PEP": 250_000,
        "WMT": 200_000,
        "UNH": 150_000,
        "DIS": 200_000,
    }

    # Should not raise an exception.
    portfolio_service.validate_investment_amount(
        amounts=amounts,
        investor=investor,
    )


def test_validate_investment_amount_rejects_excess(
    portfolio_service,
    investor,
):
    amounts = {
        "NFLX": 200_000,
        "PEP": 250_000,
        "WMT": 200_000,
        "UNH": 150_000,
        "DIS": 300_000,
    }

    with pytest.raises(ValueError):
        portfolio_service.validate_investment_amount(
            amounts=amounts,
            investor=investor,
        )