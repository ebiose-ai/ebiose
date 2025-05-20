"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING
from uuid import uuid4

from IPython import get_ipython

from ebiose.core.model_endpoint import ModelEndpoints

if get_ipython() is not None:
    from IPython.display import Markdown, display
from loguru import logger
from pydantic import BaseModel, Field, field_validator

from ebiose.core.agent import Agent
from ebiose.core.forge_cycle import (
    ForgeCycle,
    ForgeCycleConfig,
)
from ebiose.tools.embedding_helper import generate_embeddings

if TYPE_CHECKING:
    from ebiose.core.ecosystem import Ecosystem


class AgentForge(BaseModel):
    id: str = Field(default_factory=lambda: f"forge-{uuid4()!s}")
    name: str
    description: str
    agent_input_model: type[BaseModel]
    agent_output_model: type[BaseModel]
    default_model_endpoint_id: str | None = None
    default_generated_agent_engine_type: str = "langgraph_engine"

    _description_embedding: list[float] | None = None

    @property
    def description_embedding(self) -> list[float]:
        if self._description_embedding is None:
            self._description_embedding = generate_embeddings(self.description)
        return self._description_embedding

    @field_validator("default_model_endpoint_id", mode="after")
    @classmethod
    def validate_default_model_endpoint_id(cls, value: str | None) -> str:
        if value is None:
            return ModelEndpoints.get_default_model_endpoint_id()
        return value

    @abstractmethod
    async def compute_fitness(self, agent: Agent, **kwargs: dict[str, any]) -> int:
        pass

    async def run_new_cycle(
            self,
            config: ForgeCycleConfig,
            ecosystem: Ecosystem | None = None,
        ) -> list[Agent]:

        cycle = ForgeCycle(forge=self, config=config)

        return await cycle.execute_a_cycle(ecosystem)



    def display_results(self, agents: dict[str, Agent], agents_fitness: dict[str, float]) -> None:
        sorted_fitness = dict(sorted(agents_fitness.items(), key=lambda item: item[1], reverse=True))
        if get_ipython() is None:
            for agent_id, fitness_value in sorted_fitness.items():
                agent = agents[agent_id]
                mermaid_str = agent.agent_engine.graph.to_mermaid_str(orientation="LR")
                logger.info(f"Agent ID: {agent_id}, fitness: {fitness_value} \n{mermaid_str}")
        else:
            markdown_str = ""
            for agent_id, fitness_value in sorted_fitness.items():
                agent = agents[agent_id]

                markdown_str += f"# Agent ID: {agent_id}\n"
                markdown_str += f"## Fitness: {fitness_value}\n"
                markdown_str += "```mermaid \n"
                markdown_str += f"{agent.agent_engine.graph.to_mermaid_str(orientation='LR')} \n"
                markdown_str += "``` \n"
                markdown_str += "## Prompts:\n"
                markdown_str += f"##### Shared context prompt\n{agent.agent_engine.graph.shared_context_prompt}\n"
                for node in agent.agent_engine.graph.nodes:
                    if node.type == "LLMNode":
                        markdown_str += f"##### {node.name}\n{node.prompt}\n"
                markdown_str += "\n"

            display(Markdown(markdown_str))
