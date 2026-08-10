from backend.portfolio.portfolio_service import (
    PortfolioService,
)


portfolio_service = PortfolioService()

holdings = {
    "NFLX": 5,
    "PEP": 10,
    "WMT": 8,
    "UNH": 6,
    "DIS": 4,
}

portfolio = (
    portfolio_service
    .create_portfolio_from_shares(
        holdings
    )
)

print()
print("## Portfolio Created From Share Holdings")
print()

print("Share Holdings:")

for symbol, shares in holdings.items():
    print(
        f"{symbol}: {shares} shares"
    )

print()

print("Calculated Portfolio Weights:")

for symbol, weight in portfolio.weights.items():
    print(
        f"{symbol}: {weight:.2%}"
    )

print()

print(
    f"Total Weight: "
    f"{sum(portfolio.weights.values()):.2%}"
)