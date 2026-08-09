"""
Market Data Service

Responsible for downloading and storing historical market data.
"""

from pathlib import Path

import pandas as pd
import yfinance as yf

from backend.constants.market_universe import SUPPORTED_STOCKS
from backend.core.logger import get_logger
from backend.utilities.data_validator import DataValidator


class MarketDataService:
    """
    Service responsible for downloading historical market data.
    """

    def __init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)

    def download_stock(
        self,
        symbol: str,
        save: bool = True,
    ) -> pd.DataFrame:
        """
        Download historical data for a single stock.
        """
        self.logger.info(f"Starting download for {symbol}")

    # Step 1: Validate the symbol
        self._validate_symbol(symbol)

    # Step 2: Download the data
        dataframe = self._fetch_data(symbol)

    # Step 3: Validate the downloaded data
        self._validate_dataframe(dataframe)

    # Step 4: Save the data if requested
        if save:
            self._save_to_csv(dataframe, symbol)

        self.logger.info(f"Successfully processed {symbol}")

        return dataframe

    def _validate_symbol(self, symbol: str) -> None:
        """Validate the stock symbol."""
        symbol = symbol.upper()

        if symbol not in SUPPORTED_STOCKS:
            self.logger.error(
                f"Unsupported stock symbol: {symbol}"
            )

            raise ValueError(
                f"{symbol} is not supported."
            )

    def _fetch_data(self, symbol: str) -> pd.DataFrame:
        """Download data from Yahoo Finance."""
        self.logger.info(f"Downloading data for {symbol}")

        try:
            ticker = yf.Ticker(symbol)

            dataframe = ticker.history(
                period="10y",
                interval="1d",
                auto_adjust=False,
            )

            self.logger.info(
                f"Downloaded {len(dataframe)} rows for {symbol}"
            )

            return dataframe

        except Exception as error:
            self.logger.exception(
                f"Failed to download data for {symbol}"
            )

            raise RuntimeError(
                f"Unable to download data for {symbol}"
            ) from error

    def _validate_dataframe(self, dataframe: pd.DataFrame) -> None:
        """Validate downloaded data."""
        self.logger.info(
        "Validating downloaded data..."
        )

        DataValidator.validate_market_data(dataframe)

        self.logger.info(
            "Market data validation passed."
        )

    def _save_to_csv(
        self,
        dataframe: pd.DataFrame,
        symbol: str,
    ) -> None:
        """Save the data as a CSV file."""
        pass

    def _get_output_path(self, symbol: str) -> Path:
        """Return the output file path."""
        pass