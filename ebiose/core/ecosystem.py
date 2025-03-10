"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sortedcontainers import SortedList

from ebiose.core.agent import Agent
from ebiose.core.engines.graph_engine.utils import GraphUtils
from ebiose.tools.embedding_helper import embedding_distance

if TYPE_CHECKING:

    from ebiose.core.agent_forge import AgentForge


class Ecosystem:

    def __init__(
            self,
            initial_architect_agents: list[Agent] | None = None,
            forges: list[AgentForge]  | None = None,
            initial_genetic_operator_agents: list[Agent] | None = None,
        ) -> None:

        if initial_architect_agents is None:
            initial_architect_agents = [GraphUtils.get_architect_agent(model_endpoint_id="azure-gpt-4o-mini")]
        if initial_genetic_operator_agents is None:
            initial_genetic_operator_agents = [GraphUtils.get_crossover_agent(model_endpoint_id="azure-gpt-4o-mini")]

        self.initial_architect_agents: list[Agent] = initial_architect_agents
        self.initial_genetic_operator_agents: list[Agent] = initial_genetic_operator_agents
        self._agents: list[Agent] = []
        self.forge_list: list[AgentForge] = []
        self.agent_forge_distances: dict[AgentForge, SortedList] = {}
        self.model_endpoint_ids: list[str] = []

        if forges is not None:
            for forge in forges:
                self.add_forge(forge)

    async def select_agents_for_forge(self, forge: AgentForge, n_agents: int) -> list[Agent]:
        self.add_forge(forge)
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
             for agent in self._agents],
            key=lambda x: x[1],
        )

    def _add_new_born_agent(self, new_agent: Agent) -> None:
        for forge in self.forge_list:
            distance = embedding_distance(new_agent.description_embedding, forge.description_embedding)
            self.agent_forge_distances[forge.id].add((new_agent, distance))

        self._agents.append(new_agent)
