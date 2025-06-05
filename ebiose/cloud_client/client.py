import json
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import requests
from pydantic import BaseModel, Field

# --- Constants ---
# You might want to manage the base URL and API key/token through environment variables or a config file
# For the EbioseAPIClient facade, these would be passed to its set_client method.

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
    """Enum for User Roles. The OpenAPI spec defines [1, 2].
    Assuming 1 could be an admin-like role and 2 a standard user.
    Adjust names if specific roles are known.
    """
    USER = 1
    ADMIN = 2

# --- Pydantic Models (Generated from #/components/schemas) ---
# Forward references will be resolved by Pydantic using string type hints.

class AgentEngineInputModel(BaseModel):
    engineType: str | None = None
    configuration: str | None = None

class AgentEngineOutputModel(BaseModel):
    engineType: str | None = None
    configuration: str | None = None

class ApiKeyInputModel(BaseModel):
    userUuid: str | None = None
    expirationDate: datetime

class SelfApiKeyInputModel(BaseModel):
    expirationDate: datetime

class EcosystemInputModel(BaseModel):
    communityCreditsAvailable: float

class ForgeCycleInputModel(BaseModel):
    forgeDescription: str | None = None
    forgeName: str | None = None
    nAgentsInPopulation: int
    nSelectedAgentsFromEcosystem: int
    nBestAgentsToReturn: int
    replacementRatio: float
    tournamentSizeRatio: float
    localResultsPath: str | None = None
    budget: float

