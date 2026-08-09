from backend.models.investor_profile import InvestorProfile
from backend.portfolio.investor_optimizer import InvestorOptimizer


investor = InvestorProfile(
    investment_amount=1_000_000,
    investment_horizon_years=7,
    risk_tolerance="MODERATE",
    maximum_acceptable_loss=0.20,
    investment_objective="LONG_TERM_GROWTH",
)

optimizer = InvestorOptimizer()

target_volatility = optimizer.get_target_volatility(
    investor
)

print()
print("Investor Optimization Settings")
print("-------------------------------")

print(
    f"Risk Tolerance: "
    f"{investor.risk_tolerance}"
)

print(
    f"Target Volatility: "
    f"{target_volatility:.2%}"
)