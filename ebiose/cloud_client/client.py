import json
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel, Field


# --- Custom Exceptions ---
class EbioseCloudError(Exception):
    """Base exception for EbioseCloud API errors."""

    def __init__(self, message, status_code: int | None = None, response_text: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

    def __str__(self):
        return f"{super().__str__()} (Status Code: {self.status_code}, Response: {self.response_text or 'N/A'})"


class EbioseCloudHTTPError(EbioseCloudError):
    """Exception for HTTP errors (4xx, 5xx)."""


class EbioseCloudAuthError(EbioseCloudError):
    """Exception for authentication-related errors."""


# --- Enums (Updated with AgentType) ---
class Role(int, Enum):
    """Enum for User Roles."""
    USER = 1
    ADMIN = 2

class AgentType(int, Enum):
    """Enum for Agent Types, as defined in the new swagger spec."""
    GENERATOR = 0
    DISCRIMINATOR = 1
    CURATOR = 2


# --- Pydantic Models (Updated based on new swagger.json) ---
# These models define the data structures for API requests and responses.

class AgentEngineInputModel(BaseModel):
    """Input model for agent engine configuration."""
    engineType: str | None = None
    configuration: str | None = None


class AgentEngineOutputModel(BaseModel):
    """Output model for agent engine configuration."""
    engineType: str | None = None
    configuration: str | None = None


class ApiKeyInputModel(BaseModel):
    """Input model for creating or updating an API key."""
    userUuid: str | None = None
    expirationDate: datetime


class SelfApiKeyInputModel(BaseModel):
    """Input model for creating a new API key for the current user."""
    expirationDate: datetime


class EcosystemInputModel(BaseModel):
    """Input model for creating or updating an ecosystem."""
    communityCreditsAvailable: float


class ForgeCycleInputModel(BaseModel):
    """Input model for starting a new forge cycle."""
    nAgentsInPopulation: int
    nSelectedAgentsFromEcosystem: int
    nBestAgentsToReturn: int
    replacementRatio: float
    tournamentSizeRatio: float
    localResultsPath: str | None = None
    budget: float


class SelfUserInputModel(BaseModel):
    """Input model for the current user updating their own profile."""
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    githubId: str | None = None
    password: str | None = None  # Be cautious with sending passwords


class SignupInputModel(BaseModel):
    """Input model for new user registration."""
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    githubId: str | None = None
    password: str | None = None


class UserInputModel(BaseModel):
    """Input model for creating or updating a user (admin operation)."""
    role: Role
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    githubId: str | None = None
    creditsLimit: float
    password: str | None = None


class UserOutputModel(BaseModel):
    """Output model representing a user's data."""
    uuid: str | None = None
    role: Role
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    githubId: str | None = None
    apiKeys: list["ApiKeyOutputModel"] | None = None
    creditsLimit: float
    creditsUsed: float
    availableCredits: float = Field(..., description="Read-only field")


class ApiKeyOutputModel(BaseModel):
    """Output model representing an API key."""
    uuid: str | None = None
    key: str | None = None
    createdAt: datetime
    expirationDate: datetime
    user: UserOutputModel | None = None


class AgentInputModel(BaseModel):
    """Input model for creating or updating an agent. Reflects new fields."""
    name: str | None = None
    description: str | None = None
    architectAgentUuid: str | None = None
    geneticOperatorAgentUuid: str | None = None
    agentEngine: AgentEngineInputModel | None = None
    descriptionEmbedding: list[float] | None = None
    parentAgentUuids: list[str] | None = None
    agentType: AgentType


class AgentOutputModel(BaseModel):
    """Output model representing an agent. Reflects new fields."""
    uuid: str | None = None
    name: str | None = None
    description: str | None = None
    ecosystem: Optional["EcosystemOutputModel"] = None
    architectAgentUuid: str | None = None
    geneticOperatorAgentUuid: str | None = None
    agentEngine: AgentEngineOutputModel | None = None
    descriptionEmbedding: list[float] | None = None
    computeBankInDollars: float
    parentAgentUuids: list[str] | None = None
    childAgentUuids: list[str] | None = None
    agentType: AgentType


class EcosystemOutputModel(BaseModel):
    """Output model representing an ecosystem."""
    uuid: str | None = None
    communityCreditsAvailable: float
    agents: list[AgentOutputModel] | None = None


class LoginOutputModel(BaseModel):
    """Output model for a successful login."""
    user: UserOutputModel | None = None
    token: str | None = None


class NewCycleOutputModel(BaseModel):
    """Output model after starting a new forge cycle. Reflects new fields."""
    liteLLMKey: str | None = None
    forgeCycleUuid: str | None = None
    baseUrl: str | None = None


# --- New Models for Forge Endpoints ---
class ForgeInputModel(BaseModel):
    """Input model for creating or updating a forge."""
    name: str | None = None
    description: str | None = None
    ecosystemUuid: str | None = None

class ForgeCycleOutputModel(BaseModel):
    """Output model representing a forge cycle's state."""
    uuid: str | None = None
    forgeDescription: str | None = None
    forgeName: str | None = None
    liteLLMKey: str | None = None
    nAgentsInPopulation: int
    nSelectedAgentsFromEcosystem: int
    nBestAgentsToReturn: int
    replacementRatio: float
    tournamentSizeRatio: float
    localResultsPath: str | None = None
    budget: float
    isRunning: bool

class ForgeOutputModel(BaseModel):
    """Output model representing a forge."""
    uuid: str | None = None
    name: str | None = None
    description: str | None = None
    forgeCycles: list[ForgeCycleOutputModel] | None = None


# Rebuild models to resolve forward references
# This is crucial for Pydantic to correctly link models defined with string type hints.
UserOutputModel.model_rebuild()
ApiKeyOutputModel.model_rebuild()
AgentOutputModel.model_rebuild()
EcosystemOutputModel.model_rebuild()


# --- Core API Client ---
class EbioseCloudClient:
    """Core client for interacting with the EbioseCloud API."""

    def __init__(self, base_url: str, api_key: str | None = None, bearer_token: str | None = None, timeout: int = 30):
        """
        Initializes the EbioseCloudClient.

        Args:
            base_url: The base URL for the API (e.g., "http://localhost:8000").
            api_key: The API key for 'ApiKey' authentication.
            bearer_token: The Bearer token for 'Bearer' authentication.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.bearer_token = bearer_token
        self.timeout = timeout
        if not self.api_key and not self.bearer_token:
            print("Warning: EbioseCloudClient initialized without API key or Bearer token. Most operations may fail.")

    def _request(self, method: str, endpoint: str, params: dict[str, Any] | None = None, data: Any | None = None, json_data: Any | None = None) -> Any:
        """
        Internal method to make an HTTP request to the API.

        Handles URL construction, authentication headers, request execution, and error handling.

        Args:
            method: HTTP method (e.g., "GET", "POST").
            endpoint: API endpoint path (e.g., "/users").
            params: URL query parameters.
            data: Request body for form-encoded data.
            json_data: Request body for JSON-encoded data.

        Returns:
            The parsed JSON response from the API.

        Raises:
            EbioseCloudHTTPError: For HTTP status codes 4xx or 5xx.
            EbioseCloudError: For other network or request-related errors.
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"Accept": "application/json"}
        if json_data is not None:
            headers["Content-Type"] = "application/json"
        
        # Add authentication headers. Bearer token is preferred if both are available.
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        elif self.api_key:
            headers["ApiKey"] = self.api_key
        
        try:
            response = requests.request(method, url, params=params, data=data, json=json_data, headers=headers, timeout=self.timeout)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            
            # Handle successful responses with no content
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors specifically
            response_text = e.response.text if e.response is not None else "No response body"
            status_code = e.response.status_code if e.response is not None else None
            error_details = response_text
            try:
                # Try to parse a more specific error message from the JSON response
                parsed_error = json.loads(response_text)
                if isinstance(parsed_error, dict):
                    error_details = parsed_error.get("detail", parsed_error.get("message", response_text))
            except json.JSONDecodeError:
                pass  # Use the raw text if it's not JSON
            raise EbioseCloudHTTPError(f"HTTP error occurred: {e.request.method} {e.request.url} - {error_details}", status_code=status_code, response_text=response_text) from e
        except requests.exceptions.RequestException as e:
            # Handle other request exceptions (e.g., network issues)
            raise EbioseCloudError(f"Request failed: {e}") from e

    # --- ApiKey Endpoints ---
    def add_api_key(self, data: ApiKeyInputModel) -> bool:
        """Corresponds to POST /apikeys."""
        return self._request("POST", "/apikeys", json_data=data.model_dump(by_alias=True))

    def get_api_keys(self) -> list[ApiKeyOutputModel]:
        """Corresponds to GET /apikeys."""
        response_data = self._request("GET", "/apikeys")
        return [ApiKeyOutputModel(**item) for item in response_data]

    def self_add_api_key(self, data: SelfApiKeyInputModel) -> bool:
        """Corresponds to POST /apikeys/self."""
        return self._request("POST", "/apikeys/self", json_data=data.model_dump(by_alias=True))

    def self_get_api_keys(self) -> list[ApiKeyOutputModel]:
        """Corresponds to GET /apikeys/self."""
        response_data = self._request("GET", "/apikeys/self")
        return [ApiKeyOutputModel(**item) for item in response_data]

    def get_api_key(self, apiKeyUuid: str) -> ApiKeyOutputModel:
        """Corresponds to GET /apikeys/{apiKeyUuid}."""
        response_data = self._request("GET", f"/apikeys/{apiKeyUuid}")
        return ApiKeyOutputModel(**response_data)

    def delete_api_key(self, apiKeyUuid: str) -> None:
        """Corresponds to DELETE /apikeys/{apiKeyUuid}."""
        self._request("DELETE", f"/apikeys/{apiKeyUuid}")

    def update_api_key(self, apiKeyUuid: str, data: ApiKeyInputModel) -> None:
        """Corresponds to PUT /apikeys/{apiKeyUuid}."""
        self._request("PUT", f"/apikeys/{apiKeyUuid}", json_data=data.model_dump(by_alias=True))

    def self_delete_api_key(self, apiKeyUuid: str) -> None:
        """Corresponds to DELETE /apikeys/self/{apiKeyUuid}."""
        self._request("DELETE", f"/apikeys/self/{apiKeyUuid}")

    # --- AuthEndpoints ---
    def login(self, email: str, password: str) -> LoginOutputModel:
        """Corresponds to GET /auth/login."""
        params = {"email": email, "password": password}
        response_data = self._request("GET", "/auth/login", params=params)
        return LoginOutputModel(**response_data)

    def login_github(self, code: str) -> LoginOutputModel:
        """New: Corresponds to GET /auth/github/login."""
        params = {"code": code}
        response_data = self._request("GET", "/auth/github/login", params=params)
        return LoginOutputModel(**response_data)

    def sign_up(self, data: SignupInputModel) -> UserOutputModel:
        """Corresponds to POST /auth/signup."""
        response_data = self._request("POST", "/auth/signup", json_data=data.model_dump(by_alias=True))
        return UserOutputModel(**response_data)

    def self_update(self, data: SelfUserInputModel) -> UserOutputModel:
        """Corresponds to PUT /auth/self-update."""
        response_data = self._request("PUT", "/auth/self-update", json_data=data.model_dump(by_alias=True))
        return UserOutputModel(**response_data)

    def update_password(self, new_password: str) -> None:
        """Corresponds to PUT /auth/update-password."""
        self._request("PUT", "/auth/update-password", params={"newPassword": new_password})

    def refresh_token(self, token: str) -> str:
        """Corresponds to GET /auth/refresh-token."""
        return self._request("GET", "/auth/refresh-token", params={"token": token})

    def user_info(self) -> UserOutputModel:
        """Corresponds to GET /auth/user-info."""
        response_data = self._request("GET", "/auth/user-info")
        return UserOutputModel(**response_data)

    # --- EcosystemEndpoints ---
    def create_ecosystem(self, data: EcosystemInputModel) -> EcosystemOutputModel:
        """Corresponds to POST /ecosystems."""
        response_data = self._request("POST", "/ecosystems", json_data=data.model_dump(by_alias=True))
        return EcosystemOutputModel(**response_data)

    def list_ecosystems(self) -> list[EcosystemOutputModel]:
        """Corresponds to GET /ecosystems."""
        response_data = self._request("GET", "/ecosystems")
        return [EcosystemOutputModel(**item) for item in response_data]

    def get_ecosystem(self, uuid: str) -> EcosystemOutputModel:
        """Corresponds to GET /ecosystems/{uuid}."""
        response_data = self._request("GET", f"/ecosystems/{uuid}")
        return EcosystemOutputModel(**response_data)

    def update_ecosystem(self, uuid: str, data: EcosystemInputModel) -> EcosystemOutputModel:
        """Corresponds to PUT /ecosystems/{uuid}."""
        response_data = self._request("PUT", f"/ecosystems/{uuid}", json_data=data.model_dump(by_alias=True))
        return EcosystemOutputModel(**response_data)

    def delete_ecosystem(self, uuid: str) -> None:
        """Corresponds to DELETE /ecosystems/{uuid}."""
        self._request("DELETE", f"/ecosystems/{uuid}")

    def add_agents_to_ecosystem(self, ecosystem_uuid: str, agents_data: list[AgentInputModel]) -> None:
        """Corresponds to POST /ecosystems/{ecosystemUuid}/agents."""
        json_payload = [agent.model_dump(by_alias=True) for agent in agents_data]
        self._request("POST", f"/ecosystems/{ecosystem_uuid}/agents", json_data=json_payload)

    def list_agents_in_ecosystem(self, ecosystem_uuid: str) -> list[AgentOutputModel]:
        """Corresponds to GET /ecosystems/{ecosystemUuid}/agents."""
        response_data = self._request("GET", f"/ecosystems/{ecosystem_uuid}/agents")
        return [AgentOutputModel(**item) for item in response_data]

    def delete_agents_from_ecosystem(self, ecosystem_uuid: str, agent_uuids: list[str]) -> None:
        """Corresponds to DELETE /ecosystems/{ecosystemUuid}/agents."""
        self._request("DELETE", f"/ecosystems/{ecosystem_uuid}/agents", json_data=agent_uuids)

    def add_single_agent_to_ecosystem(self, ecosystem_uuid: str, agent_data: AgentInputModel) -> AgentOutputModel:
        """Corresponds to POST /ecosystems/{ecosystemUuid}/agent."""
        response_data = self._request("POST", f"/ecosystems/{ecosystem_uuid}/agent", json_data=agent_data.model_dump(by_alias=True))
        return AgentOutputModel(**response_data)

    def get_agent_in_ecosystem(self, ecosystem_uuid: str, agent_uuid: str) -> AgentOutputModel:
        """New: Corresponds to GET /ecosystems/{ecosystemUuid}/agent/{agentUuid}."""
        response_data = self._request("GET", f"/ecosystems/{ecosystem_uuid}/agent/{agent_uuid}")
        return AgentOutputModel(**response_data)

    def update_agent_in_ecosystem(self, ecosystem_uuid: str, agent_uuid: str, agent_data: AgentInputModel) -> AgentOutputModel:
        """Corresponds to PUT /ecosystems/{ecosystemUuid}/agent/{agentUuid}."""
        response_data = self._request("PUT", f"/ecosystems/{ecosystem_uuid}/agent/{agent_uuid}", json_data=agent_data.model_dump(by_alias=True))
        return AgentOutputModel(**response_data)

    # --- ForgeEndpoints ---
    def get_forges(self) -> list[ForgeOutputModel]:
        """Corresponds to GET /forges."""
        response_data = self._request("GET", "/forges")
        return [ForgeOutputModel(**item) for item in response_data]

    def add_forge(self, data: ForgeInputModel) -> ForgeOutputModel:
        """Corresponds to POST /forges."""
        response_data = self._request("POST", "/forges", json_data=data.model_dump(by_alias=True),)
        return ForgeOutputModel(**response_data)

    def get_forge(self, forge_uuid: str) -> ForgeOutputModel:
        """Corresponds to GET /forges/{forgeUuid}."""
        response_data = self._request("GET", f"/forges/{forge_uuid}")
        return ForgeOutputModel(**response_data)
    
    def update_forge(self, forge_uuid: str, data: ForgeInputModel) -> ForgeOutputModel:
        """Corresponds to PUT /forges/{forgeUuid}."""
        response_data = self._request("PUT", f"/forges/{forge_uuid}", json_data=data.model_dump(by_alias=True))
        return ForgeOutputModel(**response_data)

    def delete_forge(self, forge_uuid: str) -> None:
        """Corresponds to DELETE /forges/{forgeUuid}."""
        self._request("DELETE", f"/forges/{forge_uuid}")
        
    def start_new_forge_cycle(self, forge_uuid: str, data: ForgeCycleInputModel, override_key: bool | None = None) -> NewCycleOutputModel:
        """Corresponds to POST /forges/{forgeUuid}/cycles/start."""
        params = {"overrideKey": override_key} if override_key is not None else {}
        response_data = self._request("POST", f"/forges/{forge_uuid}/cycles/start", params=params, json_data=data.model_dump(by_alias=True))
        return NewCycleOutputModel(**response_data)

    def end_forge_cycle(self, forge_cycle_uuid: str, agents_data: list[AgentInputModel]) -> None:
        """Corresponds to POST /forges/cycles/{forgeCycleUuid}/end."""
        json_payload = [agent.model_dump(by_alias=True) for agent in agents_data]
        self._request("POST", f"/forges/cycles/{forge_cycle_uuid}/end", json_data=json_payload)

    def get_spend(self, forge_cycle_uuid: str) -> float:
        """Corresponds to GET /forges/cycles/{forgeCycleUuid}/spend."""
        return self._request("GET", f"/forges/cycles/{forge_cycle_uuid}/spend")
    
    def record_forge_cycle_usage(self, forge_cycle_uuid: str, cost: float) -> None:
        """Corresponds to POST /forges/cycles/{forgeCycleUuid}/usage."""
        params = {"cost": cost}
        self._request("POST", f"/forges/cycles/{forge_cycle_uuid}/usage", params=params)

    def select_agents_for_forge_cycle(self, forge_cycle_uuid: str, nb_agents: int) -> list[AgentOutputModel]:
        """Updated Path: Corresponds to GET /forges/cycles/{forgeCycleUuid}/select-agents."""
        params = {"nbAgents": nb_agents}
        response_data = self._request("GET", f"/forges/cycles/{forge_cycle_uuid}/select-agents", params=params)
        return [AgentOutputModel(**item) for item in response_data]

    def deduct_compute_banks_for_forge_cycle(self, forge_cycle_uuid: str, deductions: dict[str, float]) -> None:
        """Updated Path: Corresponds to POST /forges/cycles/{forgeCycleUuid}/deduct-compute-banks."""
        self._request("POST", f"/forges/cycles/{forge_cycle_uuid}/deduct-compute-banks", json_data=deductions)

    # --- Users Endpoints ---
    def create_user(self, data: UserInputModel) -> UserOutputModel:
        """Corresponds to POST /users."""
        response_data = self._request("POST", "/users", json_data=data.model_dump(by_alias=True))
        return UserOutputModel(**response_data)

    def list_users(self) -> list[UserOutputModel]:
        """Corresponds to GET /users."""
        response_data = self._request("GET", "/users")
        return [UserOutputModel(**item) for item in response_data]

    def get_user(self, userUuid: str) -> UserOutputModel:
        """Corresponds to GET /users/{userUuid}."""
        response_data = self._request("GET", f"/users/{userUuid}")
        return UserOutputModel(**response_data)

    def update_user(self, userUuid: str, data: UserInputModel) -> None:
        """Corresponds to PUT /users/{userUuid}."""
        self._request("PUT", f"/users/{userUuid}", json_data=data.model_dump(by_alias=True))

    def delete_user(self, userUuid: str) -> None:
        """Corresponds to DELETE /users/{userUuid}."""
        self._request("DELETE", f"/users/{userUuid}")

    def get_user_by_email(self, email: str) -> UserOutputModel:
        """Corresponds to GET /users/email/{email}."""
        response_data = self._request("GET", f"/users/email/{email}")
        return UserOutputModel(**response_data)

