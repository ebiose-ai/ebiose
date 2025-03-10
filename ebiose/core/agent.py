"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

import uuid
from typing import Self

from langfuse.decorators import observe
from loguru import logger
from pydantic import BaseModel, Field, model_validator

from ebiose.core.agent_engine import AgentEngine
from ebiose.core.agent_engine_factory import AgentEngineFactory
from ebiose.tools.embedding_helper import generate_embeddings


class Agent(BaseModel):
    id: str = Field(default_factory=lambda: "agent-" + str(uuid.uuid4()))
    name: str
    description: str = Field(repr=False)
    architect_agent: Agent | None = None
    genetic_operator_agent: Agent | None  = None
    parent_ids: list[str] = Field(default_factory=list)

    agent_engine: AgentEngine | None = Field(default=None)
    description_embedding: list[float] | None = Field(default=None, exclude=True)

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
                agent_engine["engine_type"],
                agent_engine["configuration"],
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
    async def run(self, input_data: BaseModel, compute_token_id: str) -> any:
        try:
            return await self.agent_engine.run(input_data, compute_token_id)
        except Exception as e:
            logger.debug(f"Error while running agent {self.id}: {e!s}")
            return None
