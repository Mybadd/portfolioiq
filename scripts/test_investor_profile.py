from backend.models.investor_profile import InvestorProfile


investor = InvestorProfile(
    investment_amount=1_000_000,
    investment_horizon_years=7,
    risk_tolerance="MODERATE",
    maximum_acceptable_loss=0.20,
    investment_objective="LONG_TERM_GROWTH",
)

print()
print("Investor Profile")
print("-----------------")
print(investor)