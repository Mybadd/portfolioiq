"""
Risk metrics data model.
"""

from dataclasses import dataclass


@dataclass
class RiskMetrics:
    """
    Contains calculated portfolio risk metrics.
    """

    annualized_volatility: float
    maximum_drawdown: float
    sharpe_ratio: float
    historical_var: float
    expected_shortfall: float