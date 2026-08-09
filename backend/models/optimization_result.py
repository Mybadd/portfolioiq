from dataclasses import dataclass


@dataclass
class OptimizationResult:
    feasible: bool
    weights: dict[str, float]
    volatility: float
    maximum_drawdown: float
    sharpe_ratio: float
    message: str