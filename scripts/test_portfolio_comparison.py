from backend.portfolio.portfolio_data_service import (
    PortfolioDataService,
)
from backend.services.portfolio_comparison_service import (
    PortfolioComparisonService,
)


symbols = [
    "NFLX",
    "PEP",
    "WMT",
    "UNH",
    "DIS",
]

before_weights = {
    "NFLX": 0.30,
    "PEP": 0.25,
    "WMT": 0.20,
    "UNH": 0.15,
    "DIS": 0.10,
}

after_weights = {
    "NFLX": 0.2577,
    "PEP": 0.1635,
    "WMT": 0.30,
    "UNH": 0.2433,
    "DIS": 0.0355,
}


data_service = PortfolioDataService()

price_data = data_service.get_price_data(
    symbols
)

combined_prices = (
    data_service.combine_price_data(
        price_data
    )
)

asset_returns = (
    data_service.calculate_returns(
        combined_prices
    )
)


comparison_service = (
    PortfolioComparisonService()
)

comparison = comparison_service.compare(
    asset_returns=asset_returns,
    before_weights=before_weights,
    after_weights=after_weights,
)


print()
print("Portfolio Comparison")
print("====================")

print(
    f"Volatility: "
    f"{comparison.before_volatility:.2%}"
    f" -> "
    f"{comparison.after_volatility:.2%}"
)

print(
    f"Maximum Drawdown: "
    f"{comparison.before_drawdown:.2%}"
    f" -> "
    f"{comparison.after_drawdown:.2%}"
)

print(
    f"Sharpe Ratio: "
    f"{comparison.before_sharpe:.4f}"
    f" -> "
    f"{comparison.after_sharpe:.4f}"
)

print(
    f"Historical VaR: "
    f"{comparison.before_var:.2%}"
    f" -> "
    f"{comparison.after_var:.2%}"
)

print(
    f"Expected Shortfall: "
    f"{comparison.before_expected_shortfall:.2%}"
    f" -> "
    f"{comparison.after_expected_shortfall:.2%}"
)

print(
    f"Risk Score: "
    f"{comparison.before_risk_score:.2f}"
    f" -> "
    f"{comparison.after_risk_score:.2f}"
)