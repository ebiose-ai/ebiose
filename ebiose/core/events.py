from __future__ import annotations

import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any
from uuid import UUID

from loguru import logger as _logger
from pydantic import BaseModel, Field, computed_field

from ebiose.cloud_client.ebiose_api_client import EbioseAPIClient

if TYPE_CHECKING:
    from uuid import UUID  # Moved UUID import for type checking


class EventPhase(Enum):
    """Enum representing different phases of the forge cycle."""

    INITIALIZATION = "initialization"
    GENERATION = "generation"
    EVALUATION = "evaluation"
    SELECTION = "selection"
    CROSSOVER_MUTATION = "crossover_mutation"
    COMPLETION = "completion"
    FAILURE = "failure"


class AgentSource(Enum):
    """Enum representing different sources of agents."""

    NEWLY_CREATED_DURING_INIT = "newly_created_during_init"
    FROM_ECOSYSTEM = "from_ecosystem"
    OFFSPRING = "offspring"
    KEPT_FROM_PREVIOUS_GEN = "kept_from_previous_gen"


class SelectionMethod(Enum):
    """Enum representing different selection methods."""

    ROULETTE_WHEEL = "roulette_wheel"
    TOURNAMENT = "tournament"


event_logger = _logger


def elastic_sink(message) -> None:  # noqa: ANN001
    record = message.record
    record_extra = record.pop("extra", {})
    event_payload = record_extra.pop("event_payload", None)
    log_doc = record_extra
    if event_payload is not None:
        log_doc.update(event_payload)
    log_doc["loguru"] = {
        "time": record["time"].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "level": record["level"].name,
        "message": record["message"],
        "file": record["file"].name,
        "line": record["line"],
        "function": record["function"],
    }

    EbioseAPIClient.log(message=log_doc)


event_logger.add(elastic_sink, level="INFO")
# Create a string with a human readable timestamp and log it
human_readable_timestamp: str = datetime.datetime.now(datetime.UTC).strftime(
    "%Y-%m-%d %H:%M:%S %Z",
)
event_logger.add(f"./tmp/log_{human_readable_timestamp}.log", rotation="10 MB")


def init_logger(
    user_id: str | None,
    forge_id: str | UUID | None,
    forge_cycle_id: str | UUID,
    initial_budget: float | None = None,
) -> None:
    global event_logger
    event_logger = event_logger.bind(
        user_id=user_id,
        forge_id=forge_id,
        forge_cycle_id=forge_cycle_id,
        initial_budget=initial_budget,
    )


class BaseEvent(BaseModel):
    """Base class for all events in the system."""

    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )
    remaining_budget: float | None = Field(default=None)
    initial_budget: float | None = Field(default=None)
    generation_number: int | None = Field(
        default=None,
        description="Generation number when this event occurred. None for forge-level events.",
    )

    @computed_field
    @property
    def event_name(self) -> str:
        return self.__class__.__name__

    @computed_field
    @property
    def budget_usage_ratio(self) -> float | None:
        """Calculate the ratio of remaining budget to initial budget (0.0 to 1.0)."""
        if self.initial_budget is None or self.remaining_budget is None:
            return None
        if self.initial_budget == 0:
            return 0.0
        return self.remaining_budget / self.initial_budget

    @computed_field
    @property
    def budget_spent_ratio(self) -> float | None:
        """Calculate the ratio of spent budget to initial budget (0.0 to 1.0)."""
        if self.initial_budget is None or self.remaining_budget is None:
            return None
        if self.initial_budget == 0:
            return 1.0
        return (self.initial_budget - self.remaining_budget) / self.initial_budget

    @computed_field
    @property
    def budget_spent(self) -> float | None:
        """Calculate the amount of budget spent."""
        if self.initial_budget is None or self.remaining_budget is None:
            return None
        return self.initial_budget - self.remaining_budget

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    def log(self, message_override: str | None = None) -> None:
        """Logs this event using Loguru.

        The event data is bound to the log record for consumption by structured logging sinks.
        """
        log_message = f"Event: {self.event_name} \n "
        log_message += self.model_dump_json(indent=2)
        if message_override:
            log_message = message_override
        event_logger.bind(event_payload=self.to_dict()).info(log_message)


# --- ForgeCycle Events ---
class ForgeCycleStartedEvent(BaseEvent):
    """Event emitted when a forge cycle starts."""

    forge_name: str
    forge_description: str
    config: dict[str, Any]  # Serialized ForgeCycleConfig


class ForgeCycleEndedEvent(BaseEvent):
    """Event emitted when a forge cycle ends successfully."""

    duration_seconds: float
    total_cost: float
    num_best_agents: int


class ForgeCycleFailedEvent(BaseEvent):
    """Event emitted when a forge cycle fails."""

    error_message: str
    duration_seconds: float


