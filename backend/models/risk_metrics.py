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