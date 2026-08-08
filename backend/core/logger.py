"""
Project Logger

Provides a centralized logger for the application.
"""

import logging


def get_logger(name: str) -> logging.Logger:
    """
    Create and return a configured logger.
    """

    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "[%(levelname)s] %(asctime)s - %(name)s - %(message)s"
        )

        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger