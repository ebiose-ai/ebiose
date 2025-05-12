"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from pydantic import BaseModel
from sortedcontainers import SortedList

from ebiose.core.agent import Agent
from ebiose.core.engines.graph_engine.utils import GraphUtils
from ebiose.core.model_endpoint import ModelEndpoints
from ebiose.tools.embedding_helper import embedding_distance

if TYPE_CHECKING:
    from ebiose.core.agent_forge import AgentForge


class Ecosystem(BaseModel):
    initial_architect_agents: list[Agent] | None = None
    initial_genetic_operator_agents: list[Agent] | None = None
    agents: list[Agent] = []
    forge_list: ClassVar[list[AgentForge]] = []
    agent_forge_distances: ClassVar[dict[AgentForge, SortedList]] = {}
    model_endpoint_ids: ClassVar[list[str]] = []

    @classmethod
    def new(cls, initial_agents: list[Agent] | None = None) -> Ecosystem:
        initial_architect_agents = [GraphUtils.get_architect_agent(ModelEndpoints.get_default_model_endpoint_id())]
        initial_genetic_operator_agents = [
            GraphUtils.get_crossover_agent(ModelEndpoints.get_default_model_endpoint_id()),
            GraphUtils.get_mutation_agent(ModelEndpoints.get_default_model_endpoint_id()),
        ]
        return cls(
            initial_architect_agents=initial_architect_agents,
            initial_genetic_operator_agents=initial_genetic_operator_agents,
            agents = initial_agents if initial_agents is not None else [],
        )

    async def select_agents_for_forge(self, forge: AgentForge, n_agents: int) -> list[Agent]:
        self.add_forge(forge)
        if n_agents <= 0:
            return []
        selected_agents = []
        agent_forge_distances = self.agent_forge_distances[forge.id]
        for _ in range(n_agents):
            if len(agent_forge_distances) == 0:
                break
            agent, _ = agent_forge_distances.pop(0)
            selected_agents.append(agent)
        return selected_agents

    def add_forge(self, forge: AgentForge) -> None:
        self.forge_list.append(forge)
        # Initialize SortedList with existing agents and their distances
        self.agent_forge_distances[forge.id] = SortedList(
            [(agent, embedding_distance(agent.description_embedding, forge.description_embedding))
             for agent in self.agents],
            key=lambda x: x[1],
        )

    def _add_new_born_agent(self, new_agent: Agent) -> None:
        for forge in self.forge_list:
            distance = embedding_distance(new_agent.description_embedding, forge.description_embedding)
            self.agent_forge_distances[forge.id].add((new_agent, distance))

        self.agents.append(new_agent)
