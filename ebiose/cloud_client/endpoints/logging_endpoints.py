"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ebiose.core.models.api_models import LogEntryInputModel, LogEntryOutputModel

if TYPE_CHECKING:
    from ebiose.cloud_client.base_client import BaseHTTPClient


class LoggingEndpoints:
    """Logging service endpoints."""
    
    def __init__(self, client: BaseHTTPClient) -> None:
        self.client = client
    
    def add_log_entry(self, data: LogEntryInputModel) -> LogEntryOutputModel:
        """Add a log entry to the logging service."""
        return LogEntryOutputModel(**self.client.request("POST", "/logging", json_data=data))
