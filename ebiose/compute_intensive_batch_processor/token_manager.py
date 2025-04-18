"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from loguru import logger


class BudgetExceededError(Exception):
    """Exception raised when a token or master budget limit is exceeded."""
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logger.info(f"BudgetExceededError: {message}. Finishing process.")
