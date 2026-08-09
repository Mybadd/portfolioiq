"""
Portfolio Service

Responsible for creating and validating investor portfolios.
"""
import pandas as pd
from backend.models.portfolio import Portfolio
from backend.core.logger import get_logger
from backend.constants.market_universe import SUPPORTED_STOCKS
from backend.portfolio.portfolio_data_service import PortfolioDataService


class PortfolioService:
    """
    Service responsible for portfolio operations.
    """

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.portfolio_data_service = PortfolioDataService()

    def create_portfolio(
        self,
        weights: dict[str, float],
    ) -> Portfolio:
        """
        Create and validate an investor portfolio.
        """
        self.logger.info("Creating portfolio...")

        self._validate_weights(weights)
        self._validate_symbols(weights)

        portfolio = Portfolio(
            weights={
                symbol.upper(): weight
                for symbol, weight in weights.items()
            }
        )

        self.logger.info(
            f"Portfolio created with {len(portfolio.weights)} assets."
        )

        return portfolio

    def _validate_weights(
        self,
        weights: dict[str, float],
    ) -> None:
        """
        Validate portfolio weights.
        """
           # Portfolio must not be empty
        if not weights:
            raise ValueError("Portfolio cannot be empty.")

    # Every asset must have a positive weight
        for symbol, weight in weights.items():
            if weight <= 0:
                raise ValueError(
                    f"Weight for {symbol} must be greater than zero."
                )

    # Portfolio weights must equal 100 percent
        total_weight = sum(weights.values())

        if abs(total_weight - 1.0) > 1e-6:
            raise ValueError(
                f"Portfolio weights must sum to 1.0. "
                f"Current total: {total_weight:.6f}"
            )
    def _validate_symbols(self,weights: dict[str, float],) -> None:
        """
        Validate that all portfolio assets are supported.
        """

        unsupported_symbols = [
            symbol.upper()
            for symbol in weights
            if symbol.upper() not in SUPPORTED_STOCKS
        ]

        if unsupported_symbols:
            raise ValueError(
                f"Unsupported stock symbols: {unsupported_symbols}"
            )   
    def calculate_portfolio_returns(self,portfolio: Portfolio,) -> pd.Series:
        """
        Calculate historical daily returns for a portfolio.
        """

        self.logger.info(
            "Starting portfolio return calculation."
        )

        symbols = list(portfolio.weights.keys())

        price_data = self.portfolio_data_service.get_price_data(
            symbols
        )

        combined_prices = (
            self.portfolio_data_service.combine_price_data(
                price_data
            )
        )

        asset_returns = (
            self.portfolio_data_service.calculate_returns(
                combined_prices
            )
        )

        portfolio_returns = (
            self.portfolio_data_service.calculate_portfolio_returns(
                asset_returns,
                portfolio.weights,
            )
        )

        self.logger.info(
            "Portfolio return calculation completed."
        )

        return portfolio_returns