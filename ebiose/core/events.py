from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID


from elasticsearch import Elasticsearch
from loguru import logger as _logger
from pydantic import BaseModel, Field, computed_field

from ebiose.cloud_client.ebiose_api_client import EbioseAPIClient

if TYPE_CHECKING:
    # from ebiose.core.forge_cycle import ForgeCycleConfig # Not directly used in event fields, config is passed as dict
    from uuid import UUID # Moved UUID import for type checking

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

def init_logger(user_id: str | None, forge_id: str | UUID | None, forge_cycle_id: str | UUID) -> None:
    global event_logger
    event_logger = event_logger.bind(
        user_id=user_id,
        forge_id=forge_id,
        forge_cycle_id=forge_cycle_id,
    )

class BaseEvent(BaseModel):
    """Base class for all events in the system."""
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))

    @computed_field
    @property
    def event_name(self) -> str:
        return self.__class__.__name__

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
        # log_message = message_override if message_override else f"Event: {self.event_name}"# for ForgeCycle {self.forge_cycle_id}"
        event_logger.bind(event_payload=self.to_dict()).info(log_message)


# --- ForgeCycle Events ---
class ForgeCycleStartedEvent(BaseEvent):
    forge_name: str
    forge_description: str
    config: dict  # Serialized ForgeCycleConfig


class ForgeCycleEndedEvent(BaseEvent):
    duration_seconds: float
    total_cost: float
    num_best_agents: int
    budget_left: float | None = None


class ForgeCycleFailedEvent(BaseEvent):
    error_message: str
    duration_seconds: float


# --- Population Initialization Events ---
class PopulationInitializationStartedEvent(BaseEvent):
    n_agents_to_initialize: int
    n_selected_from_ecosystem: int


class ArchitectAgentTaskCreatedEvent(BaseEvent):
    architect_agent_id: str | None
    generation_number: int

class AgentAddedToPopulationEvent(BaseEvent):
    agent_id: str
    generation_number: int
    source: str  # e.g., "newly_created_during_init", "from_ecosystem", "offspring", "kept_from_previous_gen"
    agent: dict[str, Any]  # Serialized Agent object if available

class PopulationInitializationCompletedEvent(BaseEvent):
    num_agents_initialized: int
    initialization_cost: float
    duration_seconds: float


# --- Generation Events ---
class GenerationRunStartedEvent(BaseEvent):
    generation_number: int
    current_population_size: int


class PopulationEvaluationStartedEvent(BaseEvent):
    generation_number: int
    num_agents_to_evaluate: int


class AgentEvaluationCompletedEvent(BaseEvent):
    agent_id: str
    generation_number: int
    fitness: float
    evaluation_cost: float


class PopulationEvaluationCompletedEvent(BaseEvent):
    generation_number: int
    total_evaluation_cost: float
    duration_seconds: float


class AgentSelectionStartedEvent(BaseEvent):
    generation_number: int
    method: str  # e.g., "roulette_wheel", "tournament"
    num_to_select: int


class AgentSelectionCompletedEvent(BaseEvent):
    generation_number: int
    method: str
    num_selected: int
    selected_agent_ids: list[str]


class CrossoverAndMutationStartedEvent(BaseEvent):
    generation_number: int
    num_parents: int  # Number of operations to be performed


class OffspringCreatedEvent(BaseEvent):
    offspring_agent_id: str
    generation_number: int
    parent_ids: list[str]
    genetic_operator_agent_id: str | None
    offspring_agent: dict[str, Any]


class CrossoverAndMutationCompletedEvent(BaseEvent):
    generation_number: int
    num_offsprings_generated: int
    cost: float
    duration_seconds: float


class GenerationRunCompletedEvent(BaseEvent):
    generation_number: int
    generation_total_cost: float
    duration_seconds: float
    population_size_after_generation: int

