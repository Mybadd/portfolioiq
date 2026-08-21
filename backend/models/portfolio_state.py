from dataclasses import dataclass


@dataclass
class PortfolioState:
    """
    Represents the current market state of an investor portfolio.

    Stores the original holdings together with the latest market
    prices, position values, total portfolio value, and dynamically
    calculated portfolio weights.
    """

    holdings: dict[str, float]
    latest_prices: dict[str, float]
    position_values: dict[str, float]
    total_portfolio_value: float
    weights: dict[str, float]