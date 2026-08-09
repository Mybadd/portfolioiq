"""
Risk Service

Responsible for calculating portfolio risk metrics.
"""

import pandas as pd

from backend.core.logger import get_logger
from backend.models.risk_metrics import RiskMetrics
from backend.constants.financial_constants import TRADING_DAYS_PER_YEAR
from backend.models.portfolio import Portfolio
from backend.models.stress_test import StressScenario

class RiskService:
    """
    Service responsible for portfolio risk calculations.
    """

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)

    def calculate_volatility(self,portfolio_returns: pd.Series,) -> float:
        """
        Calculate annualized portfolio volatility.
        """
        self.logger.info(
        "Calculating annualized portfolio volatility."
        )

        if portfolio_returns.empty:
            raise ValueError(
                "Portfolio return series cannot be empty."
            )

        daily_volatility = portfolio_returns.std()

        annualized_volatility = (
            daily_volatility
            * (TRADING_DAYS_PER_YEAR ** 0.5)
        )

        self.logger.info(
            f"Annualized volatility: "
            f"{annualized_volatility:.6f}"
        )   

        return float(annualized_volatility)
    def calculate_maximum_drawdown(self,portfolio_returns: pd.Series,) -> float:
        """
        Calculate the maximum historical drawdown
        of the portfolio.
        """

        self.logger.info(
        "Calculating maximum portfolio drawdown."
        )

        if portfolio_returns.empty:
            raise ValueError(
                "Portfolio return series cannot be empty."
            )

        cumulative_value = (
            1 + portfolio_returns
        ).cumprod()

        running_peak = cumulative_value.cummax()

        drawdown = (
            cumulative_value - running_peak
        ) / running_peak

        maximum_drawdown = drawdown.min()

        self.logger.info(
            f"Maximum drawdown: {maximum_drawdown:.6f}"
        )

        return float(maximum_drawdown)

    def calculate_sharpe_ratio(self,portfolio_returns: pd.Series,risk_free_rate: float = 0.0,) -> float:
        """
    Calculate the annualized Sharpe Ratio.

    Parameters
    ----------
    portfolio_returns:
        Daily portfolio returns.

    risk_free_rate:
        Annual risk-free rate expressed as a decimal.
        For example, 0.05 represents 5 percent.
        """

        self.logger.info(
            "Calculating Sharpe Ratio."
        )

        if portfolio_returns.empty:
            raise ValueError(
                "Portfolio return series cannot be empty."
            )

        if risk_free_rate < 0:
            raise ValueError(
                "Risk-free rate cannot be negative."
            )

        daily_risk_free_rate = (
            (1 + risk_free_rate)
            ** (1 / TRADING_DAYS_PER_YEAR)
            - 1
        )

        excess_daily_returns = (
            portfolio_returns - daily_risk_free_rate
        )

        daily_volatility = portfolio_returns.std()

        if daily_volatility == 0:
            raise ValueError(
                "Portfolio volatility cannot be zero."
            )

        sharpe_ratio = (
            excess_daily_returns.mean()
            / daily_volatility
        ) * (TRADING_DAYS_PER_YEAR ** 0.5)

        self.logger.info(
            f"Sharpe Ratio: {sharpe_ratio:.6f}"
        )

        return float(sharpe_ratio)
    def calculate_historical_value_at_risk(
    self,
    portfolio_returns: pd.Series,
    confidence_level: float = 0.95,
) -> float:
        """
        Calculate Historical Value at Risk using
        the historical simulation method.

        Parameters
        ----------
        portfolio_returns:
            Daily portfolio returns.

        confidence_level:
            Confidence level expressed as a decimal.
            For example, 0.95 represents 95 percent.

        Returns
        -------
        float
            Historical daily Value at Risk as a negative
            return value.
        """

        self.logger.info(
            "Calculating Historical Value at Risk."
        )

        if portfolio_returns.empty:
            raise ValueError(
                "Portfolio return series cannot be empty."
            )

        if not 0 < confidence_level < 1:
            raise ValueError(
                "Confidence level must be between 0 and 1."
            )

        percentile = (
            1 - confidence_level
        ) * 100

        historical_value_at_risk = (
            portfolio_returns.quantile(percentile / 100)
        )

        self.logger.info(
            f"Historical Value at Risk: "
            f"{historical_value_at_risk:.6f}"
        )

        return float(historical_value_at_risk)
    def calculate_expected_shortfall(
    self,
    portfolio_returns: pd.Series,
    confidence_level: float = 0.95,
) -> float:
        """
        Calculate Historical Expected Shortfall.

        Expected Shortfall is the average return of observations
        that are worse than the Historical Value at Risk threshold.
        """

        self.logger.info(
            "Calculating Expected Shortfall."
        )

        if portfolio_returns.empty:
            raise ValueError(
                "Portfolio return series cannot be empty."
            )

        if not 0 < confidence_level < 1:
            raise ValueError(
                "Confidence level must be between 0 and 1."
            )

        var_threshold = portfolio_returns.quantile(
            1 - confidence_level
        )

        tail_losses = portfolio_returns[
            portfolio_returns <= var_threshold
        ]

        if tail_losses.empty:
            raise ValueError(
                "Unable to calculate Expected Shortfall."
            )

        expected_shortfall = tail_losses.mean()

        self.logger.info(
            f"Expected Shortfall: "
            f"{expected_shortfall:.6f}"
        )

        return float(expected_shortfall)
    def calculate_stress_test(self,
    portfolio: Portfolio,
    scenario: StressScenario,
) -> float:
        """
        Calculate the estimated portfolio impact
        under a hypothetical stress scenario.
        """

        self.logger.info(
            f"Running stress scenario: {scenario.name}"
        )

        portfolio_impact = 0.0

        for symbol, weight in portfolio.weights.items():

            shock = scenario.asset_shocks.get(
                symbol,
                0.0,
            )

            contribution = weight * shock

            portfolio_impact += contribution

            self.logger.info(
                f"{symbol}: "
                f"weight={weight:.2%}, "
                f"shock={shock:.2%}, "
                f"contribution={contribution:.2%}"
            )

        self.logger.info(
            f"Stress test result: "
            f"{portfolio_impact:.2%}"
        )

        return float(portfolio_impact)
    def calculate_risk_contribution(
    self,
    asset_returns: pd.DataFrame,
    weights: dict[str, float],
) -> pd.Series:
        """
        Calculate each asset's contribution to
        portfolio variance.

        The result represents the proportion of
        portfolio variance attributable to each asset.
        """

        self.logger.info(
            "Calculating asset risk contributions."
        )

        if asset_returns.empty:
            raise ValueError(
                "Asset return data cannot be empty."
            )

        if not weights:
            raise ValueError(
                "Portfolio weights cannot be empty."
            )

        missing_symbols = [
            symbol
            for symbol in weights
            if symbol not in asset_returns.columns
        ]

        if missing_symbols:
            raise ValueError(
                f"Return data is missing for: "
                f"{missing_symbols}"
            )

        weight_series = pd.Series(weights)

        covariance_matrix = asset_returns[
            list(weights.keys())
        ].cov()

        portfolio_variance = (
            weight_series.T
            @ covariance_matrix
            @ weight_series
        )

        if portfolio_variance <= 0:
            raise ValueError(
                "Portfolio variance must be positive."
            )

        marginal_contribution = (
            covariance_matrix
            @ weight_series
        )

        component_contribution = (
            weight_series
            * marginal_contribution
        )

        risk_contribution = (
            component_contribution
            / portfolio_variance
        )

        self.logger.info(
            "Asset risk contributions calculated successfully."
        )

        return risk_contribution