from dataclasses import dataclass


@dataclass
class PortfolioComparison:
    before_volatility: float
    after_volatility: float

    before_drawdown: float
    after_drawdown: float

    before_sharpe: float
    after_sharpe: float

    before_var: float
    after_var: float

    before_expected_shortfall: float
    after_expected_shortfall: float

    before_risk_score: float
    after_risk_score: float