from __future__ import annotations

import json
from datetime import datetime
from enum import Enum

import requests
from pydantic import BaseModel


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


# --- Enums ---
class Role(int, Enum):
    """Enum for User Roles."""
    USER = 1
    ADMIN = 2

class AgentType(int, Enum):
    """Enum for Agent Types."""
    STANDARD = 0
    GENETIC_OPERATOR = 1
    ARCHITECT = 2

# --- Pydantic Models (Updated based on swagger.json) ---

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

class ForgeInputModel(BaseModel):
    """Input model for creating or updating a forge."""
    name: str | None = None
    description: str | None = None
    ecosystemUuid: str | None = None

class LogEntryInputModel(BaseModel):
    """Input model for creating a new log entry."""
    index: str
    data: str

class SelfUserInputModel(BaseModel):
    """Input model for the current user updating their own profile."""
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    githubId: str | None = None
    password: str | None = None

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
    apiKeys: list[ApiKeyOutputModel] | None = None
    creditsLimit: float
    creditsUsed: float
    availableCredits: float

class ApiKeyOutputModel(BaseModel):
    """Output model representing an API key."""
    uuid: str | None = None
    key: str | None = None
    createdAt: datetime
    expirationDate: datetime
    user: UserOutputModel | None = None

class AgentInputModel(BaseModel):
    """Input model for creating or updating an agent."""
    name: str | None = None
    description: str | None = None
    architectAgentUuid: str | None = None
    geneticOperatorAgentUuid: str | None = None
    agentEngine: AgentEngineInputModel | None = None
    descriptionEmbedding: list[float] | None = None
    parentAgentUuids: list[str] | None = None
    originForgeCycleUuid: str | None = None # New field
    agentType: AgentType

class AgentOutputModel(BaseModel):
    """Output model representing an agent."""
    uuid: str | None = None
    name: str | None = None
    description: str | None = None
    ecosystem: EcosystemOutputModel | None = None
    architectAgentUuid: str | None = None
    geneticOperatorAgentUuid: str | None = None
    agentEngine: AgentEngineOutputModel | None = None
    descriptionEmbedding: list[float] | None = None
    computeBankInDollars: float
    parentAgentUuids: list[str] | None = None
    childAgentUuids: list[str] | None = None
    originForgeCycle: ForgeCycleOutputModel | None = None # New field
    agentType: AgentType

class EcosystemOutputModel(BaseModel):
    """Output model representing an ecosystem."""
    uuid: str | None = None
    communityCreditsAvailable: float
    agents: list[AgentOutputModel] | None = None

class ForgeCycleOutputModel(BaseModel):
    """Output model representing a forge cycle's state. Updated structure."""
    uuid: str | None = None
    forge: ForgeOutputModel
    liteLLMKey: str | None = None
    nAgentsInPopulation: int
    nSelectedAgentsFromEcosystem: int
    nBestAgentsToReturn: int
    replacementRatio: float
    tournamentSizeRatio: float
    localResultsPath: str | None = None
    budget: float
    spentBudget: float # New field
    isRunning: bool
    generatedAgentsCount: int | None = None # New field

class ForgeOutputModel(BaseModel):
    """Output model representing a forge."""
    uuid: str | None = None
    name: str | None = None
    description: str | None = None
    forgeCycles: list[ForgeCycleOutputModel] | None = None

class LoginOutputModel(BaseModel):
    """Output model for a successful login."""
    user: UserOutputModel
    token: str | None = None

class NewCycleOutputModel(BaseModel):
    """Output model after starting a new forge cycle."""
    liteLLMKey: str | None = None
    forgeCycleUuid: str | None = None
    baseUrl: str | None = None

class LogEntryOutputModel(BaseModel):
    """Output model for a log entry response."""
    id: str | None = None
    index: str | None = None
    success: bool
    message: str | None = None


# Rebuild models to resolve forward references
# This is crucial for Pydantic to correctly link models defined with string type hints.
UserOutputModel.model_rebuild()
ApiKeyOutputModel.model_rebuild()
AgentOutputModel.model_rebuild()
EcosystemOutputModel.model_rebuild()
ForgeCycleOutputModel.model_rebuild()
ForgeOutputModel.model_rebuild()
LoginOutputModel.model_rebuild()


