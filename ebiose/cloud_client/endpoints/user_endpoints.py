"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ebiose.core.models.api_models import UserOutputModel
from ebiose.core.models.auth_models import UserInputModel

if TYPE_CHECKING:
    from ebiose.cloud_client.base_client import BaseHTTPClient


class UserEndpoints:
    """User management endpoints."""
    
    def __init__(self, client: BaseHTTPClient) -> None:
        self.client = client
    
    def create_user(self, data: UserInputModel) -> UserOutputModel:
        """Create a new user (admin operation)."""
        return UserOutputModel(**self.client.request("POST", "/users", json_data=data))
    
    def list_users(self) -> list[UserOutputModel]:
        """List all users (admin operation)."""
        return [UserOutputModel(**item) for item in self.client.request("GET", "/users")]
    
    def get_user(self, user_uuid: str) -> UserOutputModel:
        """Get a specific user (admin operation)."""
        return UserOutputModel(**self.client.request("GET", f"/users/{user_uuid}"))
    
    def update_user(self, user_uuid: str, data: UserInputModel) -> None:
        """Update a user (admin operation)."""
        self.client.request("PUT", f"/users/{user_uuid}", json_data=data)
    
    def delete_user(self, user_uuid: str) -> None:
        """Delete a user (admin operation)."""
        self.client.request("DELETE", f"/users/{user_uuid}")
    
    def get_user_by_email(self, email: str) -> UserOutputModel:
        """Get a user by email (admin operation)."""
        return UserOutputModel(**self.client.request("GET", f"/users/email/{email}"))