# --- Facade API Client ---
class EbioseAPIClient:
    """Facade client providing a high-level, user-friendly interface to the EbioseCloud API."""
    _client: EbioseCloudClient | None = None
    _base_url: str | None = None

    @classmethod
    def set_client_credentials(cls, base_url: str, api_key: str | None = None, bearer_token: str | None = None) -> None:
        """
        Set the API client with the provided base URL and API key or Bearer token.
        This method initializes or re-initializes the internal client.
        """
        cls._base_url = base_url
        cls._client = EbioseCloudClient(base_url=base_url, api_key=api_key, bearer_token=bearer_token)
        print(f"EbioseCloudClient initialized for base URL: {base_url}")

    @classmethod
    def _get_client(cls) -> EbioseCloudClient:
        """
        Ensures the client is initialized and returns it.
        Raises EbioseCloudAuthError if the client is not set.
        """
        if cls._client is None:
            raise EbioseCloudAuthError("Client not initialized. Call EbioseAPIClient.set_client_credentials() first.")
        return cls._client
    
    @classmethod
    def _handle_request(cls, action_description: str, api_call, *args, **kwargs):
        """
        Generic internal request handler for the facade.
        Provides consistent logging and error handling for all facade methods.
        """
        try:
            print(f"\nAttempting to {action_description}...")
            result = api_call(*args, **kwargs)
            print(f"Successfully finished: {action_description}.")
            return result
        except EbioseCloudHTTPError as e:
            print(f"An API HTTP error occurred while {action_description}: {e}")
            raise
        except EbioseCloudError as e:
            print(f"An API error occurred while {action_description}: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred while {action_description}: {e}")
            raise

    # --- ApiKey Facade ---
    def add_new_api_key(cls, data: ApiKeyInputModel) -> bool:
        """Creates a new API key."""
        return cls._handle_request("add new API key", cls._get_client().add_api_key, data=data)

    def list_all_api_keys(cls) -> list[ApiKeyOutputModel]:
        """Retrieves all API keys (admin operation)."""
        return cls._handle_request("list all API keys", cls._get_client().get_api_keys)
    
    def add_self_api_key(cls, data: SelfApiKeyInputModel) -> bool:
        """Creates a new API key for the currently authenticated user."""
        return cls._handle_request("add self API key", cls._get_client().self_add_api_key, data=data)

    def list_self_api_keys(cls) -> list[ApiKeyOutputModel]:
        """Retrieves API keys for the currently authenticated user."""
        return cls._handle_request("list self API keys", cls._get_client().self_get_api_keys)

    def get_specific_api_key(cls, apiKeyUuid: str) -> ApiKeyOutputModel:
        """Retrieves a specific API key by its UUID."""
        return cls._handle_request(f"get API key {apiKeyUuid}", cls._get_client().get_api_key, apiKeyUuid=apiKeyUuid)

    def remove_api_key(cls, apiKeyUuid: str) -> None:
        """Deletes a specific API key by its UUID."""
        return cls._handle_request(f"delete API key {apiKeyUuid}", cls._get_client().delete_api_key, apiKeyUuid=apiKeyUuid)

    def modify_api_key(cls, apiKeyUuid: str, data: ApiKeyInputModel) -> None:
        """Updates a specific API key by its UUID."""
        return cls._handle_request(f"update API key {apiKeyUuid}", cls._get_client().update_api_key, apiKeyUuid=apiKeyUuid, data=data)

    def remove_self_api_key(cls, apiKeyUuid: str) -> None:
        """Deletes a specific API key belonging to the current user."""
        return cls._handle_request(f"delete self API key {apiKeyUuid}", cls._get_client().self_delete_api_key, apiKeyUuid=apiKeyUuid)

    # --- Auth Facade ---
    def perform_login(cls, email: str, password: str) -> LoginOutputModel:
        """Authenticates a user with email and password."""
        return cls._handle_request(f"perform login for {email}", cls._get_client().login, email=email, password=password)

    def perform_github_login(cls, code: str) -> LoginOutputModel:
        """Authenticates a user using a GitHub OAuth code."""
        return cls._handle_request("perform GitHub login", cls._get_client().login_github, code=code)

    def perform_sign_up(cls, data: SignupInputModel) -> UserOutputModel:
        """Registers a new user."""
        return cls._handle_request("perform user sign up", cls._get_client().sign_up, data=data)
    
    def perform_self_update(cls, data: SelfUserInputModel) -> UserOutputModel:
        """Updates the profile of the currently authenticated user."""
        return cls._handle_request("perform self user update", cls._get_client().self_update, data=data)

    def change_password(cls, new_password: str) -> None:
        """Updates the password for the currently authenticated user."""
        return cls._handle_request("update password", cls._get_client().update_password, new_password=new_password)
    
    def get_refresh_token(cls, token: str) -> str:
        """Obtains a new JWT by providing a valid refresh token."""
        return cls._handle_request("refresh token", cls._get_client().refresh_token, token=token)

    def get_current_user_info(cls) -> UserOutputModel:
        """Retrieves the profile of the currently authenticated user."""
        return cls._handle_request("get current user info", cls._get_client().user_info)

    # --- Ecosystem Facade ---
    def get_ecosystems(cls) -> list[EcosystemOutputModel]:
        """Retrieves a list of all ecosystems."""
        return cls._handle_request("list all ecosystems", cls._get_client().list_ecosystems)
        
    def make_ecosystem(cls, data: EcosystemInputModel) -> EcosystemOutputModel:
        """Creates a new ecosystem."""
        return cls._handle_request("create ecosystem", cls._get_client().create_ecosystem, data=data)

    def get_specific_ecosystem(cls, uuid: str) -> EcosystemOutputModel:
        """Retrieves a specific ecosystem by its UUID."""
        return cls._handle_request(f"get ecosystem {uuid}", cls._get_client().get_ecosystem, uuid=uuid)

    def modify_ecosystem(cls, uuid: str, data: EcosystemInputModel) -> EcosystemOutputModel:
        """Updates a specific ecosystem by its UUID."""
        return cls._handle_request(f"update ecosystem {uuid}", cls._get_client().update_ecosystem, uuid=uuid, data=data)

    def remove_ecosystem(cls, uuid: str) -> None:
        """Deletes a specific ecosystem by its UUID."""
        return cls._handle_request(f"delete ecosystem {uuid}", cls._get_client().delete_ecosystem, uuid=uuid)

    def add_new_agents_to_ecosystem(cls, ecosystem_uuid: str, agents_data: list[AgentInputModel]) -> None:
        """Adds a batch of new agents to a specific ecosystem."""
        return cls._handle_request(f"add agents to ecosystem {ecosystem_uuid}", cls._get_client().add_agents_to_ecosystem, ecosystem_uuid=ecosystem_uuid, agents_data=agents_data)

    def list_all_agents_in_ecosystem(cls, ecosystem_uuid: str) -> list[AgentOutputModel]:
        """Lists all agents within a specific ecosystem."""
        return cls._handle_request(f"list agents in ecosystem {ecosystem_uuid}", cls._get_client().list_agents_in_ecosystem, ecosystem_uuid=ecosystem_uuid)

    def remove_agents_from_ecosystem(cls, ecosystem_uuid: str, agent_uuids: list[str]) -> None:
        """Removes a list of agents from a specific ecosystem by their UUIDs."""
        return cls._handle_request(f"delete agents from ecosystem {ecosystem_uuid}", cls._get_client().delete_agents_from_ecosystem, ecosystem_uuid=ecosystem_uuid, agent_uuids=agent_uuids)

    def add_single_agent(cls, ecosystem_uuid: str, agent_data: AgentInputModel) -> AgentOutputModel:
        """Adds a single new agent to a specific ecosystem."""
        return cls._handle_request(f"add single agent to ecosystem {ecosystem_uuid}", cls._get_client().add_single_agent_to_ecosystem, ecosystem_uuid=ecosystem_uuid, agent_data=agent_data)

    def get_specific_agent(cls, ecosystem_uuid: str, agent_uuid: str) -> AgentOutputModel:
        """Retrieves a single agent by its UUID from a specific ecosystem."""
        return cls._handle_request(f"get agent {agent_uuid} from ecosystem {ecosystem_uuid}", cls._get_client().get_agent_in_ecosystem, ecosystem_uuid=ecosystem_uuid, agent_uuid=agent_uuid)

    def modify_agent(cls, ecosystem_uuid: str, agent_uuid: str, agent_data: AgentInputModel) -> AgentOutputModel:
        """Updates a single agent within a specific ecosystem."""
        return cls._handle_request(f"update agent {agent_uuid} in ecosystem {ecosystem_uuid}", cls._get_client().update_agent_in_ecosystem, ecosystem_uuid=ecosystem_uuid, agent_uuid=agent_uuid, agent_data=agent_data)

    # --- Forge Facade ---
    def list_all_forges(cls) -> list[ForgeOutputModel]:
        """Retrieves a list of all forges."""
        return cls._handle_request("list all forges", cls._get_client().get_forges)
        
    def add_new_forge(cls, data: ForgeInputModel) -> ForgeOutputModel:
        """Creates a new forge."""
        return cls._handle_request("add new forge", cls._get_client().add_forge, data=data)

    def get_specific_forge(cls, forge_uuid: str) -> ForgeOutputModel:
        """Retrieves a specific forge by its UUID."""
        return cls._handle_request(f"get forge {forge_uuid}", cls._get_client().get_forge, forge_uuid=forge_uuid)

    def modify_forge(cls, forge_uuid: str, data: ForgeInputModel) -> ForgeOutputModel:
        """Updates a specific forge by its UUID."""
        return cls._handle_request(f"update forge {forge_uuid}", cls._get_client().update_forge, forge_uuid=forge_uuid, data=data)

    def remove_forge(cls, forge_uuid: str) -> None:
        """Deletes a specific forge by its UUID."""
        return cls._handle_request(f"delete forge {forge_uuid}", cls._get_client().delete_forge, forge_uuid=forge_uuid)

    def begin_new_forge_cycle(cls, forge_uuid: str, data: ForgeCycleInputModel, override_key: bool | None = None) -> NewCycleOutputModel:
        """Starts a new evolutionary cycle within a specific forge."""
        return cls._handle_request(f"start new forge cycle for forge {forge_uuid}", cls._get_client().start_new_forge_cycle, forge_uuid=forge_uuid, data=data, override_key=override_key)

    def conclude_forge_cycle(cls, forge_cycle_uuid: str, agents_data: list[AgentInputModel]) -> None:
        """Ends a forge cycle and submits the resulting agents."""
        return cls._handle_request(f"end forge cycle {forge_cycle_uuid}", cls._get_client().end_forge_cycle, forge_cycle_uuid=forge_cycle_uuid, agents_data=agents_data)

    def get_forge_cycle_spend(cls, forge_cycle_uuid: str) -> float:
        """Retrieves the total spend for a specific forge cycle."""
        return cls._handle_request(f"get spend for forge cycle {forge_cycle_uuid}", cls._get_client().get_spend, forge_cycle_uuid=forge_cycle_uuid)
    
    def log_forge_cycle_usage(cls, forge_cycle_uuid: str, cost: float) -> None:
        """Records a cost against a specific forge cycle."""
        return cls._handle_request(f"record usage for forge cycle {forge_cycle_uuid}", cls._get_client().record_forge_cycle_usage, forge_cycle_uuid=forge_cycle_uuid, cost=cost)

    def pick_agents_for_forge_cycle(cls, forge_cycle_uuid: str, nb_agents: int) -> list[AgentOutputModel]:
        """Selects a number of agents for a specific forge cycle."""
        return cls._handle_request(f"select agents for forge cycle {forge_cycle_uuid}", cls._get_client().select_agents_for_forge_cycle, forge_cycle_uuid=forge_cycle_uuid, nb_agents=nb_agents)

    def make_deduct_compute_banks_for_forge_cycle(cls, forge_cycle_uuid: str, deductions: dict[str, float]) -> None:
        """Deducts from the compute banks of agents for a specific forge cycle."""
        return cls._handle_request(f"deduct compute banks for forge cycle {forge_cycle_uuid}", cls._get_client().deduct_compute_banks_for_forge_cycle, forge_cycle_uuid=forge_cycle_uuid, deductions=deductions)
        
    # --- User Facade ---
    def make_user(cls, data: UserInputModel) -> UserOutputModel:
        """Creates a new user (admin operation)."""
        return cls._handle_request("create user", cls._get_client().create_user, data=data)
        
    def list_all_users(cls) -> list[UserOutputModel]:
        """Retrieves a list of all users (admin operation)."""
        return cls._handle_request("list all users", cls._get_client().list_users)

    def get_specific_user(cls, userUuid: str) -> UserOutputModel:
        """Retrieves a specific user by their UUID."""
        return cls._handle_request(f"get user {userUuid}", cls._get_client().get_user, userUuid=userUuid)

    def modify_user(cls, userUuid: str, data: UserInputModel) -> None:
        """Updates a specific user by their UUID (admin operation)."""
        return cls._handle_request(f"update user {userUuid}", cls._get_client().update_user, userUuid=userUuid, data=data)

    def remove_user(cls, userUuid: str) -> None:
        """Deletes a specific user by their UUID (admin operation)."""
        return cls._handle_request(f"delete user {userUuid}", cls._get_client().delete_user, userUuid=userUuid)

    def get_user_by_their_email(cls, email: str) -> UserOutputModel:
        """Retrieves a user by their email address."""
        return cls._handle_request(f"get user by email {email}", cls._get_client().get_user_by_email, email=email)