class SelfUserInputModel(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    githubId: str | None = None
    password: str | None = None # Be cautious with sending passwords

class SignupInputModel(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    githubId: str | None = None
    password: str | None = None # Be cautious with sending passwords

class UserInputModel(BaseModel):
    role: Role
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    githubId: str | None = None
    creditsLimit: float
    password: str | None = None # Be cautious with sending passwords

# Models that might have forward references or be referenced by others
class UserOutputModel(BaseModel):
    uuid: str | None = None
    role: Role
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    githubId: str | None = None
    apiKeys: list["ApiKeyOutputModel"] | None = None # Forward reference
    creditsLimit: float
    creditsUsed: float
    availableCredits: float = Field(..., description="Read-only field")

class ApiKeyOutputModel(BaseModel):
    uuid: str | None = None
    key: str | None = None
    createdAt: datetime
    expirationDate: datetime
    user: UserOutputModel | None = None # Reference to UserOutputModel

class AgentOutputModel(BaseModel):
    uuid: str | None = None
    name: str | None = None
    description: str | None = None
    ecosystem: Optional["EcosystemOutputModel"] = None # Forward reference
    architectAgent: Optional["AgentOutputModel"] = None # Self/Forward reference
    geneticOperatorAgent: Optional["AgentOutputModel"] = None # Self/Forward reference
    agentEngine: AgentEngineOutputModel | None = None
    descriptionEmbedding: list[float] | None = None
    computeBankInDollars: float

class EcosystemOutputModel(BaseModel):
    uuid: str | None = None
    communityCreditsAvailable: float
    agents: list[AgentOutputModel] | None = None # Reference to AgentOutputModel

class AgentInputModel(BaseModel):
    uuid: str | None = None # Typically not set on input unless for update linking
    name: str | None = None
    description: str | None = None
    architectAgentUuid: str | None = None
    geneticOperatorAgentUuid: str | None = None
    agentEngine: AgentEngineInputModel | None = None
    descriptionEmbedding: list[float] | None = None

class LoginOutputModel(BaseModel):
    user: UserOutputModel | None = None
    token: str | None = None

class NewCycleOutputModel(BaseModel):
    liteLLMKey: str | None = None
    forgeCycleUuid: str | None = None

# Rebuild models to resolve forward references (Pydantic usually handles this with string annotations)
# For older Pydantic versions, explicit rebuild might be needed.
# Modern Pydantic (>=1.8) often resolves these automatically.
UserOutputModel.model_rebuild()
ApiKeyOutputModel.model_rebuild()
AgentOutputModel.model_rebuild()
EcosystemOutputModel.model_rebuild()


# --- Core API Client ---
class EbioseCloudClient:
    """Core client for interacting with the EbioseCloud API.
    """
    def __init__(self, base_url: str, api_key: str | None = None, bearer_token: str | None = None, timeout: int = 30):
        """Initializes the EbioseCloudClient.

        Args:
            base_url: The base URL for the API.
            api_key: The API key for authentication.
            bearer_token: The Bearer token for authentication.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.bearer_token = bearer_token
        self.timeout = timeout

        if not self.api_key and not self.bearer_token:
            # Depending on API design, some public endpoints might not need auth.
            # However, the global security definition suggests auth is generally required.
            print("Warning: EbioseCloudClient initialized without API key or Bearer token. Most operations may fail.")


    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: Any | None = None, # For form data
        json_data: Any | None = None, # For JSON body
    ) -> Any:
        """Makes an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE).
            endpoint: API endpoint path (e.g., "/users").
            params: URL query parameters.
            data: Request body for form-encoded data.
            json_data: Request body for JSON-encoded data.

        Returns:
            Parsed JSON response or None for empty responses.

        Raises:
            EbioseCloudHTTPError: If an HTTP error occurs.
            EbioseCloudError: For other API-related errors.
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"Accept": "application/json"}

        if json_data is not None:
            headers["Content-Type"] = "application/json"

        # Authentication: Prefer Bearer token if both are provided
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        elif self.api_key:
            headers["ApiKey"] = self.api_key
        # If neither is set and an endpoint requires auth, the API will likely return a 401/403

        try:
            response = requests.request(
                method,
                url,
                params=params,
                data=data,
                json=json_data,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()  # Raises HTTPError for 4xx/5xx responses

            if response.status_code == 204 or not response.content: # No content
                return None
            return response.json()

        except requests.exceptions.HTTPError as e:
            response_text = e.response.text if e.response is not None else "No response body"
            status_code = e.response.status_code if e.response is not None else None

            # Log or capture more details from e.response if needed
            # For example, try to parse JSON error from response_text
            error_details = response_text
            try:
                parsed_error = json.loads(response_text)
                if isinstance(parsed_error, dict):
                    error_details = parsed_error.get("detail", parsed_error.get("message", response_text))
            except json.JSONDecodeError:
                pass # Keep original response_text

            raise EbioseCloudHTTPError(
                f"HTTP error occurred: {e.request.method} {e.request.url} - {error_details}",
                status_code=status_code,
                response_text=response_text,
            ) from e
        except requests.exceptions.RequestException as e:
            raise EbioseCloudError(f"Request failed: {e}") from e

    # --- ApiKey Endpoints ---
    def add_api_key(self, data: ApiKeyInputModel) -> bool:
        """POST /apikeys - AddApiKey"""
        return self._request("POST", "/apikeys", json_data=data.model_dump(by_alias=True))

    def get_api_keys(self) -> list[ApiKeyOutputModel]:
        """GET /apikeys - GetApiKeys"""
        response_data = self._request("GET", "/apikeys")
        return [ApiKeyOutputModel(**item) for item in response_data]

    def self_add_api_key(self, data: SelfApiKeyInputModel) -> bool:
        """POST /apikeys/self - SelfAddApiKey"""
        return self._request("POST", "/apikeys/self", json_data=data.model_dump(by_alias=True))

    def self_get_api_keys(self) -> list[ApiKeyOutputModel]:
        """GET /apikeys/self - SelfGetApiKeys"""
        response_data = self._request("GET", "/apikeys/self")
        return [ApiKeyOutputModel(**item) for item in response_data]

    def get_api_key(self, uuid: str) -> ApiKeyOutputModel:
        """GET /apikeys/{uuid} - GetApiKey"""
        response_data = self._request("GET", f"/apikeys/{uuid}")
        return ApiKeyOutputModel(**response_data)

    def delete_api_key(self, uuid: str) -> None:
        """DELETE /apikeys/{uuid} - DeleteApiKey"""
        self._request("DELETE", f"/apikeys/{uuid}")

    def update_api_key(self, uuid: str, data: ApiKeyInputModel) -> None:
        """PUT /apikeys/{uuid} - UpdateApiKey"""
        self._request("PUT", f"/apikeys/{uuid}", json_data=data.model_dump(by_alias=True))

    def self_delete_api_key(self, uuid: str) -> None:
        """DELETE /apikeys/self/{uuid} - SelfDeleteApiKey"""
        self._request("DELETE", f"/apikeys/self/{uuid}")

    # --- AuthEndpoints ---
    def login(self, email: str, password: str) -> LoginOutputModel:
        """GET /auth/login - Login"""
        params = {"email": email, "password": password}
        response_data = self._request("GET", "/auth/login", params=params)
        return LoginOutputModel(**response_data)

    def sign_up(self, data: SignupInputModel) -> UserOutputModel:
        """POST /auth/signup - SignUp"""
        response_data = self._request("POST", "/auth/signup", json_data=data.model_dump(by_alias=True))
        return UserOutputModel(**response_data)

    def self_update(self, data: SelfUserInputModel) -> UserOutputModel:
        """PUT /auth/self-update - SelfUpdate"""
        response_data = self._request("PUT", "/auth/self-update", json_data=data.model_dump(by_alias=True))
        return UserOutputModel(**response_data)

    def update_password(self, new_password: str) -> None:
        """PUT /auth/update-password - UpdatePassword"""
        params = {"newPassword": new_password}
        self._request("PUT", "/auth/update-password", params=params)

    def refresh_token(self, token: str) -> str:
        """GET /auth/refresh-token - RefreshToken"""
        params = {"token": token}
        return self._request("GET", "/auth/refresh-token", params=params)

    def user_info(self) -> UserOutputModel:
        """GET /auth/user-info - UserInfo"""
        response_data = self._request("GET", "/auth/user-info")
        return UserOutputModel(**response_data)

    # --- EcosystemEndpoints ---
    def create_ecosystem(self, data: EcosystemInputModel) -> EcosystemOutputModel:
        """POST /ecosystems"""
        response_data = self._request("POST", "/ecosystems", json_data=data.model_dump(by_alias=True))
        return EcosystemOutputModel(**response_data)

    def list_ecosystems(self) -> list[EcosystemOutputModel]:
        """GET /ecosystems"""
        response_data = self._request("GET", "/ecosystems")
        return [EcosystemOutputModel(**item) for item in response_data]

    def get_ecosystem(self, uuid: str) -> EcosystemOutputModel:
        """GET /ecosystems/{uuid}"""
        response_data = self._request("GET", f"/ecosystems/{uuid}")
        return EcosystemOutputModel(**response_data)

    def update_ecosystem(self, uuid: str, data: EcosystemInputModel) -> EcosystemOutputModel:
        """PUT /ecosystems/{uuid}"""
        response_data = self._request("PUT", f"/ecosystems/{uuid}", json_data=data.model_dump(by_alias=True))
        return EcosystemOutputModel(**response_data)

    def delete_ecosystem(self, uuid: str) -> None:
        """DELETE /ecosystems/{uuid}"""
        self._request("DELETE", f"/ecosystems/{uuid}")

    def add_agents_to_ecosystem(self, ecosystem_uuid: str, agents_data: list[AgentInputModel]) -> None:
        """POST /ecosystems/{ecosystemUuid}/agents"""
        json_payload = [agent.model_dump(by_alias=True) for agent in agents_data]
        self._request("POST", f"/ecosystems/{ecosystem_uuid}/agents", json_data=json_payload)

    def list_agents_in_ecosystem(self, ecosystem_uuid: str) -> list[AgentOutputModel]:
        """GET /ecosystems/{ecosystemUuid}/agents"""
        response_data = self._request("GET", f"/ecosystems/{ecosystem_uuid}/agents")
        return [AgentOutputModel(**item) for item in response_data]

    def delete_agents_from_ecosystem(self, ecosystem_uuid: str, agent_uuids: list[str]) -> None:
        """DELETE /ecosystems/{ecosystemUuid}/agents"""
        self._request("DELETE", f"/ecosystems/{ecosystem_uuid}/agents", json_data=agent_uuids)

    def select_agents_from_ecosystem(self, ecosystem_uuid: str, nb_agents: int, forge_cycle_uuid: str) -> list[AgentOutputModel]:
        """GET /ecosystems/{ecosystemUuid}/select-agents"""
        params = {"nbAgents": nb_agents, "forgeCycleUuid": forge_cycle_uuid}
        response_data = self._request("GET", f"/ecosystems/{ecosystem_uuid}/select-agents", params=params)
        return [AgentOutputModel(**item) for item in response_data]

    def deduct_compute_banks_for_ecosystem(self, ecosystem_uuid: str, deductions: dict[str, float]) -> None:
        """POST /ecosystems/{ecosystemUuid}/deduct-compute-banks"""
        self._request("POST", f"/ecosystems/{ecosystem_uuid}/deduct-compute-banks", json_data=deductions)

    # --- ForgeCycleEndpoints ---
    def start_new_forge_cycle(self, data: ForgeCycleInputModel, override_key: bool | None = None) -> NewCycleOutputModel:
        """POST /forges/cycles/start - StartNewForgeCycle"""
        params = {}
        if override_key is not None:
            params["overrideKey"] = override_key
        response_data = self._request("POST", "/forges/cycles/start", params=params if params else None, json_data=data.model_dump(by_alias=True))
        return NewCycleOutputModel(**response_data)

    def end_forge_cycle(self, forge_cycle_uuid: str, agents_data: list[AgentInputModel]) -> None:
        """POST /forges/cycles/end/{forgeCycleUuid} - EndForgeCycle"""
        json_payload = [agent.model_dump(by_alias=True) for agent in agents_data]
        self._request("POST", f"/forges/cycles/end/{forge_cycle_uuid}", json_data=json_payload)

    def get_spend(self, forge_cycle_uuid: str) -> float:
        """GET /forges/spend/{forgeCycleUuid} - GetSpend"""
        return self._request("GET", f"/forges/spend/{forge_cycle_uuid}")

    # --- Users Endpoints ---
    def create_user(self, data: UserInputModel) -> UserOutputModel:
        """POST /users"""
        response_data = self._request("POST", "/users", json_data=data.model_dump(by_alias=True))
        return UserOutputModel(**response_data)

    def list_users(self) -> list[UserOutputModel]:
        """GET /users"""
        response_data = self._request("GET", "/users")
        return [UserOutputModel(**item) for item in response_data]

    def get_user(self, uuid: str) -> UserOutputModel:
        """GET /users/{uuid}"""
        response_data = self._request("GET", f"/users/{uuid}")
        return UserOutputModel(**response_data)

    def update_user(self, uuid: str, data: UserInputModel) -> None:
        """PUT /users/{uuid}"""
        self._request("PUT", f"/users/{uuid}", json_data=data.model_dump(by_alias=True))

    def delete_user(self, uuid: str) -> None:
        """DELETE /users/{uuid}"""
        self._request("DELETE", f"/users/{uuid}")

    def get_user_by_email(self, email: str) -> UserOutputModel:
        """GET /users/email/{email}"""
        response_data = self._request("GET", f"/users/email/{email}")
        return UserOutputModel(**response_data)

    def record_user_usage(self, credits: float, user_uuid: str) -> None:
        """POST /users/usage"""
        params = {"credits": credits, "userUuid": user_uuid}
        self._request("POST", "/users/usage", params=params)


# --- Facade API Client (as per user's example structure) ---
class EbioseAPIClient:
    _client: EbioseCloudClient | None = None
    _base_url: str | None = None # Store base_url for re-initialization if needed

    @classmethod
    def set_client_credentials(cls, base_url: str, api_key: str | None = None, bearer_token: str | None = None) -> None:
        """Set the API client with the provided base URL and API key or Bearer token.
        This method initializes or re-initializes the internal client.
        """
        cls._base_url = base_url # Store for potential re-init or reference
        cls._client = EbioseCloudClient(base_url=base_url, api_key=api_key, bearer_token=bearer_token)
        print(f"EbioseCloudClient initialized for base URL: {base_url}")

    @classmethod
    def _get_client(cls) -> EbioseCloudClient:
        """Ensures the client is initialized and returns it.
        Raises EbioseCloudAuthError if the client is not set.
        """
        if cls._client is None:
            # You might want to load credentials from a config/env here if not set via set_client_credentials
            # For now, it strictly requires set_client_credentials to be called first.
            raise EbioseCloudAuthError(
                "Client not initialized. Call EbioseAPIClient.set_client_credentials(base_url, api_key/bearer_token) first.",
            )
        return cls._client

    # --- Wrapper Methods for EbioseCloudClient operations ---
    # Example: Ecosystems (as in user's provided snippet)
    @classmethod
    def get_ecosystems(cls) -> list[EcosystemOutputModel]:
        """Get the list of all ecosystems."""
        client = cls._get_client()
        try:
            print("\nAttempting to list all ecosystems...")
            list_of_ecosystems = client.list_ecosystems() # Corresponds to GET /ecosystems

            if list_of_ecosystems:
                print("Successfully retrieved the list of ecosystems.")
                # For brevity, not printing full JSON here, but you can uncomment:
                # print(json.dumps([eco.model_dump() for eco in list_of_ecosystems], indent=2, default=str))
                return list_of_ecosystems
            print("No ecosystems were found.")
            return []
        except EbioseCloudHTTPError as e:
            print(f"An API HTTP error occurred while fetching ecosystems: {e}")
            # Consider re-raising or handling more gracefully based on application needs
            raise
        except EbioseCloudError as e:
            print(f"An API error occurred while fetching ecosystems: {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred while fetching ecosystems: {e}")
            raise

    # --- Add wrappers for all other EbioseCloudClient methods here ---
    # Example for another method group: ApiKey
    @classmethod
    def add_new_api_key(cls, user_uuid: str | None, expiration_date: datetime) -> bool:
        client = cls._get_client()
        input_data = ApiKeyInputModel(userUuid=user_uuid, expirationDate=expiration_date)
        return client.add_api_key(data=input_data)

    @classmethod
    def list_all_api_keys(cls) -> list[ApiKeyOutputModel]:
        client = cls._get_client()
        return client.get_api_keys()

    # ... (and so on for all methods in EbioseCloudClient)
    # It's a good practice to wrap each method to provide consistent error handling
    # or logging at the facade level if desired.

    # --- AuthEndpoints Wrappers ---
    @classmethod
    def perform_login(cls, email: str, password: str) -> LoginOutputModel:
        client = cls._get_client()
        return client.login(email=email, password=password)

    @classmethod
    def perform_sign_up(cls, signup_data: SignupInputModel) -> UserOutputModel:
        client = cls._get_client()
        return client.sign_up(data=signup_data)

    @classmethod
    def get_current_user_info(cls) -> UserOutputModel:
        client = cls._get_client()
        return client.user_info()

    # Add more wrappers as needed for other client methods...
    # For example:
    # @classmethod
    # def create_new_user(cls, user_data: UserInputModel) -> UserOutputModel:
    #     client = cls._get_client()
    #     return client.create_user(data=user_data)


if __name__ == "__main__":
    # --- Example Usage (Illustrative) ---
    # **Important**: Replace with your actual base_url and credentials.
    # This example assumes you have a running instance of the EbioseCloud API.

    # Option 1: Using API Key
    # EbioseAPIClient.set_client_credentials(
    #     base_url="http://localhost:8000", # Replace with your API base URL
    #     api_key="YOUR_API_KEY"
    # )

    # Option 2: Using Bearer Token (e.g., after login)
    # EbioseAPIClient.set_client_credentials(
    #     base_url="http://localhost:8000", # Replace with your API base URL
    #     bearer_token="YOUR_BEARER_TOKEN"
    # )

    print("Ebiose API Client (Python) - Example Usage")
    print("Please configure EbioseAPIClient.set_client_credentials() before running examples.")
    print("-" * 30)

    # --- Mocking ModelEndpoints for the example if you have them ---
    class ModelEndpoints: # Mock for example
        @staticmethod
        def get_ebiose_api_base():
            return "http://your-api-base-url.com/api/v1" # Replace!
        @staticmethod
        def get_ebiose_api_key():
            return "your_actual_api_key" # Replace!
        @staticmethod
        def get_ebiose_bearer_token():
            return None # Or "your_actual_bearer_token"

    # Example of setting up the client using the facade
    try:
        # Initialize with either API key or bearer token
        # Using API Key:
        # EbioseAPIClient.set_client_credentials(
        #     base_url=ModelEndpoints.get_ebiose_api_base(),
        #     api_key=ModelEndpoints.get_ebiose_api_key()
        # )

        # Or using Bearer Token (if you have one, perhaps from a login flow):
        # EbioseAPIClient.set_client_credentials(
        #    base_url=ModelEndpoints.get_ebiose_api_base(),
        #    bearer_token=ModelEndpoints.get_ebiose_bearer_token() # Assuming this method exists
        # )

        # If neither is set, subsequent calls will raise EbioseCloudAuthError
        # For this example to run without actual credentials, we'll skip API calls.
        print("To run example API calls, uncomment and configure set_client_credentials above.")

        # --- Example: Listing ecosystems (if client is configured) ---
        # if EbioseAPIClient._client: # Check if client was actually configured
        #     try:
        #         print("\nFetching ecosystems via facade...")
        #         ecosystems = EbioseAPIClient.get_ecosystems()
        #         if ecosystems:
        #             print(f"Found {len(ecosystems)} ecosystem(s). First one (UUID): {ecosystems[0].uuid if ecosystems else 'N/A'}")
        #             # print(json.dumps([e.model_dump() for e in ecosystems], indent=2, default=str))
        #         else:
        #             print("No ecosystems returned by facade.")
        #     except EbioseCloudError as e:
        #         print(f"Error during example ecosystem fetch: {e}")
        # else:
        #     print("\nSkipping ecosystem fetch example as client is not configured with credentials.")


        # --- Example: Attempting login (if client is configured for base_url only) ---
        # This call would typically not require an API key/bearer token on the client itself,
        # as the login endpoint is usually public.
        # However, the client still needs the base_url.

        # EbioseAPIClient.set_client_credentials(base_url=ModelEndpoints.get_ebiose_api_base()) # Set only base_url for login
        # if EbioseAPIClient._client:
        #     try:
        #         print("\nAttempting login...")
        #         login_response = EbioseAPIClient.perform_login(email="test@example.com", password="password123")
        #         print(f"Login successful for user: {login_response.user.email if login_response.user else 'Unknown'}")
        #         print(f"Received token (first 10 chars): {login_response.token[:10] if login_response.token else 'N/A'}...")
        #
        #         # Now you could re-initialize the client with the bearer token:
        #         # if login_response.token:
        #         #     EbioseAPIClient.set_client_credentials(
        #         #         base_url=ModelEndpoints.get_ebiose_api_base(),
        #         #         bearer_token=login_response.token
        #         #     )
        #         #     print("Client re-initialized with Bearer token.")
        #         #     # Now try an authenticated endpoint:
        #         #     user_details = EbioseAPIClient.get_current_user_info()
        #         #     print(f"Fetched user info for: {user_details.email}")
        #
        #     except EbioseCloudHTTPError as e:
        #         print(f"Login failed or error: {e}")
        #         if e.status_code == 404 and "user" in str(e).lower(): # Example of specific error handling
        #             print("Hint: User not found or incorrect credentials.")
        #     except EbioseCloudError as e:
        #         print(f"API error during login: {e}")
        # else:
        #     print("\nSkipping login example as client base_url is not configured.")


    except EbioseCloudAuthError as e:
        print(f"Client setup error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in the example: {e}")

