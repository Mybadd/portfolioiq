from backend.portfolio.portfolio_data_service import (
    PortfolioDataService,
)
from backend.portfolio.portfolio_optimizer import (
    PortfolioOptimizer,
)


symbols = [
    "NFLX",
    "PEP",
    "WMT",
    "UNH",
    "DIS",
]

data_service = PortfolioDataService()

price_data = data_service.get_price_data(
    symbols
)

prices = data_service.combine_price_data(
    price_data
)

returns = data_service.calculate_returns(
    prices
)

optimizer = PortfolioOptimizer()

feasible = optimizer.check_feasibility(
    asset_returns=returns,
    maximum_acceptable_loss=0.20,
    target_volatility=0.20,
    maximum_weight=0.30,
)

print()
print("## Investor Constraint Feasibility")
print()

if feasible:
    print(
        "Constraints can be satisfied "
        "with the available assets."
    )
else:
    print(
        "Constraints cannot be satisfied "
        "with the available assets."
    )

    print()
    print("Suggested Actions:")
    print(
        "- Expand the asset universe."
    )
    print(
        "- Consider adding lower-risk assets."
    )
    print(
        "- Consider allocating part of the portfolio "
        "to cash or fixed-income assets."
    )