if __name__ == "__main__":
    # This block is for example usage and will only run when the script is executed directly.
    print("Ebiose API Client (Python) - Example Usage")
    print("Please configure EbioseAPIClient.set_client_credentials() before running examples.")
    print("-" * 30)

    # To use the client, you must first set the credentials.
    # Uncomment and replace the placeholder values below.
    
    # --- Step 1: Initialize the client ---
    # EbioseAPIClient.set_client_credentials(
    #     base_url="http://localhost:8000",  # Replace with your API's base URL
    #     api_key="your_api_key_here"       # Or use bearer_token="your_token_here"
    # )

    # --- Step 2: Call facade methods (if client is configured) ---
    # if EbioseAPIClient._client:
    #     try:
    #         # Example: List all forges available to the authenticated user.
    #         all_forges = EbioseAPIClient.list_all_forges()
    #         print(f"Found {len(all_forges)} forges.")
    #         if all_forges:
    #             print(f"First forge name: {all_forges[0].name}")

    #         # Example: Create a new forge. This requires an existing ecosystem UUID.
    #         # Replace 'your-ecosystem-uuid' with a real one from your application.
    #         # new_forge_data = ForgeInputModel(
    #         #     name="My New Test Forge", 
    #         #     description="A forge for testing the API client.", 
    #         #     ecosystemUuid="your-ecosystem-uuid"
    #         # )
    #         # created_forge = EbioseAPIClient.add_new_forge(data=new_forge_data)
    #         # print(f"Created new forge with UUID: {created_forge.uuid}")

    #     except EbioseCloudError as e:
    #         # Catch API-specific errors for graceful handling.
    #         print(f"An error occurred during an API call: {e}")
    # else:
    #     print("Client is not configured. Skipping API call examples.")
