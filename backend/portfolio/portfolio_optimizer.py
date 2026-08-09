"""
Risk-Adjusted Portfolio Optimization
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from backend.core.logger import get_logger


class PortfolioOptimizer:

    def __init__(self) -> None:
        self.logger = get_logger(
            self.__class__.__name__
        )

    def optimize(
        self,
        asset_returns: pd.DataFrame,
        maximum_weight: float = 0.30,
        target_volatility: float | None = None,
        risk_free_rate: float = 0.0,
    ) -> dict[str, float]:
        """
        Optimize a portfolio using a risk-adjusted
        objective rather than volatility alone.

        The optimizer considers:

        - Portfolio volatility
        - Sharpe ratio
        - Concentration
        - Investor volatility target
        """

        self.logger.info(
            "Starting risk-adjusted portfolio optimization."
        )

        if asset_returns.empty:
            raise ValueError(
                "Asset returns cannot be empty."
            )

        assets = list(asset_returns.columns)
        number_of_assets = len(assets)

        if number_of_assets == 0:
            raise ValueError(
                "At least one asset is required."
            )

        if not 0 < maximum_weight <= 1:
            raise ValueError(
                "Maximum weight must be between 0 and 1."
            )

        if (
            maximum_weight * number_of_assets < 1
        ):
            raise ValueError(
                "Maximum weight is too restrictive "
                "for the number of assets."
            )

        covariance_matrix = (
            asset_returns.cov().values * 252
        )

        mean_returns = (
            asset_returns.mean().values * 252
        )

        def portfolio_volatility(weights):
            variance = (
                weights.T
                @ covariance_matrix
                @ weights
            )

            return np.sqrt(
                max(variance, 0)
            )

        def portfolio_return(weights):
            return weights @ mean_returns

        def sharpe_ratio(weights):
            volatility = portfolio_volatility(
                weights
            )

            if volatility <= 1e-12:
                return 0.0

            return (
                portfolio_return(weights)
                - risk_free_rate
            ) / volatility

        def concentration_penalty(weights):
            """
            Penalize excessive concentration.

            Herfindahl-Hirschman Index:
                sum(weight^2)
            """

            return np.sum(weights ** 2)

        def objective(weights):
            volatility = portfolio_volatility(
                weights
            )

            sharpe = sharpe_ratio(weights)

            concentration = (
                concentration_penalty(weights)
            )

            # Lower is better.
            #
            # Volatility is the primary risk component.
            # Sharpe is rewarded.
            # Concentration is penalized.
            score = (
                0.50 * volatility
                - 0.35 * sharpe
                + 0.15 * concentration
            )

            return score

        initial_weights = (
            np.ones(number_of_assets)
            / number_of_assets
        )

        constraints = [
            {
                "type": "eq",
                "fun": lambda weights:
                    np.sum(weights) - 1,
            }
        ]

        if target_volatility is not None:

            if target_volatility <= 0:
                raise ValueError(
                    "Target volatility must be positive."
                )

            constraints.append(
                {
                    "type": "ineq",
                    "fun": lambda weights:
                        target_volatility
                        - portfolio_volatility(
                            weights
                        ),
                }
            )

        bounds = [
            (0, maximum_weight)
            for _ in range(number_of_assets)
        ]

        result = minimize(
            objective,
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={
                "maxiter": 1000,
                "ftol": 1e-9,
            },
        )

        if not result.success:
            raise RuntimeError(
                "Portfolio optimization failed: "
                f"{result.message}"
            )

        optimized_weights = {
            asset: float(weight)
            for asset, weight in zip(
                assets,
                result.x,
            )
        }

        self.logger.info(
            "Risk-adjusted portfolio optimization "
            "completed."
        )

        return optimized_weights
    def check_feasibility(
    self,
    asset_returns,
    maximum_acceptable_loss: float,
    target_volatility: float | None = None,
    maximum_weight: float = 0.30,
) -> dict:
        """
        Check whether the available asset universe can produce
        a portfolio satisfying the investor's constraints.
        """

        self.logger.info(
            "Checking portfolio constraint feasibility."
        )

        assets = list(asset_returns.columns)
        number_of_assets = len(assets)

        covariance_matrix = (
            asset_returns.cov().values * 252
        )

        def portfolio_volatility(weights):
            variance = (
                weights.T
                @ covariance_matrix
                @ weights
            )

            return np.sqrt(max(variance, 0))

        def portfolio_returns(weights):
            return asset_returns @ weights

        def maximum_drawdown(weights):
            returns = portfolio_returns(weights)

            cumulative = (1 + returns).cumprod()

            running_max = cumulative.cummax()

            drawdowns = (
                cumulative / running_max
            ) - 1

            return drawdowns.min()

        def objective(weights):
            """
            Minimize drawdown magnitude.
            """

            return abs(
                maximum_drawdown(weights)
            )

        initial_weights = (
            np.ones(number_of_assets)
            / number_of_assets
        )

        constraints = [
            {
                "type": "eq",
                "fun": lambda weights:
                    np.sum(weights) - 1,
            }
        ]

        if target_volatility is not None:
            constraints.append(
                {
                    "type": "ineq",
                    "fun": lambda weights:
                        target_volatility
                        - portfolio_volatility(weights),
                }
            )

        bounds = [
            (0, maximum_weight)
            for _ in range(number_of_assets)
        ]

        result = minimize(
            objective,
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={
                "maxiter": 1000,
                "ftol": 1e-8,
            },
        )

        # -----------------------------------------
        # Optimization failed
        # -----------------------------------------

        if not result.success:
            self.logger.warning(
                "No feasible portfolio found."
            )

            return {
                "feasible": False,
                "best_drawdown": None,
                "maximum_acceptable_loss": (
                    maximum_acceptable_loss
                ),
                "target_volatility": (
                    target_volatility
                ),
            }

        # -----------------------------------------
        # Best achievable portfolio
        # -----------------------------------------

        best_drawdown = maximum_drawdown(
            result.x
        )

        self.logger.info(
            f"Best achievable maximum drawdown: "
            f"{best_drawdown:.4f}"
        )

        acceptable_drawdown = (
            -abs(maximum_acceptable_loss)
        )

        feasible = (
            best_drawdown >= acceptable_drawdown
        )

        if feasible:
            self.logger.info(
                "Investor constraints are feasible."
            )
        else:
            self.logger.warning(
                "Investor constraints cannot be "
                "satisfied by the available assets."
            )

        # -----------------------------------------
        # Return detailed feasibility result
        # -----------------------------------------

        return {
            "feasible": bool(feasible),

            "best_drawdown": float(
                best_drawdown
            ),

            "maximum_acceptable_loss": float(
                maximum_acceptable_loss
            ),

            "target_volatility": (
                float(target_volatility)
                if target_volatility is not None
                else None
            ),
        }