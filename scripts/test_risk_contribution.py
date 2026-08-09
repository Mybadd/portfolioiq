from backend.portfolio.portfolio_service import PortfolioService
from backend.risk.risk_service import RiskService


portfolio_service = PortfolioService()
risk_service = RiskService()

portfolio = portfolio_service.create_portfolio(
    {
        "NFLX": 0.30,
        "PEP": 0.25,
        "WMT": 0.20,
        "UNH": 0.15,
        "DIS": 0.10,
    }
)

print()
print("Portfolio:")
print(portfolio)

# Retrieve historical market data
price_data = portfolio_service.portfolio_data_service.get_price_data(
    list(portfolio.weights.keys())
)

# Combine closing prices
combined_prices = (
    portfolio_service.portfolio_data_service.combine_price_data(
        price_data
    )
)

# Calculate individual asset returns
asset_returns = (
    portfolio_service.portfolio_data_service.calculate_returns(
        combined_prices
    )
)

# Calculate risk contribution
risk_contribution = (
    risk_service.calculate_risk_contribution(
        asset_returns,
        portfolio.weights,
    )
)

print()
print("Risk Contribution")
print("-----------------")

for symbol, contribution in risk_contribution.items():
    print(
        f"{symbol}: "
        f"{contribution:.2%}"
    )

print()
print(
    f"Total Risk Contribution: "
    f"{risk_contribution.sum():.2%}"
)