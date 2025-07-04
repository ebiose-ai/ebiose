"""Core models for the Ebiose system."""

from ebiose.core.models.agent_models import Agent, AgentEngine, AgentEngineConfig
from ebiose.core.models.api_models import (
    AgentInputModel,
    AgentOutputModel,
    AgentEngineInputModel,
    AgentEngineOutputModel,
    ApiKeyInputModel,
    ApiKeyOutputModel,
    EcosystemInputModel,
    EcosystemOutputModel,
    ForgeCycleInputModel,
    ForgeCycleOutputModel,
    ForgeInputModel,
    ForgeOutputModel,
    UserInputModel,
    UserOutputModel,
    NewCycleOutputModel,
    LogEntryInputModel,
    LogEntryOutputModel,
)
from ebiose.core.models.auth_models import (
    SelfUserInputModel,
    SignupInputModel,
    UserInputModel as AuthUserInputModel,
)
from ebiose.core.models.forge_models import AgentForge, ForgeCycle, ForgeCycleConfig
from ebiose.core.models.enums import Role, AgentType
from ebiose.core.models.exceptions import EbioseCloudError, EbioseCloudHTTPError, EbioseCloudAuthError, AgentEngineError, AgentEngineRunError

__all__ = [
    # Agent models
    "Agent",
    "AgentEngine",
    "AgentEngineConfig",
    # API models
    "AgentInputModel",
    "AgentOutputModel",
    "AgentEngineInputModel",
    "AgentEngineOutputModel",
    "ApiKeyInputModel",
    "ApiKeyOutputModel",
    "EcosystemInputModel",
    "EcosystemOutputModel",
    "ForgeCycleInputModel",
    "ForgeCycleOutputModel",
    "ForgeInputModel",
    "ForgeOutputModel",
    "UserInputModel",
    "UserOutputModel",
    "NewCycleOutputModel",
    "LogEntryInputModel",
    "LogEntryOutputModel",
    # Auth models
    "SelfUserInputModel",
    "SignupInputModel",
    "AuthUserInputModel",
    # Forge models
    "AgentForge",
    "ForgeCycle",
    "ForgeCycleConfig",
    # Enums
    "Role",
    "AgentType",
    # Exceptions
    "EbioseCloudError",
    "EbioseCloudHTTPError",
    "EbioseCloudAuthError",
    "AgentEngineError",
    "AgentEngineRunError",
]

# Ensure all models are properly rebuilt to resolve forward references
Agent.model_rebuild()
AgentEngine.model_rebuild()
UserOutputModel.model_rebuild()
ApiKeyOutputModel.model_rebuild()
AgentOutputModel.model_rebuild()
EcosystemOutputModel.model_rebuild()
ForgeCycleOutputModel.model_rebuild()
ForgeOutputModel.model_rebuild()
LogEntryOutputModel.model_rebuild()
