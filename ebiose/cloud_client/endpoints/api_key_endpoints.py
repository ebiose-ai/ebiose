"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ebiose.core.models.api_models import ApiKeyOutputModel

if TYPE_CHECKING:
    from ebiose.cloud_client.base_client import BaseHTTPClient


class ApiKeyInputModel:
    """Input model for creating or updating an API key."""
    
    def __init__(self, user_uuid: str | None, expiration_date: str):
        self.userUuid = user_uuid
        self.expirationDate = expiration_date


class SelfApiKeyInputModel:
    """Input model for creating a new API key for the current user."""
    
    def __init__(self, expiration_date: str):
        self.expirationDate = expiration_date


class ApiKeyEndpoints:
    """API key management endpoints."""
    
    def __init__(self, client: BaseHTTPClient) -> None:
        self.client = client
    
    def add_api_key(self, data: ApiKeyInputModel) -> bool:
        """Add a new API key (admin operation)."""
        return self.client.request("POST", "/apikeys", json_data=data)
    
    def get_api_keys(self) -> list[ApiKeyOutputModel]:
        """Get all API keys (admin operation)."""
        return [ApiKeyOutputModel(**item) for item in self.client.request("GET", "/apikeys")]
    
    def self_add_api_key(self, data: SelfApiKeyInputModel) -> bool:
        """Add a new API key for the current user."""
        return self.client.request("POST", "/apikeys/self", json_data=data)
    
    def self_get_api_keys(self) -> list[ApiKeyOutputModel]:
        """Get current user's API keys."""
        return [ApiKeyOutputModel(**item) for item in self.client.request("GET", "/apikeys/self")]
    
    def get_api_key(self, api_key_uuid: str) -> ApiKeyOutputModel:
        """Get a specific API key."""
        return ApiKeyOutputModel(**self.client.request("GET", f"/apikeys/{api_key_uuid}"))
    
    def delete_api_key(self, api_key_uuid: str) -> None:
        """Delete an API key (admin operation)."""
        self.client.request("DELETE", f"/apikeys/{api_key_uuid}")
    
    def update_api_key(self, api_key_uuid: str, data: ApiKeyInputModel) -> None:
        """Update an API key (admin operation)."""
        self.client.request("PUT", f"/apikeys/{api_key_uuid}", json_data=data)
    
    def self_delete_api_key(self, api_key_uuid: str) -> None:
        """Delete current user's API key."""
        self.client.request("DELETE", f"/apikeys/self/{api_key_uuid}")
