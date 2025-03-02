from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from pydantic import BaseModel, Field

from ebiose.core.agent import Agent
from ebiose.core.evo_forging_cycle import EvoForgingCycle, EvoForgingCylceConfig
from ebiose.tools.embedding_helper import generate_embeddings

if TYPE_CHECKING:
    from ebiose.core.ecosystem import Ecosystem


class AgentForge(BaseModel):
    id: str = Field(default_factory=lambda: f"forge-{uuid4()!s}")
    name: str
    description: str
    agent_input_model: type[BaseModel]
    agent_output_model: type[BaseModel]
    default_model_endpoint_id: str
    default_generated_agent_engine_type: str = "langgraph_engine"

    _description_embedding: list[float] | None = None


    @property
    def description_embedding(self) -> list[float]:
        if self._description_embedding is None:
            self._description_embedding = generate_embeddings(self.description)
        return self._description_embedding

    @abstractmethod
    async def compute_fitness(self, agent: Agent, compute_token_id: str, **kwargs: dict[str, any]) -> int:
        pass

    # async def async_compute_fitness(self, agent: Agent, compute_token_id: str) -> int:
    #     return await self.compute_fitness(agent, compute_token_id)

    #     Use ThreadPoolExecutor to run compute_fitness in a separate thread
    #     This is useful if compute_fitness is CPU-bound or involves I/O operations
    #     with ThreadPoolExecutor() as executor:
    #         return await asyncio.get_event_loop().run_in_executor(
    #             executor, self.compute_fitness, agent, compute_token_id
    #     )

    async def run_new_cycle(
            self,
            ecosystem: Ecosystem,
            cycle_config: EvoForgingCylceConfig,
        ) -> list[Agent]:
        cycle = EvoForgingCycle(forge=self, config=cycle_config)
        ecosystem.add_forge(self)
        # try to select agents from the ecocystem to enter the forge cycle
        # if not, architect agents will handle creating new agents in the forge cycle
        return await cycle.execute_a_cycle(ecosystem)

