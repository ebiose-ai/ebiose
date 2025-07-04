"""Agent-related models for the Ebiose system."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator
from pydantic.alias_generators import to_camel

from ebiose.core.models.exceptions import AgentEngineRunError

if TYPE_CHECKING:
    from ebiose.core.engines.graph_engine.graph import Graph


class AgentEngineConfig(BaseModel):
    """Configuration for an agent engine."""

    engine_type: str
    configuration: dict[str, Any] | None = None
    model_endpoint_id: str | None = None


class AgentEngine(BaseModel):
    """Base class for agent engines."""

    engine_type: str
    agent_id: str | None = None
    configuration: dict[str, Any] | None = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    async def run(
        self,
        agent_input: BaseModel,
        master_agent_id: str,
        forge_cycle_id: str | None = None,
        **kwargs: dict[str, Any],
    ) -> Any:
        """Run the agent engine."""
        try:
            return await self._run_implementation(
                agent_input,
                master_agent_id,
                forge_cycle_id,
                **kwargs,
            )
        except Exception as e:
            raise AgentEngineRunError(
                message="Error during agent engine run",
                original_exception=e,
                agent_identifier=self.agent_id,
            ) from e

    async def _run_implementation(
        self,
        agent_input: BaseModel,
        master_agent_id: str,
        forge_cycle_id: str | None = None,
        **kwargs: dict[str, Any],
    ) -> Any:
        """Implementation of the agent engine run method."""
        raise NotImplementedError


class Agent(BaseModel):
    """Core agent model."""

    id: str = Field(default_factory=lambda: f"agent-{uuid.uuid4()}")
    name: str
    agent_type: Literal["architect", "genetic_operator"] | None = None
    description: str | None = None
    architect_agent_id: str | None = None
    genetic_operator_agent_id: str | None = None
    architect_agent: Agent | None = None
    parent_ids: list[str] = Field(default_factory=list)
    agent_engine: AgentEngine | None = Field(default=None)
    description_embedding: list[float] | None = Field(default=None, exclude=True)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    @field_serializer("agent_engine")
    def serialize_agent_engine(self, agent_engine: AgentEngine | None) -> dict[str, Any]:
        """Serialize the agent engine."""
        if agent_engine is not None:
            return agent_engine.model_dump(by_alias=True)
        return {}

    @model_validator(mode="before")
    @classmethod
    def validate_agent(cls, data: Any) -> Any:
        """Validate agent data before creation."""
        if "agent_engine" in data and data["agent_engine"] is not None:
            data["agent_engine"] = cls.validate_agent_engine(data["agent_engine"])
        return data

    @classmethod
    def validate_agent_engine(cls, agent_engine: dict[str, Any] | AgentEngine) -> AgentEngine:
        """Validate and create agent engine."""
        if isinstance(agent_engine, dict):
            from ebiose.core.agent_engine_factory import AgentEngineFactory

            return AgentEngineFactory.create_engine(
                engine_type=agent_engine["engine_type"],
                configuration=agent_engine["configuration"],
                agent_id=agent_engine["agent_id"],
            )
        if isinstance(agent_engine, AgentEngine):
            return agent_engine

        msg = "Invalid agent engine type"
        raise TypeError(msg)

    @model_validator(mode="after")
    def generate_embeddings(self) -> Self:
        """Generate embeddings for the agent description."""
        if self.description_embedding is None and self.description:
            from ebiose.tools.embedding_helper import generate_embeddings

            self.description_embedding = generate_embeddings(self.description)
        return self

    async def run(
        self,
        input_data: BaseModel,
        master_agent_id: str,
        forge_cycle_id: str | None = None,
        **kwargs: dict[str, Any],
    ) -> Any:
        """Run the agent."""
        if self.agent_engine is None:
            msg = "Agent engine is not configured"
            raise ValueError(msg)
        return await self.agent_engine.run(
            input_data,
            master_agent_id,
            forge_cycle_id,
            **kwargs,
        )

    def update_io_models(
        self,
        agent_input_model: type[BaseModel] | None = None,
        agent_output_model: type[BaseModel] | None = None,
    ) -> None:
        """Update input/output models for the agent."""
        if self.agent_engine is None:
            msg = "Agent engine is not configured"
            raise ValueError(msg)
        if agent_input_model is not None:
            self.agent_engine.input_model = agent_input_model
        if agent_output_model is not None:
            self.agent_engine.output_model = agent_output_model

# Rebuild models to resolve forward references
Agent.model_rebuild()
AgentEngine.model_rebuild()
