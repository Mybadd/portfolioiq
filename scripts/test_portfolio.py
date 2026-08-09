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

print("Portfolio created successfully.")
print(portfolio)