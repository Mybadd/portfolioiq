from backend.portfolio.portfolio_service import PortfolioService
from backend.risk.risk_service import RiskService


portfolio_service = PortfolioService()
risk_service = RiskService()

portfolio = portfolio_service.create_portfolio(
    {
        "GOOGL": 0.30,
        "META": 0.25,
        "TSLA": 0.20,
        "V": 0.15,
        "COST": 0.10,
    }
)

portfolio_returns = (
    portfolio_service.calculate_portfolio_returns(
        portfolio
    )
)

volatility = risk_service.calculate_volatility(
    portfolio_returns
)

maximum_drawdown = (
    risk_service.calculate_maximum_drawdown(
        portfolio_returns
    )
)
sharpe_ratio = risk_service.calculate_sharpe_ratio(
    portfolio_returns,
    risk_free_rate=0.05,
)

historical_value_at_risk = (
    risk_service.calculate_historical_value_at_risk(
        portfolio_returns,
        confidence_level=0.95,
    )
)
expected_shortfall = (
    risk_service.calculate_expected_shortfall(
        portfolio_returns,
        confidence_level=0.95,
    )
)

print(
    f"Expected Shortfall (95%): "
    f"{expected_shortfall:.2%}"
)
print(
    f"Historical Value at Risk (95%): "
    f"{historical_value_at_risk:.2%}"
)
print(
    f"Sharpe Ratio: "
    f"{sharpe_ratio:.4f}"
)

print()
print(
    f"Annualized volatility: "
    f"{volatility:.2%}"
)

print(
    f"Maximum drawdown: "
    f"{maximum_drawdown:.2%}"
)