"""Base HTTP client for Ebiose Cloud API."""

from __future__ import annotations

import json
from typing import Any

import requests
from loguru import logger
from pydantic import BaseModel

from ebiose.core.models.exceptions import EbioseCloudError, EbioseCloudHTTPError


class BaseHTTPClient:
    """Base HTTP client for interacting with the EbioseCloud API."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        bearer_token: str | None = None,
        timeout: int = 30,
    ) -> None:
        """Initialize the HTTP client.

        Args:
            base_url: The base URL for the API.
            api_key: The API key for 'ApiKey' authentication.
            bearer_token: The Bearer token for 'Bearer' authentication.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.bearer_token = bearer_token
        self.timeout = timeout
        if not self.api_key and not self.bearer_token:
            logger.debug(
                "Warning: BaseHTTPClient initialized without API key or Bearer token."
            )

    def _build_headers(self, json_data: Any = None) -> dict[str, str]:
        """Build request headers."""
        headers = {"Accept": "application/json"}
        if json_data is not None:
            headers["Content-Type"] = "application/json"

        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        elif self.api_key:
            headers["ApiKey"] = self.api_key

        return headers

    def _serialize_json_data(self, json_data: Any) -> Any:
        """Serialize JSON data handling Pydantic models."""
        if json_data is None:
            return None

        # Handle Pydantic v2 and v1 compatibility
        if hasattr(BaseModel, "model_dump"):
            return json.loads(
                json.dumps(
                    json_data,
                    default=lambda o: (
                        o.model_dump(by_alias=True) if isinstance(o, BaseModel) else o
                    ),
                )
            )
        else:
            return json.loads(
                json.dumps(
                    json_data,
                    default=lambda o: (
                        o.dict(by_alias=True) if isinstance(o, BaseModel) else o
                    ),
                )
            )

    def _handle_error_response(self, error: requests.exceptions.HTTPError) -> None:
        """Handle HTTP error responses."""
        response_text = error.response.text if error.response else "No response body"
        status_code = error.response.status_code if error.response else None
        error_details = response_text

        try:
            parsed_error = json.loads(response_text)
            if isinstance(parsed_error, dict):
                error_details = parsed_error.get(
                    "detail", parsed_error.get("message", response_text)
                )
        except json.JSONDecodeError:
            pass

        raise EbioseCloudHTTPError(
            f"HTTP error occurred: {error.request.method} {error.request.url} - {error_details}",
            status_code=status_code,
            response_text=response_text,
        ) from error

    def request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: Any = None,
        json_data: Any = None,
    ) -> Any:
        """Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Form data
            json_data: JSON data

        Returns:
            Response data or None

        Raises:
            EbioseCloudHTTPError: For HTTP errors
            EbioseCloudError: For other request errors
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._build_headers(json_data)
        json_payload = self._serialize_json_data(json_data)

        try:
            response = requests.request(
                method,
                url,
                params=params,
                data=data,
                json=json_payload,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()

            if response.status_code == 204 or not response.content:
                return None
            return response.json()

        except requests.exceptions.HTTPError as e:
            self._handle_error_response(e)
        except requests.exceptions.RequestException as e:
            raise EbioseCloudError(f"Request failed: {e}") from e
