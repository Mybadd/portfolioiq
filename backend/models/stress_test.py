from dataclasses import dataclass
from typing import Dict


@dataclass
class StressScenario:
    """
    Represents a hypothetical market stress scenario.
    """

    name: str
    asset_shocks: Dict[str, float]

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError(
                "Stress scenario name cannot be empty."
            )

        if not self.asset_shocks:
            raise ValueError(
                "Asset shocks cannot be empty."
            )

        for symbol, shock in self.asset_shocks.items():
            if not isinstance(shock, (int, float)):
                raise TypeError(
                    f"Shock for {symbol} must be numeric."
                )

            if shock < -1:
                raise ValueError(
                    f"Shock for {symbol} cannot be below -100%."
                )