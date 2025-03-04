from __future__ import annotations

from abc import abstractmethod
from uuid import uuid4

from IPython import get_ipython

if get_ipython() is not None:
    from IPython.display import Markdown, display
from loguru import logger
from pydantic import BaseModel, Field

from ebiose.core.agent import Agent
from ebiose.core.ecosystem import Ecosystem
from ebiose.core.evo_forging_cycle import EvoForgingCycle, EvoForgingCylceConfig
from ebiose.tools.embedding_helper import generate_embeddings


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
            config: EvoForgingCylceConfig,
            ecosystem: Ecosystem | None = None,
        ) -> list[Agent]:
        cycle = EvoForgingCycle(forge=self, config=config)
        if ecosystem is None:
            ecosystem = Ecosystem()
        ecosystem.add_forge(self)
        # try to select agents from the ecocystem to enter the forge cycle
        # if not, architect agents will handle creating new agents in the forge cycle
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
