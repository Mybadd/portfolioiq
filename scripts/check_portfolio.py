from backend.portfolio.portfolio_service import PortfolioService


service = PortfolioService()

portfolio = service.create_portfolio(
    {
        "AAPL": 0.30,
        "MSFT": 0.25,
        "NVDA": 0.20,
        "AMZN": 0.15,
        "JPM": 0.10,
    }
)

portfolio_returns = service.calculate_portfolio_returns(
    portfolio
)

print()
print("Portfolio:")
print(portfolio)

print()
print("Portfolio returns:")
print(portfolio_returns.head())

print()
print("Number of trading days:")
print(len(portfolio_returns))

print()
print("Missing values:")
print(portfolio_returns.isnull().sum())