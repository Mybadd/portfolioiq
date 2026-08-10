from backend.models.investor_profile import (
    InvestorProfile,
)

from backend.portfolio.portfolio_service import (
    PortfolioService,
)


portfolio_service = PortfolioService()

investor = InvestorProfile(
    investment_amount=1_000_000,
    investment_horizon_years=7,
    risk_tolerance="MODERATE",
    maximum_acceptable_loss=0.20,
    investment_objective="LONG_TERM_GROWTH",
)

amounts = {
    "NFLX": 200_000,
    "PEP": 250_000,
    "WMT": 200_000,
    "UNH": 150_000,
    "DIS": 200_000,
}

portfolio_service.validate_investment_amount(
    amounts=amounts,
    investor=investor,
)

portfolio = (
    portfolio_service
    .create_portfolio_from_amounts(
        amounts
    )
)

print()
print(
    "## Investor Portfolio Validation"
)
print()

print(
    f"Investor Investment Amount: "
    f"₹{investor.investment_amount:,.2f}"
)

print(
    f"Total Portfolio Allocation: "
    f"₹{sum(amounts.values()):,.2f}"
)

print(
    "Status: VALID"
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