class ForgeCycleErrorEvent(BaseEvent):
    """Event emitted when an error occurs during a forge cycle without causing failure."""

    error_message: str
    error_type: str = Field(description="Type/category of the error")
    error_details: dict[str, Any] | None = Field(
        default=None,
        description="Additional error details and context",
    )
    component: str | None = Field(
        default=None,
        description="Component/module where the error occurred",
    )
    recoverable: bool = Field(
        default=True,
        description="Whether the error was recoverable",
    )


# --- Population Initialization Events ---
class PopulationInitializationStartedEvent(BaseEvent):
    """Event emitted when population initialization starts."""

    n_agents_to_initialize: int
    n_selected_from_ecosystem: int
    generation_number: int = Field(
        default=0,
        description="Always 0 during initialization",
    )


class ArchitectAgentTaskCreatedEvent(BaseEvent):
    """Event emitted when an architect agent task is created."""

    architect_agent_id: str | None


class AgentAddedToPopulationEvent(BaseEvent):
    """Event emitted when an agent is added to the population."""

    agent_id: str
    source: AgentSource = Field(description="Source of the agent")
    agent: dict[str, Any]  # Serialized Agent object if available


class PopulationInitializationCompletedEvent(BaseEvent):
    """Event emitted when population initialization completes."""

    num_agents_initialized: int
    initialization_cost: float
    duration_seconds: float
    generation_number: int = Field(
        default=0,
        description="Always 0 during initialization",
    )


# --- Generation Events ---
class GenerationRunStartedEvent(BaseEvent):
    """Event emitted when a generation run starts."""

    current_population_size: int


class PopulationEvaluationStartedEvent(BaseEvent):
    """Event emitted when population evaluation starts."""

    num_agents_to_evaluate: int


class AgentEvaluationCompletedEvent(BaseEvent):
    """Event emitted when an agent evaluation completes."""

    agent_id: str
    fitness: float
    evaluation_cost: float


class PopulationEvaluationCompletedEvent(BaseEvent):
    """Event emitted when population evaluation completes."""

    total_evaluation_cost: float
    duration_seconds: float


class AgentSelectionStartedEvent(BaseEvent):
    """Event emitted when agent selection starts."""

    method: SelectionMethod = Field(description="Selection method used")
    num_to_select: int


class AgentSelectionCompletedEvent(BaseEvent):
    """Event emitted when agent selection completes."""

    method: SelectionMethod = Field(description="Selection method used")
    num_selected: int
    selected_agent_ids: list[str]


class CrossoverAndMutationStartedEvent(BaseEvent):
    """Event emitted when crossover and mutation starts."""

    num_parents: int  # Number of operations to be performed


class OffspringCreatedEvent(BaseEvent):
    """Event emitted when an offspring is created."""

    offspring_agent_id: str
    parent_ids: list[str]
    genetic_operator_agent_id: str | None
    offspring_agent: dict[str, Any]


class CrossoverAndMutationCompletedEvent(BaseEvent):
    """Event emitted when crossover and mutation completes."""

    num_offsprings_generated: int
    cost: float
    duration_seconds: float


class GenerationRunCompletedEvent(BaseEvent):
    """Event emitted when a generation run completes."""

    generation_total_cost: float
    duration_seconds: float
    population_size_after_generation: int


# --- LLM Error Events ---
class LLMApiErrorEvent(BaseEvent):
    """Event emitted when an LLM API error occurs."""

    error_message: str
    error_type: str = Field(description="Type of the LLM API error")
    llm_identifier: str | None = Field(
        default=None,
        description="Identifier of the LLM that caused the error",
    )
    agent_id: str | None = Field(
        default=None,
        description="ID of the agent making the LLM call",
    )
    model_endpoint_id: str | None = Field(
        default=None,
        description="Model endpoint ID used for the call",
    )
    original_exception: str | None = Field(
        default=None,
        description="String representation of the original exception",
    )
    retry_attempt: int | None = Field(
        default=None,
        description="Retry attempt number if applicable",
    )
    component: str = Field(
        default="llm_api",
        description="Component where the error occurred",
    )


class LLMNodeErrorEvent(BaseEvent):
    """Event emitted when an LLM node execution error occurs."""

    error_message: str
    error_type: str = Field(description="Type of the LLM node error")
    node_name: str | None = Field(
        default=None,
        description="Name of the LLM node that failed",
    )
    node_id: str | None = Field(
        default=None,
        description="ID of the LLM node that failed",
    )
    agent_id: str | None = Field(
        default=None,
        description="ID of the agent executing the node",
    )
    model_endpoint_id: str | None = Field(
        default=None,
        description="Model endpoint ID used by the node",
    )
    original_exception: str | None = Field(
        default=None,
        description="String representation of the original exception",
    )
    component: str = Field(
        default="llm_node",
        description="Component where the error occurred",
    )
