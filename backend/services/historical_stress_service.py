"""
Historical Stress Testing Service

Calculates portfolio performance during
historically defined market stress periods.
"""

from dataclasses import dataclass

import pandas as pd

from backend.core.logger import get_logger


@dataclass(frozen=True)
class HistoricalScenario:
    """
    Represents a historical market stress period.
    """

    name: str
    start_date: str
    end_date: str
    description: str


class HistoricalStressService:
    """
    Service for evaluating portfolio performance
    during historical market stress periods.
    """

    HISTORICAL_SCENARIOS = {
        "COVID_CRASH": HistoricalScenario(
            name="COVID-19 Crash",
            start_date="2020-02-19",
            end_date="2020-03-23",
            description=(
                "Global equity sell-off during "
                "the initial COVID-19 market shock."
            ),
        ),
        "2022_BEAR_MARKET": HistoricalScenario(
            name="2022 Bear Market",
            start_date="2022-01-03",
            end_date="2022-10-12",
            description=(
                "Broad equity-market decline during "
                "the 2022 bear market."
            ),
        ),
    }

    def __init__(self) -> None:
        self.logger = get_logger(
            self.__class__.__name__
        )

    def get_scenario(
        self,
        scenario_name: str,
    ) -> HistoricalScenario:
        """
        Retrieve a predefined historical scenario.
        """

        normalized_name = (
            scenario_name.strip().upper()
        )

        if normalized_name not in self.HISTORICAL_SCENARIOS:
            raise ValueError(
                "Unsupported historical scenario: "
                f"{scenario_name}. Supported scenarios are: "
                f"{sorted(self.HISTORICAL_SCENARIOS)}"
            )

        return self.HISTORICAL_SCENARIOS[
            normalized_name
        ]

    def calculate_asset_returns(
        self,
        price_data: pd.DataFrame,
        scenario: HistoricalScenario,
    ) -> pd.Series:
        """
        Calculate each asset's total return during
        the historical stress period.
        """

        if price_data.empty:
            raise ValueError(
                "Historical price data cannot be empty."
            )

        scenario_prices = price_data.loc[
            scenario.start_date:scenario.end_date
        ]

        if scenario_prices.empty:
            raise ValueError(
                f"No market data available for "
                f"{scenario.name}."
            )

        if len(scenario_prices) < 2:
            raise ValueError(
                f"Insufficient market data for "
                f"{scenario.name}."
            )

        first_prices = scenario_prices.iloc[0]
        last_prices = scenario_prices.iloc[-1]

        asset_returns = (
            last_prices / first_prices
        ) - 1.0

        return asset_returns

    def calculate_portfolio_impact(
        self,
        asset_returns: pd.Series,
        weights: dict[str, float],
    ) -> float:
        """
        Calculate portfolio return during the
        historical stress period.
        """

        missing_symbols = [
            symbol
            for symbol in weights
            if symbol not in asset_returns.index
        ]

        if missing_symbols:
            raise ValueError(
                "Historical return data is missing "
                f"for: {missing_symbols}"
            )

        weight_series = pd.Series(
            weights,
            dtype=float,
        )

        selected_returns = asset_returns[
            list(weights.keys())
        ]

        return float(
            (
                weight_series
                * selected_returns
            ).sum()
        )

    def calculate_recovery_required(
        self,
        portfolio_impact: float,
    ) -> float | None:
        """
        Calculate the gain required to recover
        from the historical portfolio loss.
        """

        portfolio_value_after = (
            1.0 + portfolio_impact
        )

        if portfolio_value_after <= 0:
            return None

        return float(
            (1.0 / portfolio_value_after) - 1.0
        )