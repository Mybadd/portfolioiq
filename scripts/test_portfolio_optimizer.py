from backend.portfolio.portfolio_data_service import (
    PortfolioDataService,
)
from backend.portfolio.portfolio_optimizer import (
    PortfolioOptimizer,
)
from backend.models.investor_profile import InvestorProfile
from backend.portfolio.investor_optimizer import InvestorOptimizer
import numpy as np

investor = InvestorProfile(
    investment_amount=1_000_000,
    investment_horizon_years=7,
    risk_tolerance="MODERATE",
    maximum_acceptable_loss=0.20,
    investment_objective="LONG_TERM_GROWTH",
)

investor_optimizer = InvestorOptimizer()

target_volatility = (
    investor_optimizer.get_target_volatility(
        investor
    )
)
symbols = [
    "NFLX",
    "PEP",
    "WMT",
    "UNH",
    "DIS",
]


data_service = PortfolioDataService()
optimizer = PortfolioOptimizer()


price_data = (
    data_service.get_price_data(symbols)
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


optimized_weights = optimizer.optimize(
    asset_returns,
    maximum_weight=0.30,
    target_volatility=target_volatility,
)

weights = np.array(
    [
        optimized_weights[symbol]
        for symbol in asset_returns.columns
    ]
)

covariance_matrix = (
    asset_returns.cov().values * 252
)

optimized_volatility = np.sqrt(
    weights.T
    @ covariance_matrix
    @ weights
)

print()
print(
    f"Optimized Annualized Volatility: "
    f"{optimized_volatility:.2%}"
)

print(
    f"Target Volatility: "
    f"{target_volatility:.2%}"
)

print(
    f"Constraint Satisfied: "
    f"{optimized_volatility <= target_volatility}"
)
print()
print("Optimized Portfolio")
print("-------------------")

for symbol, weight in optimized_weights.items():
    print(
        f"{symbol}: {weight:.2%}"
    )

print()
print(
    f"Total Weight: "
    f"{sum(optimized_weights.values()):.2%}"
)

