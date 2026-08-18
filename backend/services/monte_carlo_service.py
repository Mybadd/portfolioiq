"""
Monte Carlo Simulation Service

Provides historical bootstrap Monte Carlo simulation
for portfolio return and tail-risk analysis.
"""

import numpy as np
import pandas as pd

from backend.core.logger import get_logger


class MonteCarloService:
    """
    Service responsible for Monte Carlo portfolio simulation.

    The implementation uses historical bootstrap sampling.
    Complete historical rows are sampled together so that
    the historical relationship between portfolio assets
    is preserved.
    """

    def __init__(self) -> None:
        self.logger = get_logger(
            self.__class__.__name__
        )

    def simulate(
        self,
        asset_returns: pd.DataFrame,
        weights: dict[str, float],
        simulations: int = 10000,
        horizon_days: int = 252,
        confidence_level: float = 0.95,
        random_seed: int | None = 42,
    ) -> dict:
        """
        Run a historical bootstrap Monte Carlo simulation.

        Parameters
        ----------
        asset_returns:
            Historical daily asset returns.

        weights:
            Portfolio asset weights.

        simulations:
            Number of Monte Carlo paths.

        horizon_days:
            Number of trading days simulated
            for each path.

        confidence_level:
            Confidence level used for VaR and
            Expected Shortfall.

        random_seed:
            Optional random seed for reproducibility.
        """

        self._validate_inputs(
            asset_returns=asset_returns,
            weights=weights,
            simulations=simulations,
            horizon_days=horizon_days,
            confidence_level=confidence_level,
        )

        self.logger.info(
            "Starting historical bootstrap Monte Carlo "
            f"simulation: simulations={simulations}, "
            f"horizon={horizon_days} days."
        )

        symbols = list(weights.keys())

        missing_symbols = [
            symbol
            for symbol in symbols
            if symbol not in asset_returns.columns
        ]

        if missing_symbols:
            raise ValueError(
                "Return data is missing for: "
                f"{missing_symbols}"
            )

        returns = asset_returns[
            symbols
        ].dropna()

        if returns.empty:
            raise ValueError(
                "No valid historical returns available."
            )

        # --------------------------------------------------
        # Prepare weights
        # --------------------------------------------------

        weight_series = pd.Series(
            weights,
            dtype=float,
        )

        weight_series = weight_series[
            symbols
        ]

        # --------------------------------------------------
        # Convert historical asset returns into
        # NumPy representation.
        #
        # Shape:
        #
        #     historical_days × assets
        # --------------------------------------------------

        historical_returns = (
            returns.to_numpy(
                dtype=float
            )
        )

        historical_days = (
            historical_returns.shape[0]
        )

        self.logger.info(
            f"Using {historical_days} historical "
            "observations."
        )

        # --------------------------------------------------
        # Bootstrap complete historical rows.
        #
        # Shape:
        #
        #     simulations × horizon_days
        #
        # Each selected row represents one complete
        # historical cross-sectional market observation.
        # --------------------------------------------------

        rng = np.random.default_rng(
            random_seed
        )

        sampled_indices = rng.integers(
            low=0,
            high=historical_days,
            size=(
                simulations,
                horizon_days,
            ),
        )

        sampled_returns = (
            historical_returns[
                sampled_indices
            ]
        )

        # --------------------------------------------------
        # Convert asset returns into portfolio returns.
        #
        # Shape:
        #
        #     simulations × horizon_days
        # --------------------------------------------------

        portfolio_daily_returns = np.einsum(
            "shk,k->sh",
            sampled_returns,
            weight_series.to_numpy(),
        )

        # --------------------------------------------------
        # Calculate cumulative terminal value.
        #
        # V_T = product(1 + R_t)
        # --------------------------------------------------

        terminal_values = np.prod(
            1.0 + portfolio_daily_returns,
            axis=1,
        )

        terminal_returns = (
            terminal_values - 1.0
        )

        # --------------------------------------------------
        # Distribution statistics
        # --------------------------------------------------

        mean_return = float(
            np.mean(terminal_returns)
        )

        median_return = float(
            np.median(terminal_returns)
        )

        percentile_5 = float(
            np.percentile(
                terminal_returns,
                5,
            )
        )

        percentile_95 = float(
            np.percentile(
                terminal_returns,
                95,
            )
        )

        # --------------------------------------------------
        # Probability of losses
        # --------------------------------------------------

        probability_of_loss = float(
            np.mean(
                terminal_returns < 0
            )
        )

        probability_loss_10 = float(
            np.mean(
                terminal_returns <= -0.10
            )
        )

        probability_loss_20 = float(
            np.mean(
                terminal_returns <= -0.20
            )
        )

        # --------------------------------------------------
        # Monte Carlo VaR
        # --------------------------------------------------

        var_percentile = (
            (1.0 - confidence_level)
            * 100.0
        )

        monte_carlo_var = float(
            np.percentile(
                terminal_returns,
                var_percentile,
            )
        )

        # --------------------------------------------------
        # Expected Shortfall
        # --------------------------------------------------

        tail_losses = terminal_returns[
            terminal_returns
            <= monte_carlo_var
        ]

        if len(tail_losses) == 0:
            raise RuntimeError(
                "Unable to calculate Monte Carlo "
                "Expected Shortfall."
            )

        monte_carlo_expected_shortfall = float(
            np.mean(tail_losses)
        )

        # --------------------------------------------------
        # Worst and best simulated outcomes
        # --------------------------------------------------

        worst_return = float(
            np.min(terminal_returns)
        )

        best_return = float(
            np.max(terminal_returns)
        )

        # --------------------------------------------------
        # Build histogram data.
        #
        # The frontend can use this to render the
        # simulated return distribution.
        # --------------------------------------------------

        histogram_counts, histogram_edges = (
            np.histogram(
                terminal_returns,
                bins=40,
            )
        )

        histogram = []

        for index, count in enumerate(
            histogram_counts
        ):
            histogram.append(
                {
                    "lower": float(
                        histogram_edges[index]
                    ),
                    "upper": float(
                        histogram_edges[
                            index + 1
                        ]
                    ),
                    "count": int(count),
                }
            )

        # --------------------------------------------------
        # Result
        # --------------------------------------------------

        result = {
            "method": (
                "HISTORICAL_BOOTSTRAP"
            ),
            "simulations": simulations,
            "horizon_days": horizon_days,
            "confidence_level": (
                confidence_level
            ),
            "historical_observations": (
                historical_days
            ),
            "statistics": {
                "mean_return": mean_return,
                "median_return": median_return,
                "percentile_5": percentile_5,
                "percentile_95": percentile_95,
                "probability_of_loss": (
                    probability_of_loss
                ),
                "probability_loss_10": (
                    probability_loss_10
                ),
                "probability_loss_20": (
                    probability_loss_20
                ),
                "var": monte_carlo_var,
                "expected_shortfall": (
                    monte_carlo_expected_shortfall
                ),
                "worst_return": worst_return,
                "best_return": best_return,
            },
            "histogram": histogram,
        }

        self.logger.info(
            "Monte Carlo simulation completed "
            "successfully."
        )

        return result
    # ======================================================
    # Multi-Horizon Simulation
    # ======================================================

    def simulate_all_horizons(
        self,
        asset_returns: pd.DataFrame,
        weights: dict[str, float],
        simulations: int = 10000,
        confidence_level: float = 0.95,
        random_seed: int | None = 42,
    ) -> dict:
        """
        Run historical bootstrap Monte Carlo simulation
        across all supported investment horizons.
        """

        horizons = {
            "1M": 21,
            "3M": 63,
            "6M": 126,
            "1Y": 252,
            "2Y": 504,
        }

        self.logger.info(
            "Starting multi-horizon Monte Carlo simulation."
        )

        results = {}

        for horizon_name, horizon_days in horizons.items():

            self.logger.info(
                f"Simulating horizon {horizon_name} "
                f"({horizon_days} trading days)."
            )

            results[horizon_name] = self.simulate(
                asset_returns=asset_returns,
                weights=weights,
                simulations=simulations,
                horizon_days=horizon_days,
                confidence_level=confidence_level,
                random_seed=random_seed,
            )

        self.logger.info(
            "Multi-horizon Monte Carlo simulation "
            "completed successfully."
        )

        return results
    def _validate_inputs(
        self,
        asset_returns: pd.DataFrame,
        weights: dict[str, float],
        simulations: int,
        horizon_days: int,
        confidence_level: float,
    ) -> None:
        """
        Validate Monte Carlo simulation inputs.
        """

        if asset_returns.empty:
            raise ValueError(
                "Asset returns cannot be empty."
            )

        if not weights:
            raise ValueError(
                "Portfolio weights cannot be empty."
            )

        if simulations <= 0:
            raise ValueError(
                "Number of simulations must be positive."
            )

        if horizon_days <= 0:
            raise ValueError(
                "Simulation horizon must be positive."
            )

        if not 0 < confidence_level < 1:
            raise ValueError(
                "Confidence level must be between "
                "0 and 1."
            )

        invalid_weights = [
            symbol
            for symbol, weight in weights.items()
            if not np.isfinite(weight)
            or weight < 0
        ]

        if invalid_weights:
            raise ValueError(
                "Portfolio weights must be finite "
                "and non-negative: "
                f"{invalid_weights}"
            )

        total_weight = sum(
            weights.values()
        )

        if not np.isclose(
            total_weight,
            1.0,
            atol=1e-4,
        ):
            raise ValueError(
                "Portfolio weights must sum to 1.0."
            )

        if asset_returns.isnull().values.any():
            raise ValueError(
                "Asset returns contain missing values."
            )

        if not np.isfinite(
            asset_returns.to_numpy(
                dtype=float
            )
        ).all():
            raise ValueError(
                "Asset returns contain invalid "
                "numeric values."
            )