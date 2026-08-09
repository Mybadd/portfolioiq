from dataclasses import dataclass


@dataclass
class RiskReport:
    annualized_volatility: float
    maximum_drawdown: float
    sharpe_ratio: float
    historical_value_at_risk: float
    expected_shortfall: float
    risk_contribution: dict[str, float]
    stress_results: dict[str, float]
    risk_score: float
    risk_level: str