"""Refactored EbioseCloud client with improved architecture."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ebiose.cloud_client.base_client import BaseHTTPClient
from ebiose.cloud_client.endpoints.api_key_endpoints import ApiKeyEndpoints
from ebiose.cloud_client.endpoints.auth_endpoints import AuthEndpoints
from ebiose.cloud_client.endpoints.ecosystem_endpoints import EcosystemEndpoints
from ebiose.cloud_client.endpoints.forge_endpoints import ForgeEndpoints
from ebiose.cloud_client.endpoints.logging_endpoints import LoggingEndpoints
from ebiose.cloud_client.endpoints.user_endpoints import UserEndpoints
from ebiose.core.models.api_models import (
    AgentInputModel,
    AgentOutputModel,
    ApiKeyInputModel,
    ApiKeyOutputModel,
    EcosystemInputModel,
    EcosystemOutputModel,
    ForgeCycleInputModel,
    ForgeInputModel,
    ForgeOutputModel,
    LogEntryInputModel,
    LogEntryOutputModel,
    LoginOutputModel,
    NewCycleOutputModel,
    SelfApiKeyInputModel,
    SelfUserInputModel,
    SignupInputModel,
    UserInputModel,
    UserOutputModel,
)

if TYPE_CHECKING:
    pass


class EbioseCloudClient:
    """Core client for interacting with the EbioseCloud API."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        bearer_token: str | None = None,
        timeout: int = 30,
    ) -> None:
        """Initialize the EbioseCloudClient.

        Args:
            base_url: The base URL for the API.
            api_key: The API key for 'ApiKey' authentication.
            bearer_token: The Bearer token for 'Bearer' authentication.
            timeout: Request timeout in seconds.
        """
        self._http_client = BaseHTTPClient(base_url, api_key, bearer_token, timeout)
        
        # Initialize endpoint handlers
        self.api_keys = ApiKeyEndpoints(self._http_client)
        self.auth = AuthEndpoints(self._http_client)
        self.ecosystems = EcosystemEndpoints(self._http_client)
        self.forges = ForgeEndpoints(self._http_client)
        self.logging = LoggingEndpoints(self._http_client)
        self.users = UserEndpoints(self._http_client)
        
        # Legacy alias for backward compatibility
        self.forge = self.forges

    # --- Legacy wrapper methods for backward compatibility ---
    def get_forges(self) -> list[ForgeOutputModel]:
        """Get all forges."""
        return self.forge.get_forges()

    def add_forge(self, data: ForgeInputModel) -> ForgeOutputModel:
        """Add a new forge."""
        return self.forge.add_forge(data)

    def get_forge(self, forge_uuid: str) -> ForgeOutputModel:
        """Get a specific forge."""
        return self.forge.get_forge(forge_uuid)

    def update_forge(
        self, forge_uuid: str, data: ForgeInputModel
    ) -> ForgeOutputModel:
        """Update a forge."""
        return self.forge.update_forge(forge_uuid, data)

    def delete_forge(self, forge_uuid: str) -> None:
        """Delete a forge."""
        self.forge.delete_forge(forge_uuid)

    def start_new_forge_cycle(
        self,
        forge_uuid: str,
        data: ForgeCycleInputModel,
        override_key: bool | None = None,
    ) -> NewCycleOutputModel:
        """Start a new forge cycle."""
        return self.forge.start_new_forge_cycle(forge_uuid, data, override_key)

    def end_forge_cycle(
        self, forge_cycle_uuid: str, agents_data: list[AgentInputModel]
    ) -> None:
        """End a forge cycle."""
        self.forge.end_forge_cycle(forge_cycle_uuid, agents_data)

    def get_spend(self, forge_cycle_uuid: str) -> float:
        """Get spend for a forge cycle."""
        return self.forge.get_spend(forge_cycle_uuid)

    def select_agents_for_forge_cycle(
        self, forge_cycle_uuid: str, nb_agents: int
    ) -> list[AgentOutputModel]:
        """Select agents for a forge cycle."""
        return self.forge.select_agents_for_forge_cycle(forge_cycle_uuid, nb_agents)

    # --- ApiKey Endpoints (kept here for now) ---
    def add_api_key(self, data: ApiKeyInputModel) -> bool:
        """Add an API key."""
        return self._http_client.request("POST", "/apikeys", json_data=data)

    def get_api_keys(self) -> list[ApiKeyOutputModel]:
        """Get API keys."""
        response = self._http_client.request("GET", "/apikeys")
        return [ApiKeyOutputModel(**item) for item in response]

    def self_add_api_key(self, data: SelfApiKeyInputModel) -> bool:
        """Add an API key for current user."""
        return self._http_client.request("POST", "/apikeys/self", json_data=data)

    def self_get_api_keys(self) -> list[ApiKeyOutputModel]:
        """Get API keys for current user."""
        response = self._http_client.request("GET", "/apikeys/self")
        return [ApiKeyOutputModel(**item) for item in response]

    def get_api_key(self, apiKeyUuid: str) -> ApiKeyOutputModel:
        """Get a specific API key."""
        response = self._http_client.request("GET", f"/apikeys/{apiKeyUuid}")
        return ApiKeyOutputModel(**response)

    def delete_api_key(self, apiKeyUuid: str) -> None:
        """Delete an API key."""
        self._http_client.request("DELETE", f"/apikeys/{apiKeyUuid}")

    def update_api_key(self, apiKeyUuid: str, data: ApiKeyInputModel) -> None:
        """Update an API key."""
        self._http_client.request("PUT", f"/apikeys/{apiKeyUuid}", json_data=data)

    def self_delete_api_key(self, apiKeyUuid: str) -> None:
        """Delete an API key for current user."""
        self._http_client.request("DELETE", f"/apikeys/self/{apiKeyUuid}")

    # --- AuthEndpoints ---
    def login(self, email: str, password: str) -> LoginOutputModel:
        """Login with email and password."""
        response = self._http_client.request(
            "GET", "/auth/login", params={"email": email, "password": password}
        )
        return LoginOutputModel(**response)

    def login_github(self, code: str) -> LoginOutputModel:
        """Login with GitHub."""
        response = self._http_client.request(
            "GET", "/auth/github/login", params={"code": code}
        )
        return LoginOutputModel(**response)

    def sign_up(self, data: SignupInputModel) -> UserOutputModel:
        """Sign up a new user."""
        response = self._http_client.request("POST", "/auth/signup", json_data=data)
        return UserOutputModel(**response)

    def self_update(self, data: SelfUserInputModel) -> UserOutputModel:
        """Update current user profile."""
        response = self._http_client.request(
            "PUT", "/auth/self-update", json_data=data
        )
        return UserOutputModel(**response)

    def update_password(self, new_password: str) -> None:
        """Update password."""
        self._http_client.request(
            "PUT", "/auth/update-password", params={"newPassword": new_password}
        )

    def refresh_token(self, token: str) -> str:
        """Refresh authentication token."""
        return self._http_client.request(
            "GET", "/auth/refresh-token", params={"token": token}
        )

    def user_info(self) -> UserOutputModel:
        """Get current user info."""
        response = self._http_client.request("GET", "/auth/user-info")
        return UserOutputModel(**response)

    # --- EcosystemEndpoints ---
    def create_ecosystem(self, data: EcosystemInputModel) -> EcosystemOutputModel:
        """Create an ecosystem."""
        response = self._http_client.request("POST", "/ecosystems", json_data=data)
        return EcosystemOutputModel(**response)

    def list_ecosystems(self) -> list[EcosystemOutputModel]:
        """List ecosystems."""
        response = self._http_client.request("GET", "/ecosystems")
        return [EcosystemOutputModel(**item) for item in response]

    def get_ecosystem(self, uuid: str) -> EcosystemOutputModel:
        """Get an ecosystem."""
        response = self._http_client.request("GET", f"/ecosystems/{uuid}")
        return EcosystemOutputModel(**response)

    def update_ecosystem(
        self, uuid: str, data: EcosystemInputModel
    ) -> EcosystemOutputModel:
        """Update an ecosystem."""
        response = self._http_client.request(
            "PUT", f"/ecosystems/{uuid}", json_data=data
        )
        return EcosystemOutputModel(**response)

    def delete_ecosystem(self, uuid: str) -> None:
        """Delete an ecosystem."""
        self._http_client.request("DELETE", f"/ecosystems/{uuid}")

    def add_agents_to_ecosystem(
        self, ecosystem_uuid: str, agents_data: list[AgentInputModel]
    ) -> None:
        """Add agents to ecosystem."""
        self._http_client.request(
            "POST", f"/ecosystems/{ecosystem_uuid}/agents", json_data=agents_data
        )

    def list_agents_in_ecosystem(
        self, ecosystem_uuid: str
    ) -> list[AgentOutputModel]:
        """List agents in ecosystem."""
        response = self._http_client.request(
            "GET", f"/ecosystems/{ecosystem_uuid}/agents"
        )
        return [AgentOutputModel(**item) for item in response]

    def delete_agents_from_ecosystem(
        self, ecosystem_uuid: str, agent_uuids: list[str]
    ) -> None:
        """Delete agents from ecosystem."""
        self._http_client.request(
            "DELETE",
            f"/ecosystems/{ecosystem_uuid}/agents",
            json_data=agent_uuids,
        )

    def get_agent_in_ecosystem(
        self, ecosystem_uuid: str, agent_uuid: str
    ) -> AgentOutputModel:
        """Get agent in ecosystem."""
        response = self._http_client.request(
            "GET", f"/ecosystems/{ecosystem_uuid}/agent/{agent_uuid}"
        )
        return AgentOutputModel(**response)

    def update_agent_in_ecosystem(
        self,
        ecosystem_uuid: str,
        agent_uuid: str,
        agent_data: AgentInputModel,
    ) -> AgentOutputModel:
        """Update agent in ecosystem."""
        response = self._http_client.request(
            "PUT",
            f"/ecosystems/{ecosystem_uuid}/agent/{agent_uuid}",
            json_data=agent_data,
        )
        return AgentOutputModel(**response)

    def add_single_agent_to_ecosystem(
        self, ecosystem_uuid: str, agent_data: AgentInputModel
    ) -> AgentOutputModel:
        """Add single agent to ecosystem."""
        response = self._http_client.request(
            "POST", f"/ecosystems/{ecosystem_uuid}/agent", json_data=agent_data
        )
        return AgentOutputModel(**response)

    # --- Additional forge methods ---
    def deduct_compute_banks_for_forge_cycle(
        self, forge_cycle_uuid: str, deductions: dict[str, float]
    ) -> None:
        """Deduct compute banks for forge cycle."""
        self.forge.deduct_compute_banks_for_forge_cycle(forge_cycle_uuid, deductions)

    def record_forge_cycle_usage(self, forge_cycle_uuid: str, cost: float) -> None:
        """Record forge cycle usage."""
        self.forge.record_forge_cycle_usage(forge_cycle_uuid, cost)

    def add_agent_during_forge_cycle(
        self, forge_cycle_uuid: str, data: AgentInputModel
    ) -> AgentOutputModel:
        """Add agent during forge cycle."""
        return self.forge.add_agent_during_forge_cycle(forge_cycle_uuid, data)

    def add_agents_during_forge_cycle(
        self, forge_cycle_uuid: str, agents_data: list[AgentInputModel]
    ) -> None:
        """Add agents during forge cycle."""
        self.forge.add_agents_during_forge_cycle(forge_cycle_uuid, agents_data)

    # --- Logging Endpoint ---
    def add_log_entry(self, data: LogEntryInputModel) -> LogEntryOutputModel:
        """Add log entry."""
        response = self._http_client.request("POST", "/logging", json_data=data)
        return LogEntryOutputModel(**response)

    # --- Users Endpoints ---
    def create_user(self, data: UserInputModel) -> UserOutputModel:
        """Create a user."""
        response = self._http_client.request("POST", "/users", json_data=data)
        return UserOutputModel(**response)

    def list_users(self) -> list[UserOutputModel]:
        """List users."""
        response = self._http_client.request("GET", "/users")
        return [UserOutputModel(**item) for item in response]

    def get_user(self, userUuid: str) -> UserOutputModel:
        """Get a user."""
        response = self._http_client.request("GET", f"/users/{userUuid}")
        return UserOutputModel(**response)

    def update_user(self, userUuid: str, data: UserInputModel) -> None:
        """Update a user."""
        self._http_client.request("PUT", f"/users/{userUuid}", json_data=data)

    def delete_user(self, userUuid: str) -> None:
        """Delete a user."""
        self._http_client.request("DELETE", f"/users/{userUuid}")

    def get_user_by_email(self, email: str) -> UserOutputModel:
        """Get user by email."""
        response = self._http_client.request("GET", f"/users/email/{email}")
        return UserOutputModel(**response)
