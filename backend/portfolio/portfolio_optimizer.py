"""
Quantitative Portfolio Optimization

Provides standard quantitative portfolio optimization
methods while preserving investor constraint feasibility
analysis.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from backend.core.logger import get_logger


class PortfolioOptimizer:
    """
    Quantitative portfolio optimization engine.

    Supported methods:

    - MINIMUM_VARIANCE
    - RISK_PARITY

    The optimizer supports long-only portfolios with
    configurable maximum asset weights and optional
    volatility constraints.
    """

    def __init__(self) -> None:
        self.logger = get_logger(
            self.__class__.__name__
        )

    # ==========================================================
    # Public optimization interface
    # ==========================================================

    def optimize(
        self,
        asset_returns: pd.DataFrame,
        maximum_weight: float = 0.30,
        target_volatility: float | None = None,
        risk_free_rate: float = 0.0,
        method: str = "MINIMUM_VARIANCE",
    ) -> dict[str, float]:
        """
        Optimize a portfolio using a quantitative
        portfolio construction method.

        Parameters
        ----------
        asset_returns:
            Historical daily asset returns.

        maximum_weight:
            Maximum allocation allowed for any
            individual asset.

        target_volatility:
            Optional maximum annualized volatility.

        risk_free_rate:
            Annual risk-free rate. Used by methods
            that consider risk-adjusted return.

        method:
            Optimization methodology.

            Supported:
                MINIMUM_VARIANCE
                RISK_PARITY

        Returns
        -------
        dict[str, float]
            Optimized portfolio weights.
        """

        self._validate_returns(
            asset_returns
        )

        self._validate_maximum_weight(
            maximum_weight,
            len(asset_returns.columns),
        )

        if target_volatility is not None:
            if target_volatility <= 0:
                raise ValueError(
                    "Target volatility must be positive."
                )

        normalized_method = (
            method.strip().upper()
        )

        supported_methods = {
            "MINIMUM_VARIANCE",
            "RISK_PARITY",
            "CVAR",
        }

        if normalized_method not in supported_methods:
            raise ValueError(
                f"Unsupported optimization method: "
                f"{method}. Supported methods are: "
                f"{sorted(supported_methods)}"
            )

        self.logger.info(
            "Starting quantitative portfolio "
            f"optimization using {normalized_method}."
        )

        assets = list(
            asset_returns.columns
        )

        number_of_assets = len(assets)

        covariance_matrix = (
            asset_returns.cov().values * 252
        )

        # Small numerical regularization improves
        # stability when assets are highly correlated.
        covariance_matrix = (
            covariance_matrix
            + np.eye(number_of_assets) * 1e-8
        )

        if normalized_method == "MINIMUM_VARIANCE":
                optimized_weights = (
                    self._minimum_variance(
                        covariance_matrix=covariance_matrix,
                        number_of_assets=number_of_assets,
                        maximum_weight=maximum_weight,
                        target_volatility=target_volatility,
                    )
                )

        elif normalized_method == "RISK_PARITY":
                optimized_weights = (
                    self._risk_parity(
                        covariance_matrix=covariance_matrix,
                        number_of_assets=number_of_assets,
                        maximum_weight=maximum_weight,
                        target_volatility=target_volatility,
                    )
                )

        else:
                optimized_weights = (
                    self._cvar(
                        asset_returns=asset_returns,
                        number_of_assets=number_of_assets,
                        maximum_weight=maximum_weight,
                        target_volatility=target_volatility,
                    )
                )

        result = {
            asset: float(weight)
            for asset, weight in zip(
                assets,
                optimized_weights,
            )
        }

        self.logger.info(
            f"{normalized_method} optimization "
            "completed successfully."
        )

        return result
# ==========================================================
# CVaR / Expected Shortfall — Rockafellar–Uryasev
# ==========================================================

    def _cvar(self,asset_returns: pd.DataFrame,number_of_assets: int,maximum_weight: float,target_volatility: float | None,) -> np.ndarray:
        """
        Calculate a long-only CVaR-minimizing portfolio using
        the Rockafellar–Uryasev formulation.

        CVaR is optimized at a 95% confidence level.

        The optimization introduces an auxiliary VaR threshold
        variable alpha.

        Objective:

            minimize:
                alpha +
                1/(1-beta) * mean(max(loss - alpha, 0))

        Subject to:

            sum(w) = 1
            0 <= w_i <= maximum_weight

        An optional annualized volatility constraint can also
        be applied.
        """

        confidence_level = 0.95

        returns = asset_returns.values

        number_of_observations = len(returns)

        if number_of_observations == 0:
            raise ValueError(
                "Asset return data cannot be empty."
            )

        # ------------------------------------------------------
        # Portfolio return
        # ------------------------------------------------------

        def portfolio_returns(
            weights: np.ndarray,
        ) -> np.ndarray:
            return returns @ weights

        # ------------------------------------------------------
        # Annualized portfolio volatility
        # ------------------------------------------------------

        def portfolio_volatility(
            weights: np.ndarray,
        ) -> float:
            daily_returns = portfolio_returns(
                weights
            )

            return float(
                np.std(
                    daily_returns,
                    ddof=1,
                )
                * np.sqrt(252)
            )

        # ------------------------------------------------------
        # Rockafellar–Uryasev CVaR objective
        #
        # x =
        # [w_1, ..., w_n, alpha]
        # ------------------------------------------------------

        def objective(
            variables: np.ndarray,
        ) -> float:

            weights = variables[
                :number_of_assets
            ]

            alpha = variables[
                number_of_assets
            ]

            # Portfolio losses
            losses = -portfolio_returns(
                weights
            )

            excess_losses = np.maximum(
                losses - alpha,
                0.0,
            )

            cvar = (
                alpha
                + (
                    np.mean(excess_losses)
                    / (1.0 - confidence_level)
                )
            )

            return float(cvar)

        # ------------------------------------------------------
        # Initial solution
        # ------------------------------------------------------

        initial_weights = (
            np.ones(number_of_assets)
            / number_of_assets
        )

        initial_losses = -portfolio_returns(
            initial_weights
        )

        initial_alpha = float(
            np.quantile(
                initial_losses,
                confidence_level,
            )
        )

        initial_variables = np.concatenate(
            [
                initial_weights,
                [initial_alpha],
            ]
        )

        # ------------------------------------------------------
        # Portfolio weight constraint
        # ------------------------------------------------------

        constraints = [
            {
                "type": "eq",
                "fun": lambda variables: (
                    np.sum(
                        variables[
                            :number_of_assets
                        ]
                    )
                    - 1.0
                ),
            }
        ]

        # ------------------------------------------------------
        # Optional volatility constraint
        # ------------------------------------------------------

        if target_volatility is not None:
            constraints.append(
                {
                    "type": "ineq",
                    "fun": lambda variables: (
                        target_volatility
                        - portfolio_volatility(
                            variables[
                                :number_of_assets
                            ]
                        )
                    ),
                }
            )

        # ------------------------------------------------------
        # Bounds
        #
        # Alpha is allowed to move across the historical
        # loss range.
        # ------------------------------------------------------

        losses = -(
            returns @ initial_weights
        )

        alpha_lower = float(
            np.min(losses)
        )

        alpha_upper = float(
            np.max(losses)
        )

        bounds = [
            (0.0, maximum_weight)
            for _ in range(number_of_assets)
        ]

        bounds.append(
            (
                alpha_lower,
                alpha_upper,
            )
        )

        # ------------------------------------------------------
        # Optimization
        # ------------------------------------------------------

        result = minimize(
            objective,
            initial_variables,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={
                "maxiter": 3000,
                "ftol": 1e-10,
            },
        )

        if not result.success:
            raise RuntimeError(
                "CVaR optimization failed: "
                f"{result.message}"
            )

        optimized_weights = result.x[
            :number_of_assets
        ]

        return self._normalize_weights(
            optimized_weights
        )
    # ==========================================================
    # Minimum Variance
    # ==========================================================

    def _minimum_variance(
        self,
        covariance_matrix: np.ndarray,
        number_of_assets: int,
        maximum_weight: float,
        target_volatility: float | None,
    ) -> np.ndarray:
        """
        Calculate the minimum-variance portfolio.

        Objective:

            min w'Σw

        Subject to:

            Σw = 1
            0 <= w_i <= maximum_weight

        An optional volatility constraint can also
        be applied.
        """

        def portfolio_variance(
            weights: np.ndarray,
        ) -> float:
            return float(
                weights.T
                @ covariance_matrix
                @ weights
            )

        def portfolio_volatility(
            weights: np.ndarray,
        ) -> float:
            return float(
                np.sqrt(
                    max(
                        portfolio_variance(
                            weights
                        ),
                        0.0,
                    )
                )
            )

        initial_weights = (
            np.ones(number_of_assets)
            / number_of_assets
        )

        constraints = [
            {
                "type": "eq",
                "fun": lambda weights: (
                    np.sum(weights) - 1.0
                ),
            }
        ]

        if target_volatility is not None:
            constraints.append(
                {
                    "type": "ineq",
                    "fun": lambda weights: (
                        target_volatility
                        - portfolio_volatility(
                            weights
                        )
                    ),
                }
            )

        bounds = [
            (0.0, maximum_weight)
            for _ in range(number_of_assets)
        ]

        result = minimize(
            portfolio_variance,
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={
                "maxiter": 1000,
                "ftol": 1e-10,
            },
        )

        if not result.success:
            raise RuntimeError(
                "Minimum-variance optimization failed: "
                f"{result.message}"
            )

        return self._normalize_weights(
            result.x
        )

    # ==========================================================
    # Risk Parity
    # ==========================================================

    def _risk_parity(
        self,
        covariance_matrix: np.ndarray,
        number_of_assets: int,
        maximum_weight: float,
        target_volatility: float | None,
    ) -> np.ndarray:
        """
        Calculate a long-only risk-parity portfolio.

        Risk parity attempts to make each asset's
        contribution to total portfolio volatility
        approximately equal.

        Risk contribution for asset i:

            RC_i = w_i * (Σw)_i / portfolio_variance
        """

        def portfolio_variance(
            weights: np.ndarray,
        ) -> float:
            return float(
                weights.T
                @ covariance_matrix
                @ weights
            )

        def portfolio_volatility(
            weights: np.ndarray,
        ) -> float:
            return float(
                np.sqrt(
                    max(
                        portfolio_variance(
                            weights
                        ),
                        0.0,
                    )
                )
            )

        def risk_contributions(
            weights: np.ndarray,
        ) -> np.ndarray:
            portfolio_var = (
                portfolio_variance(weights)
            )

            if portfolio_var <= 1e-16:
                return np.zeros(
                    number_of_assets
                )

            marginal_contribution = (
                covariance_matrix @ weights
            )

            return (
                weights
                * marginal_contribution
                / portfolio_var
            )

        def objective(
            weights: np.ndarray,
        ) -> float:
            contributions = (
                risk_contributions(weights)
            )

            target = (
                1.0 / number_of_assets
            )

            return float(
                np.sum(
                    (
                        contributions
                        - target
                    )
                    ** 2
                )
            )

        initial_weights = (
            np.ones(number_of_assets)
            / number_of_assets
        )

        constraints = [
            {
                "type": "eq",
                "fun": lambda weights: (
                    np.sum(weights) - 1.0
                ),
            }
        ]

        if target_volatility is not None:
            constraints.append(
                {
                    "type": "ineq",
                    "fun": lambda weights: (
                        target_volatility
                        - portfolio_volatility(
                            weights
                        )
                    ),
                }
            )

        bounds = [
            (0.0, maximum_weight)
            for _ in range(number_of_assets)
        ]

        result = minimize(
            objective,
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={
                "maxiter": 2000,
                "ftol": 1e-12,
            },
        )

        if not result.success:
            raise RuntimeError(
                "Risk-parity optimization failed: "
                f"{result.message}"
            )

        return self._normalize_weights(
            result.x
        )

    # ==========================================================
    # Feasibility Analysis
    # ==========================================================

    def check_feasibility(
        self,
        asset_returns: pd.DataFrame,
        maximum_acceptable_loss: float,
        target_volatility: float | None = None,
        maximum_weight: float = 0.30,
    ) -> dict:
        """
        Check whether the available asset universe
        can produce a portfolio satisfying the
        investor's constraints.

        The feasibility search minimizes historical
        maximum drawdown magnitude.
        """

        self.logger.info(
            "Checking portfolio constraint feasibility."
        )

        self._validate_returns(
            asset_returns
        )

        self._validate_maximum_weight(
            maximum_weight,
            len(asset_returns.columns),
        )

        if maximum_acceptable_loss <= 0:
            raise ValueError(
                "Maximum acceptable loss must be positive."
            )

        if target_volatility is not None:
            if target_volatility <= 0:
                raise ValueError(
                    "Target volatility must be positive."
                )

        assets = list(
            asset_returns.columns
        )

        number_of_assets = len(assets)

        covariance_matrix = (
            asset_returns.cov().values * 252
        )

        def portfolio_volatility(
            weights: np.ndarray,
        ) -> float:
            variance = (
                weights.T
                @ covariance_matrix
                @ weights
            )

            return float(
                np.sqrt(
                    max(
                        variance,
                        0.0,
                    )
                )
            )

        def portfolio_returns(
            weights: np.ndarray,
        ) -> pd.Series:
            return asset_returns @ weights

        def maximum_drawdown(
            weights: np.ndarray,
        ) -> float:
            returns = portfolio_returns(
                weights
            )

            cumulative = (
                1.0 + returns
            ).cumprod()

            running_max = (
                cumulative.cummax()
            )

            drawdowns = (
                cumulative / running_max
            ) - 1.0

            return float(
                drawdowns.min()
            )

        def objective(
            weights: np.ndarray,
        ) -> float:
            return abs(
                maximum_drawdown(
                    weights
                )
            )

        initial_weights = (
            np.ones(number_of_assets)
            / number_of_assets
        )

        constraints = [
            {
                "type": "eq",
                "fun": lambda weights: (
                    np.sum(weights) - 1.0
                ),
            }
        ]

        if target_volatility is not None:
            constraints.append(
                {
                    "type": "ineq",
                    "fun": lambda weights: (
                        target_volatility
                        - portfolio_volatility(
                            weights
                        )
                    ),
                }
            )

        bounds = [
            (0.0, maximum_weight)
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

        best_drawdown = (
            maximum_drawdown(
                result.x
            )
        )

        acceptable_drawdown = (
            -abs(
                maximum_acceptable_loss
            )
        )

        feasible = (
            best_drawdown
            >= acceptable_drawdown
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

    # ==========================================================
    # Validation / Utility
    # ==========================================================

    def _validate_returns(
        self,
        asset_returns: pd.DataFrame,
    ) -> None:
        """
        Validate the historical return dataset.
        """

        if asset_returns.empty:
            raise ValueError(
                "Asset returns cannot be empty."
            )

        if asset_returns.shape[1] == 0:
            raise ValueError(
                "At least one asset is required."
            )

        if asset_returns.isnull().values.any():
            raise ValueError(
                "Asset returns contain missing values."
            )

        if not np.isfinite(
            asset_returns.values
        ).all():
            raise ValueError(
                "Asset returns contain invalid "
                "numeric values."
            )

    def _validate_maximum_weight(
        self,
        maximum_weight: float,
        number_of_assets: int,
    ) -> None:
        """
        Validate maximum portfolio weight.
        """

        if not 0 < maximum_weight <= 1:
            raise ValueError(
                "Maximum weight must be between 0 and 1."
            )

        if (
            maximum_weight
            * number_of_assets
            < 1.0
        ):
            raise ValueError(
                "Maximum weight is too restrictive "
                "for the number of assets."
            )

    def _normalize_weights(
        self,
        weights: np.ndarray,
    ) -> np.ndarray:
        """
        Normalize numerical optimizer output so
        portfolio weights sum exactly to one.
        """

        weights = np.asarray(
            weights,
            dtype=float,
        )

        weights = np.clip(
            weights,
            0.0,
            None,
        )

        total = weights.sum()

        if total <= 0:
            raise RuntimeError(
                "Optimizer produced invalid weights."
            )

        return weights / total