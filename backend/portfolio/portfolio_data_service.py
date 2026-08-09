"""
Portfolio Data Service

Responsible for collecting market data required
for portfolio analysis.
"""

import pandas as pd

from backend.core.logger import get_logger
from backend.services.market_data_service import MarketDataService


class PortfolioDataService:
    """
    Service responsible for preparing market data
    for portfolio analysis.
    """

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.market_data_service = MarketDataService()

    def get_price_data(
        self,
        symbols: list[str],
    ) -> dict[str, pd.DataFrame]:
        """
        Retrieve historical price data for multiple stocks.
        """
        self.logger.info(
        f"Retrieving market data for {len(symbols)} assets."
        )

        price_data = {}

        for symbol in symbols:
            self.logger.info(
                f"Retrieving data for {symbol}..."
            )

            dataframe = self.market_data_service.download_stock(
                symbol,
                save=True,
            )

            price_data[symbol.upper()] = dataframe

        self.logger.info(
            "Market data retrieval completed."
        )

        return price_data
    def combine_price_data(self,price_data: dict[str, pd.DataFrame],) -> pd.DataFrame:
        """
        Combine closing prices from multiple assets
        into a single DataFrame.
        """

        self.logger.info(
            "Combining closing prices for portfolio assets."
        )

        closing_prices = {}

        for symbol, dataframe in price_data.items():
            closing_prices[symbol] = dataframe["Close"]

        combined_data = pd.DataFrame(closing_prices)

        self.logger.info(
            f"Combined price data shape: {combined_data.shape}"
        )

        return combined_data
    def calculate_returns(self,price_data: pd.DataFrame,) -> pd.DataFrame:
        """
        Calculate daily percentage returns from closing prices.
        """

        self.logger.info(
            "Calculating daily asset returns."
        )

        returns = price_data.pct_change()

    # The first row has no previous trading day,
    # so it does not have a return.
        returns = returns.dropna()

        self.logger.info(
            f"Calculated returns for {len(returns)} trading days."
        )

        return returns
    
    def calculate_portfolio_returns(self,returns: pd.DataFrame,weights: dict[str, float],) -> pd.Series:
        """
        Calculate the daily returns of an investment portfolio.
        """

        self.logger.info(
            "Calculating portfolio returns."
        )

    # Make sure the portfolio contains only
    # assets for which we have return data.
        missing_symbols = [
            symbol
            for symbol in weights
            if symbol not in returns.columns
            ]

        if missing_symbols:
            raise ValueError(
                f"Return data is missing for: {missing_symbols}"
            )

    # Select the assets in the portfolio
        portfolio_returns = returns[
            list(weights.keys())
            ]

    # Convert weights into a Pandas Series
        weight_series = pd.Series(weights)

    # Calculate weighted daily portfolio return
        daily_portfolio_returns = (
            portfolio_returns * weight_series
        ).sum(axis=1)

        self.logger.info(
            "Portfolio returns calculated successfully."
        )

        return daily_portfolio_returns