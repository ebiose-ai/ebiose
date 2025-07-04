"""Exception classes for the Ebiose system."""

from __future__ import annotations


class EbioseCloudError(Exception):
    """Base exception for EbioseCloud API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_text: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

    def __str__(self) -> str:
        return f"{super().__str__()} (Status Code: {self.status_code}, Response: {self.response_text or 'N/A'})"


class EbioseCloudHTTPError(EbioseCloudError):
    """Exception for HTTP errors (4xx, 5xx)."""


class EbioseCloudAuthError(EbioseCloudError):
    """Exception for authentication-related errors."""


class AgentEngineRunError(Exception):
    """Custom exception for errors during agent run."""

    def __init__(
        self,
        message: str,
        original_exception: Exception | None = None,
        agent_identifier: str | None = None,
    ) -> None:
        super().__init__(message)
        self.original_exception = original_exception
        self.agent_identifier = agent_identifier

    def __str__(self) -> str:
        import traceback

        error_msg = "AgentRunError"
        if self.agent_identifier:
            error_msg += f" (Agent: {self.agent_identifier})"
        error_msg += f": {super().__str__()}"
        if self.original_exception:
            orig_traceback = traceback.format_exception(
                type(self.original_exception),
                self.original_exception,
                self.original_exception.__traceback__,
            )
            error_msg += f"\n--- Caused by ---\n{''.join(orig_traceback)}"
        return error_msg


class AgentEngineError(Exception):
    """Exception raised when an agent engine encounters an error."""

    def __init__(self, message: str, engine_type: str | None = None):
        super().__init__(message)
        self.engine_type = engine_type
