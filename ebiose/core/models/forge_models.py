"""Forge-related models for the Ebiose system."""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from ebiose.core.models.agent_models import Agent


class ForgeCycleConfig(BaseModel):
    """Configuration for a forge cycle."""

    n_agents_in_population: int = 10
    n_selected_agents_from_ecosystem: int = 5
    n_best_agents_to_return: int = 3
    replacement_ratio: float = 0.5
    tournament_size_ratio: float = 0.1
    local_results_path: Path | None = None
    mode: Literal["local", "cloud"]


class CloudForgeCycleConfig(ForgeCycleConfig):
    """Configuration for a cloud forge cycle."""

    budget: float
    mode: Literal["local", "cloud"] = "cloud"


class LocalForgeCycleConfig(ForgeCycleConfig):
    """Configuration for a local forge cycle."""

    n_generations: int
    mode: Literal["local", "cloud"] = "local"


@dataclass
class ForgeCycle:
    """Represents a forge cycle."""

    forge: AgentForge
    config: ForgeCycleConfig
    id: str = field(default_factory=lambda: f"forge-cycle-{uuid4()}")

    cur_generation: int = 0
    agents: dict[str, Agent] = field(default_factory=dict)
    agents_fitness: dict[str, float] = field(default_factory=dict)
    agents_first_generation_costs: dict[str, float] = field(default_factory=dict)
    init_agents_population: dict[Agent] = field(default_factory=list)
    architect_agents: dict[str, Agent] = field(default_factory=dict)
    genetic_operator_agents: dict[str, Agent] = field(default_factory=dict)

    def save_current_state(self, generation: int | None = None) -> None:
        """Save the current state of the forge cycle."""
        # Implementation would go here
        pass

    def add_agent(self, agent: Agent, source: str) -> None:
        """Add an agent to the forge cycle."""
        # Implementation would go here
        pass


class AgentForge(BaseModel):
    """Represents an agent forge."""

    id: str = Field(default_factory=lambda: f"forge-{uuid4()}")
    name: str
    description: str
    agent_input_model: type[BaseModel]
    agent_output_model: type[BaseModel]
    default_model_endpoint_id: str | None = None
    default_generated_agent_engine_type: str = "langgraph_engine"

    _description_embedding: list[float] | None = None

    @property
    def description_embedding(self) -> list[float]:
        """Get or generate description embedding."""
        if self._description_embedding is None:
            from ebiose.tools.embedding_helper import generate_embeddings

            self._description_embedding = generate_embeddings(self.description)
        return self._description_embedding

    @field_validator("default_model_endpoint_id", mode="after")
    @classmethod
    def validate_default_model_endpoint_id(cls, value: str | None) -> str:
        """Validate and set default model endpoint ID."""
        if value is None:
            from ebiose.core.model_endpoint import ModelEndpoints

            return ModelEndpoints.get_default_model_endpoint_id()
        return value

    @abstractmethod
    async def compute_fitness(
        self,
        agent: Agent,
        **kwargs: dict[str, Any],
    ) -> tuple[str, float]:
        """Compute fitness for an agent."""
        pass

    async def run_new_cycle(
        self,
        config: ForgeCycleConfig,
        ecosystem: Ecosystem | None = None,
    ) -> list[Agent]:
        """Run a new forge cycle."""
        cycle = ForgeCycle(forge=self, config=config)
        return await cycle.execute_a_cycle(ecosystem)
