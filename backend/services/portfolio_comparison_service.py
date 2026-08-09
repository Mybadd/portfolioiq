"""
Portfolio Comparison Service

Compares the risk characteristics of an original
portfolio and an optimized portfolio using the
same historical asset returns.
"""

import pandas as pd

from backend.core.logger import get_logger
from backend.models.portfolio_comparison import PortfolioComparison
from backend.risk.risk_service import RiskService


class PortfolioComparisonService:

    def __init__(self) -> None:
        self.logger = get_logger(
            self.__class__.__name__
        )
        self.risk_service = RiskService()

    def compare(
        self,
        asset_returns: pd.DataFrame,
        before_weights: dict[str, float],
        after_weights: dict[str, float],
    ) -> PortfolioComparison:
        """
        Compare the original and optimized portfolios.
        """

        self.logger.info(
            "Starting portfolio comparison."
        )

        before_returns = self._calculate_portfolio_returns(
            asset_returns,
            before_weights,
        )

        after_returns = self._calculate_portfolio_returns(
            asset_returns,
            after_weights,
        )

        before_metrics = self._calculate_metrics(
            before_returns
        )

        after_metrics = self._calculate_metrics(
            after_returns
        )

        comparison = PortfolioComparison(
            before_volatility=before_metrics["volatility"],
            after_volatility=after_metrics["volatility"],
            before_drawdown=before_metrics["drawdown"],
            after_drawdown=after_metrics["drawdown"],
            before_sharpe=before_metrics["sharpe"],
            after_sharpe=after_metrics["sharpe"],
            before_var=before_metrics["var"],
            after_var=after_metrics["var"],
            before_expected_shortfall=(
                before_metrics["expected_shortfall"]
            ),
            after_expected_shortfall=(
                after_metrics["expected_shortfall"]
            ),
            before_risk_score=before_metrics["risk_score"],
            after_risk_score=after_metrics["risk_score"],
        )

        self.logger.info(
            "Portfolio comparison completed."
        )

        return comparison

    def _calculate_portfolio_returns(
        self,
        asset_returns: pd.DataFrame,
        weights: dict[str, float],
    ) -> pd.Series:
        """
        Calculate portfolio returns from asset returns
        and portfolio weights.
        """

        missing_assets = set(weights) - set(
            asset_returns.columns
        )

        if missing_assets:
            raise ValueError(
                "Missing assets from return data: "
                f"{sorted(missing_assets)}"
            )

        weight_series = pd.Series(
            weights,
            dtype=float,
        )

        weight_series = weight_series.reindex(
            asset_returns.columns
        ).fillna(0.0)

        if abs(weight_series.sum() - 1.0) > 1e-6:
            raise ValueError(
                "Portfolio weights must sum to 1.0."
            )

        return asset_returns @ weight_series

    def _calculate_metrics(
        self,
        portfolio_returns: pd.Series,
    ) -> dict[str, float]:
        """
        Calculate all required risk metrics.
        """

        volatility = (
            self.risk_service.calculate_volatility(
                portfolio_returns
            )
        )

        drawdown = (
            self.risk_service.calculate_maximum_drawdown(
                portfolio_returns
            )
        )

        sharpe = (
            self.risk_service.calculate_sharpe_ratio(
                portfolio_returns
            )
        )

        value_at_risk = (
            self.risk_service.calculate_historical_value_at_risk(
                portfolio_returns
            )
        )

        expected_shortfall = (
            self.risk_service.calculate_expected_shortfall(
                portfolio_returns
            )
        )

        # Use the same scoring model for both portfolios.
        risk_score = self._calculate_risk_score(
            volatility=volatility,
            drawdown=drawdown,
            sharpe=sharpe,
            value_at_risk=value_at_risk,
            expected_shortfall=expected_shortfall,
        )

        return {
            "volatility": volatility,
            "drawdown": drawdown,
            "sharpe": sharpe,
            "var": value_at_risk,
            "expected_shortfall": expected_shortfall,
            "risk_score": risk_score,
        }

    def _calculate_risk_score(
        self,
        volatility: float,
        drawdown: float,
        sharpe: float,
        value_at_risk: float,
        expected_shortfall: float,
    ) -> float:
        """
        Calculate the risk score using the same
        Version 1 scoring methodology.
        """

        volatility_score = min(
            volatility / 0.50 * 100,
            100,
        )

        drawdown_score = min(
            abs(drawdown) / 0.60 * 100,
            100,
        )

        var_score = min(
            abs(value_at_risk) / 0.10 * 100,
            100,
        )

        expected_shortfall_score = min(
            abs(expected_shortfall) / 0.15 * 100,
            100,
        )

        if sharpe >= 2:
            sharpe_adjustment = -15
        elif sharpe >= 1:
            sharpe_adjustment = -8
        elif sharpe >= 0:
            sharpe_adjustment = 0
        else:
            sharpe_adjustment = 10

        score = (
            volatility_score * 0.25
            + drawdown_score * 0.25
            + var_score * 0.20
            + expected_shortfall_score * 0.20
            + 5
            + sharpe_adjustment
        )

        return max(
            0,
            min(score, 100),
        )