"""API models for the Ebiose Cloud API."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

from ebiose.core.models.enums import AgentType, Role

if TYPE_CHECKING:
    pass


# --- Input Models ---
class AgentEngineInputModel(BaseModel):
    """Input model for agent engine configuration."""

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


class AgentInputModel(BaseModel):
    """Input model for creating or updating an agent."""

    name: str | None = None
    description: str | None = None
    architectAgentUuid: str | None = None
    geneticOperatorAgentUuid: str | None = None
    agentEngine: AgentEngineInputModel | None = None
    descriptionEmbedding: list[float] | None = None
    parentAgentUuids: list[str] | None = None
    originForgeCycleUuid: str | None = None
    agentType: AgentType


# --- Output Models ---
class AgentEngineOutputModel(BaseModel):
    """Output model for agent engine configuration."""

    engineType: str | None = None
    configuration: str | None = None


class ApiKeyOutputModel(BaseModel):
    """Output model representing an API key."""

    uuid: str | None = None
    key: str | None = None
    createdAt: datetime
    expirationDate: datetime
    user: UserOutputModel | None = None


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


class EcosystemOutputModel(BaseModel):
    """Output model representing an ecosystem."""

    uuid: str | None = None
    communityCreditsAvailable: float
    agents: list[AgentOutputModel] | None = None


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
    originForgeCycle: ForgeCycleOutputModel | None = None
    agentType: AgentType


class ForgeCycleOutputModel(BaseModel):
    """Output model representing a forge cycle's state."""

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
    spentBudget: float
    isRunning: bool
    generatedAgentsCount: int | None = None


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
UserOutputModel.model_rebuild()
ApiKeyOutputModel.model_rebuild()
AgentOutputModel.model_rebuild()
EcosystemOutputModel.model_rebuild()
ForgeCycleOutputModel.model_rebuild()
ForgeOutputModel.model_rebuild()
LoginOutputModel.model_rebuild()
