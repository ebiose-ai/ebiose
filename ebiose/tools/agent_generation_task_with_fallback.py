from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from loguru import logger

from ebiose.core.agent_factory import AgentFactory

if TYPE_CHECKING:
    from pydantic import BaseModel

    from ebiose.core.agent import Agent
    from ebiose.core.agent_forge import AgentForge

T = TypeVar("T")

# init in ecosystem
async def architect_agent_task(
        forge: AgentForge,
        architect_agent: Agent,
        architect_agent_input: BaseModel,
        architect_agent_compute_token: str,
        genetic_operator_agent: Agent,
    ) -> Agent | None:

    result = await AgentFactory.generate_agent(
        architect_agent,
        architect_agent_input,
        architect_agent_compute_token,
        genetic_operator_agent,
        generated_agent_engine_type=forge.default_generated_agent_engine_type,
        generated_model_endpoint_id=forge.default_model_endpoint_id,
        generated_agent_input=forge.agent_input_model,
        generated_agent_output=forge.agent_output_model,
    )

    if result is None:
        logger.error(f"Architect agent {architect_agent.id} failed creating a valid agent for {forge.name}. Retrying once.")
        return await AgentFactory.generate_agent(
            architect_agent,
            architect_agent_input,
            architect_agent_compute_token,
            genetic_operator_agent,
            generated_agent_engine_type=forge.default_generated_agent_engine_type,
            generated_model_endpoint_id=forge.default_model_endpoint_id,
            generated_agent_input=forge.agent_input_model,
            generated_agent_output=forge.agent_output_model,
        )

    return result

# crossovoer and mutate
async def crossover_agent_task(
                forge: AgentForge,
                genetic_operator_agent: Agent,
                crossover_agent_input: BaseModel,
                crossover_agent_compute_token: str,
                parent1: Agent,
                parent2: Agent,
            ) -> Agent | None:

            result = await AgentFactory.crossover_agents(
                genetic_operator_agent,
                crossover_agent_input,
                crossover_agent_compute_token,
                generated_agent_engine_type=forge.default_generated_agent_engine_type,
                generated_model_endpoint_id=forge.default_model_endpoint_id,
                generated_agent_input=forge.agent_input_model,
                generated_agent_output=forge.agent_output_model,
                parent_ids = [parent1.id, parent2.id],
            )

            if result is None:
                logger.error(f"Error while generating offspring from {[parent1.id, parent2.id]}. Falling back to architect agent.")
                result = await AgentFactory.generate_agent(
                    parent1.architect_agent,
                    parent1.architect_agent.agent_engine.input_model(forge_description=forge.description),
                    crossover_agent_compute_token,
                    genetic_operator_agent,
                    generated_agent_engine_type=forge.default_generated_agent_engine_type,
                    generated_model_endpoint_id=forge.default_model_endpoint_id,
                    generated_agent_input=forge.agent_input_model,
                    generated_agent_output=forge.agent_output_model,
                )

            return result
