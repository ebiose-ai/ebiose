"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

import traceback
import uuid
from typing import Literal, Self

from langfuse.decorators import observe
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator
from pydantic.alias_generators import to_camel

from ebiose.core.agent_engine import AgentEngine
from ebiose.core.agent_engine_factory import AgentEngineFactory
from ebiose.tools.embedding_helper import generate_embeddings


class Agent(BaseModel):
    id: str = Field(default_factory=lambda: "agent-" + str(uuid.uuid4()))
    name: str
    agent_type: Literal["architect", "genetic_operator"] | None = None
    description: str | None = None
    architect_agent_id: str | None = None 
    genetic_operator_agent_id: str | None = None  #
    architect_agent: Agent | None = None  # Reference to the architect agent if this is a generated agent
    parent_ids: list[str] = Field(default_factory=list)

    agent_engine: AgentEngine | None = Field(default=None)
    description_embedding: list[float] | None = Field(default=None, exclude=True)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True, # Allows initializing with snake_case names
    )

    @field_serializer("agent_engine")
    def serialize_agent_engine(self, agent_engine: AgentEngine | None) -> dict:
        if agent_engine is not None:
            return agent_engine.model_dump(by_alias=True) # TODO(xabier): remove by_alias ?
        return {}

    @model_validator(mode="before")
    @classmethod
    def validate_agent(cls, data: any) -> any:
        if "agent_engine" in data and data["agent_engine"] is not None:
            data["agent_engine"] = cls.validate_agent_engine(data["agent_engine"])
        return data

    @classmethod
    def validate_agent_engine(cls, agent_engine: dict | AgentEngine) -> AgentEngine:
        if isinstance(agent_engine, dict):
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
        if self.description_embedding is None:
            self.description_embedding = generate_embeddings(self.description)
        return self

    @observe(name="run_agent")
    async def run(self, input_data: BaseModel, master_agent_id: str, forge_cycle_id: str | None = None, **kwargs: dict[str, any]) -> any:
        return await self.agent_engine.run(input_data, master_agent_id, forge_cycle_id, **kwargs)

    def update_io_models(
        self,
        agent_input_model: type[BaseModel] | None = None,
        agent_output_model: type[BaseModel] | None = None,
    ) -> None:
        if agent_input_model is not None:
            self.agent_engine.input_model = agent_input_model
        if agent_output_model is not None:
            self.agent_engine.output_model = agent_output_model
