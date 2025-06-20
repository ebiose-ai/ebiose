"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

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
        genetic_operator_agent: Agent,
        forge_cycle_id: str | None = None,
    ) -> Agent | None:
    # TODO(xabier): remove
    # from ebiose.cloud_client.ebiose_api_client import get_sample_agent
    # from ebiose.cloud_client.ebiose_api_client import EbioseAPIClient
    # agent = get_sample_agent()
    # agent.architect_agent_id = "agent-c6ef9d53-923b-459a-ab99-ebb2877517d8"
    # agent.genetic_operator_agent_id = "agent-dff043b2-fa0f-4761-a1f0-5561bd58ed26"
    # return agent

    response = None
    try:
        response = await AgentFactory.generate_agent(
            architect_agent,
            architect_agent_input,
            genetic_operator_agent,
            generated_agent_engine_type=forge.default_generated_agent_engine_type,
            generated_model_endpoint_id=forge.default_model_endpoint_id,
            generated_agent_input=forge.agent_input_model,
            generated_agent_output=forge.agent_output_model,
            forge_cycle_id= forge_cycle_id,
            forge_description=forge.description,
        )
    except Exception as e:
        logger.debug(f"Architect agent {architect_agent.id} failed creating a valid agent for {forge.name}. Retrying once.")
        response = await AgentFactory.generate_agent(
            architect_agent,
            architect_agent_input,
            genetic_operator_agent,
            generated_agent_engine_type=forge.default_generated_agent_engine_type,
            generated_model_endpoint_id=forge.default_model_endpoint_id,
            generated_agent_input=forge.agent_input_model,
            generated_agent_output=forge.agent_output_model,
            forge_cycle_id=forge_cycle_id,
            forge_description=forge.description,
        )
    return response

# crossovoer and mutate
async def crossover_agent_task(
                forge: AgentForge,
                genetic_operator_agent: Agent,
                crossover_agent_input: BaseModel,
                architect_agent: Agent | None,
                parent1: Agent,
                parent2: Agent | None,
                master_agent_id: str | None = None,
                forge_cycle_id: str | None = None,
            ) -> Agent | None:
    # TODO(xabier): remove
    # from ebiose.cloud_client.ebiose_api_client import get_sample_agent
    # from ebiose.cloud_client.ebiose_api_client import EbioseAPIClient
    # agent = get_sample_agent()
    # agent.architect_agent_id = "agent-c6ef9d53-923b-459a-ab99-ebb2877517d8"
    # agent.genetic_operator_agent_id = "agent-dff043b2-fa0f-4761-a1f0-5561bd58ed26"
    # return agent

    result = None
    try:
        result = await AgentFactory.crossover_agents(
            genetic_operator_agent,
            crossover_agent_input,
            generated_agent_engine_type=forge.default_generated_agent_engine_type,
            generated_model_endpoint_id=forge.default_model_endpoint_id,
            generated_agent_input=forge.agent_input_model,
            generated_agent_output=forge.agent_output_model,
            parent_ids = [parent1.id, parent2.id] if parent2 is not None else [parent1.id],
            master_agent_id=master_agent_id,
            forge_cycle_id=forge_cycle_id,
            architect_agent=architect_agent,
            forge_description=forge.description,
        )
    except Exception as e:
        logger.debug(f"Error while generating offspring from {[parent1.id, parent2.id]}. Falling back to architect agent.")
        result = await AgentFactory.generate_agent(
            architect_agent,
            architect_agent.agent_engine.input_model(forge_description=forge.description),
            genetic_operator_agent,
            generated_agent_engine_type=forge.default_generated_agent_engine_type,
            generated_model_endpoint_id=forge.default_model_endpoint_id,
            generated_agent_input=forge.agent_input_model,
            generated_agent_output=forge.agent_output_model,
            forge_cycle_id=forge_cycle_id,
            forge_description=forge.description,
        )

    return result
