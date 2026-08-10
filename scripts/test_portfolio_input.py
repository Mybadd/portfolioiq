from backend.portfolio.portfolio_service import PortfolioService


portfolio_service = PortfolioService()

amounts = {
    "NFLX": 200_000,
    "PEP": 250_000,
    "WMT": 200_000,
    "UNH": 150_000,
    "DIS": 200_000,
}

portfolio = (
    portfolio_service
    .create_portfolio_from_amounts(amounts)
)

print()
print("## Portfolio Created From Investment Amounts")
print()

print(
    "Total Investment: "
    f"₹{sum(amounts.values()):,.2f}"
)

print()

for symbol, weight in portfolio.weights.items():
    print(
        f"{symbol}: {weight:.2%}"
    )

print()

print(
    f"Total Weight: "
    f"{sum(portfolio.weights.values()):.2%}"
)