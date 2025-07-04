"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ebiose.core.models.api_models import LoginOutputModel, UserOutputModel
from ebiose.core.models.auth_models import SelfUserInputModel, SignupInputModel

if TYPE_CHECKING:
    from ebiose.cloud_client.base_client import BaseHTTPClient


class AuthEndpoints:
    """Authentication-related API endpoints."""
    
    def __init__(self, client: BaseHTTPClient):
        self.client = client
    
    def login(self, email: str, password: str) -> LoginOutputModel:
        """Login with email and password."""
        return LoginOutputModel(**self.client.request(
            "GET", "/auth/login", 
            params={"email": email, "password": password}
        ))
    
    def login_github(self, code: str) -> LoginOutputModel:
        """Login with GitHub OAuth code."""
        return LoginOutputModel(**self.client.request(
            "GET", "/auth/github/login", 
            params={"code": code}
        ))
    
    def sign_up(self, data: SignupInputModel) -> UserOutputModel:
        """Register a new user."""
        return UserOutputModel(**self.client.request(
            "POST", "/auth/signup", 
            json_data=data
        ))
    
    def self_update(self, data: SelfUserInputModel) -> UserOutputModel:
        """Update current user's profile."""
        return UserOutputModel(**self.client.request(
            "PUT", "/auth/self-update", 
            json_data=data
        ))
    
    def update_password(self, new_password: str) -> None:
        """Update current user's password."""
        self.client.request(
            "PUT", "/auth/update-password", 
            params={"newPassword": new_password}
        )
    
    def refresh_token(self, token: str) -> str:
        """Refresh authentication token."""
        return self.client.request(
            "GET", "/auth/refresh-token", 
            params={"token": token}
        )
    
    def user_info(self) -> UserOutputModel:
        """Get current user information."""
        return UserOutputModel(**self.client.request("GET", "/auth/user-info"))