# --- Core API Client ---
class EbioseCloudClient:
    """Core client for interacting with the EbioseCloud API."""

    def __init__(self, base_url: str, api_key: str | None = None, bearer_token: str | None = None, timeout: int = 30):
        """
        Initializes the EbioseCloudClient.

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
            print("Warning: EbioseCloudClient initialized without API key or Bearer token.")

    def _request(self, method: str, endpoint: str, params: dict[str, any] | None = None, data: any = None, json_data: any = None) -> any:
        """Internal method to make an HTTP request."""
        url = f"{self.base_url}{endpoint}"
        headers = {"Accept": "application/json"}
        if json_data is not None:
            headers["Content-Type"] = "application/json"
        
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        elif self.api_key:
            headers["ApiKey"] = self.api_key
        
        try:
            # Pydantic v2 uses model_dump, v1 uses dict. Handle both for compatibility.
            if hasattr(BaseModel, 'model_dump'):
                json_payload = json.loads(json.dumps(json_data, default=lambda o: o.model_dump(by_alias=True) if isinstance(o, BaseModel) else o))
            else:
                 json_payload = json.loads(json.dumps(json_data, default=lambda o: o.dict(by_alias=True) if isinstance(o, BaseModel) else o))

            response = requests.request(method, url, params=params, data=data, json=json_payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            if response.status_code == 204 or not response.content:
                return None
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            response_text = e.response.text if e.response else "No response body"
            status_code = e.response.status_code if e.response else None
            error_details = response_text
            try:
                parsed_error = json.loads(response_text)
                if isinstance(parsed_error, dict):
                    error_details = parsed_error.get("detail", parsed_error.get("message", response_text))
            except json.JSONDecodeError:
                pass
            raise EbioseCloudHTTPError(f"HTTP error occurred: {e.request.method} {e.request.url} - {error_details}", status_code=status_code, response_text=response_text) from e
        except requests.exceptions.RequestException as e:
            raise EbioseCloudError(f"Request failed: {e}") from e

    # --- ApiKey Endpoints ---
    def add_api_key(self, data: ApiKeyInputModel) -> bool:
        return self._request("POST", "/apikeys", json_data=data)

    def get_api_keys(self) -> list[ApiKeyOutputModel]:
        return [ApiKeyOutputModel(**item) for item in self._request("GET", "/apikeys")]

    def self_add_api_key(self, data: SelfApiKeyInputModel) -> bool:
        return self._request("POST", "/apikeys/self", json_data=data)

    def self_get_api_keys(self) -> list[ApiKeyOutputModel]:
        return [ApiKeyOutputModel(**item) for item in self._request("GET", "/apikeys/self")]

    def get_api_key(self, apiKeyUuid: str) -> ApiKeyOutputModel:
        return ApiKeyOutputModel(**self._request("GET", f"/apikeys/{apiKeyUuid}"))

    def delete_api_key(self, apiKeyUuid: str) -> None:
        self._request("DELETE", f"/apikeys/{apiKeyUuid}")

    def update_api_key(self, apiKeyUuid: str, data: ApiKeyInputModel) -> None:
        self._request("PUT", f"/apikeys/{apiKeyUuid}", json_data=data)

    def self_delete_api_key(self, apiKeyUuid: str) -> None:
        self._request("DELETE", f"/apikeys/self/{apiKeyUuid}")

    # --- AuthEndpoints ---
    def login(self, email: str, password: str) -> LoginOutputModel:
        return LoginOutputModel(**self._request("GET", "/auth/login", params={"email": email, "password": password}))

    def login_github(self, code: str) -> LoginOutputModel:
        return LoginOutputModel(**self._request("GET", "/auth/github/login", params={"code": code}))

    def sign_up(self, data: SignupInputModel) -> UserOutputModel:
        return UserOutputModel(**self._request("POST", "/auth/signup", json_data=data))

    def self_update(self, data: SelfUserInputModel) -> UserOutputModel:
        return UserOutputModel(**self._request("PUT", "/auth/self-update", json_data=data))

    def update_password(self, new_password: str) -> None:
        self._request("PUT", "/auth/update-password", params={"newPassword": new_password})

    def refresh_token(self, token: str) -> str:
        return self._request("GET", "/auth/refresh-token", params={"token": token})

    def user_info(self) -> UserOutputModel:
        return UserOutputModel(**self._request("GET", "/auth/user-info"))

    # --- EcosystemEndpoints ---
    def create_ecosystem(self, data: EcosystemInputModel) -> EcosystemOutputModel:
        return EcosystemOutputModel(**self._request("POST", "/ecosystems", json_data=data))

    def list_ecosystems(self) -> list[EcosystemOutputModel]:
        return [EcosystemOutputModel(**item) for item in self._request("GET", "/ecosystems")]

    def get_ecosystem(self, uuid: str) -> EcosystemOutputModel:
        return EcosystemOutputModel(**self._request("GET", f"/ecosystems/{uuid}"))

    def update_ecosystem(self, uuid: str, data: EcosystemInputModel) -> EcosystemOutputModel:
        return EcosystemOutputModel(**self._request("PUT", f"/ecosystems/{uuid}", json_data=data))

    def delete_ecosystem(self, uuid: str) -> None:
        self._request("DELETE", f"/ecosystems/{uuid}")

    def add_agents_to_ecosystem(self, ecosystem_uuid: str, agents_data: list[AgentInputModel]) -> None:
        self._request("POST", f"/ecosystems/{ecosystem_uuid}/agents", json_data=agents_data)

    def list_agents_in_ecosystem(self, ecosystem_uuid: str) -> list[AgentOutputModel]:
        return [AgentOutputModel(**item) for item in self._request("GET", f"/ecosystems/{ecosystem_uuid}/agents")]

    def delete_agents_from_ecosystem(self, ecosystem_uuid: str, agent_uuids: list[str]) -> None:
        self._request("DELETE", f"/ecosystems/{ecosystem_uuid}/agents", json_data=agent_uuids)
    
    def get_agent_in_ecosystem(self, ecosystem_uuid: str, agent_uuid: str) -> AgentOutputModel:
        return AgentOutputModel(**self._request("GET", f"/ecosystems/{ecosystem_uuid}/agent/{agent_uuid}"))

    def update_agent_in_ecosystem(self, ecosystem_uuid: str, agent_uuid: str, agent_data: AgentInputModel) -> AgentOutputModel:
        return AgentOutputModel(**self._request("PUT", f"/ecosystems/{ecosystem_uuid}/agent/{agent_uuid}", json_data=agent_data))

    def add_single_agent_to_ecosystem(self, ecosystem_uuid: str, agent_data: AgentInputModel) -> AgentOutputModel:
        return AgentOutputModel(**self._request("POST", f"/ecosystems/{ecosystem_uuid}/agent", json_data=agent_data))

    # --- ForgeEndpoints ---
    def get_forges(self) -> list[ForgeOutputModel]:
        return [ForgeOutputModel(**item) for item in self._request("GET", "/forges")]

    def add_forge(self, data: ForgeInputModel) -> ForgeOutputModel:
        return ForgeOutputModel(**self._request("POST", "/forges", json_data=data))

    def get_forge(self, forge_uuid: str) -> ForgeOutputModel:
        return ForgeOutputModel(**self._request("GET", f"/forges/{forge_uuid}"))
    
    def update_forge(self, forge_uuid: str, data: ForgeInputModel) -> ForgeOutputModel:
        return ForgeOutputModel(**self._request("PUT", f"/forges/{forge_uuid}", json_data=data))

    def delete_forge(self, forge_uuid: str) -> None:
        self._request("DELETE", f"/forges/{forge_uuid}")
        
    def start_new_forge_cycle(self, forge_uuid: str, data: ForgeCycleInputModel, override_key: bool | None = None) -> NewCycleOutputModel:
        params = {"overrideKey": override_key} if override_key is not None else {}
        return NewCycleOutputModel(**self._request("POST", f"/forges/{forge_uuid}/cycles/start", params=params, json_data=data))

    def end_forge_cycle(self, forge_cycle_uuid: str, agents_data: list[AgentInputModel]) -> None:
        self._request("POST", f"/forges/cycles/{forge_cycle_uuid}/end", json_data=agents_data)

    def get_spend(self, forge_cycle_uuid: str) -> float:
        return self._request("GET", f"/forges/cycles/{forge_cycle_uuid}/spend")
    
    def select_agents_for_forge_cycle(self, forge_cycle_uuid: str, nb_agents: int) -> list[AgentOutputModel]:
        return [AgentOutputModel(**item) for item in self._request("GET", f"/forges/cycles/{forge_cycle_uuid}/select-agents", params={"nbAgents": nb_agents})]

    def deduct_compute_banks_for_forge_cycle(self, forge_cycle_uuid: str, deductions: dict[str, float]) -> None:
        self._request("POST", f"/forges/cycles/{forge_cycle_uuid}/deduct-compute-banks", json_data=deductions)

    def record_forge_cycle_usage(self, forge_cycle_uuid: str, cost: float) -> None:
        self._request("POST", f"/forges/cycles/{forge_cycle_uuid}/usage", params={"cost": cost})

    def add_agent_during_forge_cycle(self, forge_cycle_uuid: str, data: AgentInputModel) -> AgentOutputModel:
        """New: Corresponds to POST /forges/cycles/{forgeCycleUuid}/agent."""
        return AgentOutputModel(**self._request("POST", f"/forges/cycles/{forge_cycle_uuid}/agent", json_data=data))

    def add_agents_during_forge_cycle(self, forge_cycle_uuid: str, agents_data: list[AgentInputModel]) -> None:
        """New: Corresponds to POST /forges/cycles/{forgeCycleUuid}/agents."""
        self._request("POST", f"/forges/cycles/{forge_cycle_uuid}/agents", json_data=agents_data)

    # --- Logging Endpoint (New) ---
    def add_log_entry(self, data: LogEntryInputModel) -> LogEntryOutputModel:
        """Corresponds to POST /logging."""
        return LogEntryOutputModel(**self._request("POST", "/logging", json_data=data))
        
    # --- Users Endpoints ---
    def create_user(self, data: UserInputModel) -> UserOutputModel:
        return UserOutputModel(**self._request("POST", "/users", json_data=data))

    def list_users(self) -> list[UserOutputModel]:
        return [UserOutputModel(**item) for item in self._request("GET", "/users")]

    def get_user(self, userUuid: str) -> UserOutputModel:
        return UserOutputModel(**self._request("GET", f"/users/{userUuid}"))

    def update_user(self, userUuid: str, data: UserInputModel) -> None:
        self._request("PUT", f"/users/{userUuid}", json_data=data)

    def delete_user(self, userUuid: str) -> None:
        self._request("DELETE", f"/users/{userUuid}")

    def get_user_by_email(self, email: str) -> UserOutputModel:
        return UserOutputModel(**self._request("GET", f"/users/email/{email}"))


# --- Facade API Client ---
class EbioseAPIClient:
    """Facade client providing a high-level interface to the EbioseCloud API."""
    _client: EbioseCloudClient | None = None

    @classmethod
    def set_client_credentials(cls, base_url: str, api_key: str | None = None, bearer_token: str | None = None) -> None:
        """Sets the API client credentials."""
        cls._client = EbioseCloudClient(base_url=base_url, api_key=api_key, bearer_token=bearer_token)
        print(f"EbioseCloudClient initialized for base URL: {base_url}")

    @classmethod
    def _get_client(cls) -> EbioseCloudClient:
        """Ensures the client is initialized."""
        if cls._client is None:
            raise EbioseCloudAuthError("Client not initialized. Call EbioseAPIClient.set_client_credentials() first.")
        return cls._client
    
    @classmethod
    def _handle_request(cls, action_description: str, api_call, *args, **kwargs):
        """Generic request handler for the facade."""
        try:
            print(f"\nAttempting to {action_description}...")
            result = api_call(*args, **kwargs)
            print(f"Successfully finished: {action_description}.")
            return result
        except EbioseCloudError as e:
            print(f"An API error occurred while {action_description}: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred while {action_description}: {e}")
            raise

    # --- ApiKey Facade ---
    @classmethod
    def add_new_api_key(cls, data: ApiKeyInputModel) -> bool:
        return cls._handle_request("add new API key", cls._get_client().add_api_key, data=data)
    
    # ... (other facade methods remain largely the same, so they are omitted for brevity but should be included)

    # --- Forge Facade (with new methods) ---
    @classmethod
    def list_all_forges(cls) -> list[ForgeOutputModel]:
        return cls._handle_request("list all forges", cls._get_client().get_forges)
        
    @classmethod
    def add_new_forge(cls, data: ForgeInputModel) -> ForgeOutputModel:
        return cls._handle_request("add new forge", cls._get_client().add_forge, data=data)

    @classmethod
    def get_specific_forge(cls, forge_uuid: str) -> ForgeOutputModel:
        return cls._handle_request(f"get forge {forge_uuid}", cls._get_client().get_forge, forge_uuid=forge_uuid)

    @classmethod
    def modify_forge(cls, forge_uuid: str, data: ForgeInputModel) -> ForgeOutputModel:
        return cls._handle_request(f"update forge {forge_uuid}", cls._get_client().update_forge, forge_uuid=forge_uuid, data=data)

    @classmethod
    def remove_forge(cls, forge_uuid: str) -> None:
        return cls._handle_request(f"delete forge {forge_uuid}", cls._get_client().delete_forge, forge_uuid=forge_uuid)

    @classmethod
    def begin_new_forge_cycle(cls, forge_uuid: str, data: ForgeCycleInputModel, override_key: bool | None = None) -> NewCycleOutputModel:
        return cls._handle_request(f"start new forge cycle for forge {forge_uuid}", cls._get_client().start_new_forge_cycle, forge_uuid=forge_uuid, data=data, override_key=override_key)

    @classmethod
    def conclude_forge_cycle(cls, forge_cycle_uuid: str, agents_data: list[AgentInputModel]) -> None:
        return cls._handle_request(f"end forge cycle {forge_cycle_uuid}", cls._get_client().end_forge_cycle, forge_cycle_uuid=forge_cycle_uuid, agents_data=agents_data)

    @classmethod
    def get_forge_cycle_spend(cls, forge_cycle_uuid: str) -> float:
        return cls._handle_request(f"get spend for forge cycle {forge_cycle_uuid}", cls._get_client().get_spend, forge_cycle_uuid=forge_cycle_uuid)
    
    @classmethod
    def log_forge_cycle_usage(cls, forge_cycle_uuid: str, cost: float) -> None:
        return cls._handle_request(f"record usage for forge cycle {forge_cycle_uuid}", cls._get_client().record_forge_cycle_usage, forge_cycle_uuid=forge_cycle_uuid, cost=cost)

    @classmethod
    def pick_agents_for_forge_cycle(cls, forge_cycle_uuid: str, nb_agents: int) -> list[AgentOutputModel]:
        return cls._handle_request(f"select agents for forge cycle {forge_cycle_uuid}", cls._get_client().select_agents_for_forge_cycle, forge_cycle_uuid=forge_cycle_uuid, nb_agents=nb_agents)

    @classmethod
    def make_deduct_compute_banks_for_forge_cycle(cls, forge_cycle_uuid: str, deductions: dict[str, float]) -> None:
        return cls._handle_request(f"deduct compute banks for forge cycle {forge_cycle_uuid}", cls._get_client().deduct_compute_banks_for_forge_cycle, forge_cycle_uuid=forge_cycle_uuid, deductions=deductions)

    @classmethod
    def add_agent_during_cycle(cls, forge_cycle_uuid: str, agent_data: AgentInputModel) -> AgentOutputModel:
        """Adds a single agent during an active forge cycle."""
        return cls._handle_request(f"add agent to active forge cycle {forge_cycle_uuid}", cls._get_client().add_agent_during_forge_cycle, forge_cycle_uuid=forge_cycle_uuid, data=agent_data)

    @classmethod
    def add_agents_during_cycle(cls, forge_cycle_uuid: str, agents_data: list[AgentInputModel]) -> None:
        """Adds multiple agents during an active forge cycle."""
        return cls._handle_request(f"add agents to active forge cycle {forge_cycle_uuid}", cls._get_client().add_agents_during_forge_cycle, forge_cycle_uuid=forge_cycle_uuid, agents_data=agents_data)

    # --- Logging Facade (New) ---
    @classmethod
    def log_message(cls, data: LogEntryInputModel) -> LogEntryOutputModel:
        """Sends a log entry to the logging service."""
        # Note: A more specific description might be better depending on usage.
        return cls._handle_request(f"send log entry to index '{data.index}'", cls._get_client().add_log_entry, data=data)

if __name__ == "__main__":
    print("Ebiose API Client (Python) - Example Usage")
    print("Please configure EbioseAPIClient.set_client_credentials() before running examples.")
    print("-" * 30)

    # Example of setting credentials (uncomment to use)
    # EbioseAPIClient.set_client_credentials(
    #     base_url="http://127.0.0.1:8000", 
    #     bearer_token="your_bearer_token_here"
    # )

    # if EbioseAPIClient._client:
    #     try:
    #         # Example: Log a message
    #         log_data = LogEntryInputModel(index="client_test", data="This is a test log from the updated client.")
    #         log_response = EbioseAPIClient.log_message(data=log_data)
    #         print(f"Log response: {log_response.message}")

    #         # Example: List users
    #         users = EbioseAPIClient._get_client().list_users()
    #         print(f"Found {len(users)} users.")

    #     except EbioseCloudError as e:
    #         print(f"An error occurred: {e}")
    # else:
    #     print("Client is not configured. Skipping API call examples.")
