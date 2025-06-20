"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
import uuid

from loguru import logger

from ebiose.cloud_client.client import AgentOutputModel

if TYPE_CHECKING:
    from pydantic import BaseModel
    from ebiose.core.agent import Agent
    from ebiose.core.agent_engine_factory import AgentEngineFactory


class AgentFactory:
    @staticmethod
    def load_agent(
        agent_config: dict,
        model_endpoint_id: str | None = None,
    ) -> "Agent":
        from ebiose.core.agent_engine_factory import AgentEngineFactory # Local import
        from ebiose.core.agent import Agent # Local import

        # creating engine
        agent_engine = AgentEngineFactory.create_engine(
            engine_type=agent_config["agent_engine"]["engine_type"],
            configuration=agent_config["agent_engine"]["configuration"],
            agent_id=agent_config["agent_engine"]["agent_id"],
            model_endpoint_id=model_endpoint_id,
        )

        agent_config = agent_config.copy()
        agent_config["agent_engine"] = agent_engine
        agent_config["architect_agent"] = None
        agent_config["genetic_operator_agent"] = None
        agent_config["id"]=agent_engine.agent_id

        return Agent.model_validate(agent_config)


    @staticmethod
    def load_agent_from_api(
        response_dict: AgentOutputModel,
        model_endpoint_id: str | None = None,
    ) -> "Agent":
        from ebiose.core.agent_engine_factory import AgentEngineFactory # Local import
        from ebiose.core.agent import Agent # Local import

        engine_configuration = json.loads(response_dict.agentEngine.configuration)
        # creating engine
        agent_engine = AgentEngineFactory.create_engine(
            engine_type=response_dict.agentEngine.engineType,
            configuration=engine_configuration,
            model_endpoint_id=model_endpoint_id,
            agent_id=engine_configuration["agent_id"],
        )

        # architect_agent = AgentFactory.load_agent_from_api(
        #     response_dict.architectAgent,
        # ) if response_dict.architectAgent is not None else None
        # genetic_operator_agent = AgentFactory.load_agent_from_api(
        #     response_dict.geneticOperatorAgent,
        # ) if response_dict.geneticOperatorAgent is not None else None

        # TODO(xabier): remove when agent_type is implemented server-side
        agent_type = None
        if "architect" in response_dict.name:
            agent_type = "architect"
        elif "crossover" in response_dict.name or "mutation" in response_dict.name:
            agent_type = "genetic_operator"

        return Agent(
            id=response_dict.uuid,
            name=response_dict.name,
            agent_type=agent_type,  # TODO(xabier): remove when agent_type is implemented server-side
            description=response_dict.description,
            architect_agent_id=response_dict.architectAgentUuid,
            # architect_agent=architect_agent,  # TODO(xabier): replace with id
            genetic_operator_agent_id=response_dict.geneticOperatorAgentUuid,
            # genetic_operator_agent=genetic_operator_agent,  # TODO(xabier): replace with id
            agent_engine=agent_engine,
            parent_ids=response_dict.parentAgentUuids, #TODO(xabier): response_dict.parentIds or [],
        )

    @staticmethod
    async def generate_agent(
        architect_agent: Agent,
        agent_input: dict,
        genetic_operator_agent: Agent | None = None,
        generated_agent_engine_type: str | None = None,
        generated_agent_input: type[BaseModel] | None = None,
        generated_agent_output: type[BaseModel] | None = None,
        generated_model_endpoint_id: str | None = None,
        forge_cycle_id: str | None = None,
        forge_description: str | None = None,
    ) -> "Agent":
        from ebiose.core.agent import Agent # Local import
        from ebiose.core.agent_engine_factory import AgentEngineFactory # Local import

        output = await architect_agent.run(agent_input, master_agent_id=architect_agent.id, forge_cycle_id=forge_cycle_id)
        try:
            agent_name = forge_description
            agent_description = output.description
            agent_engine_configuration = {
                "graph": output.model_dump(),
                "input_model": generated_agent_input.model_json_schema() if generated_agent_input is not None else {},
                "output_model": generated_agent_output.model_json_schema() if generated_agent_output is not None else {},
            }
            agent_id = "agent-" + str(uuid.uuid4())

            generated_agent_engine = AgentEngineFactory.create_engine(
                generated_agent_engine_type,
                agent_id=agent_id,
                configuration=agent_engine_configuration,
                model_endpoint_id=generated_model_endpoint_id,
            )
        except Exception as e:
            logger.debug(f"Architect agent failed creating a valid agent: {e!s}")
            return None

        try:
            new_agent = Agent(
                name=agent_name,
                description=agent_description,
                id=agent_id,
                architect_agent_id=architect_agent.id,
                genetic_operator_agent_id=genetic_operator_agent.id,
                agent_engine=generated_agent_engine,
            )
        except Exception as e:
            logger.debug(f"Architect agent failed creating a valid agent: {e!s}")
            new_agent = None

        return new_agent


    @staticmethod
    async def crossover_agents(
        crossover_agent: Agent,
        input_data: BaseModel,
        generated_agent_engine_type: str | None = None,
        generated_agent_input: type[BaseModel] | None = None,
        generated_agent_output: type[BaseModel] | None = None,
        generated_model_endpoint_id: str | None = None,
        architect_agent: Agent | None = None,
        parent_ids: list[str] | None = None,
        master_agent_id: str | None = None,
        forge_cycle_id: str | None = None,
        forge_description: str | None = None,
    ) -> tuple["Agent", "Agent"] | "Agent" :
        from ebiose.core.agent import Agent # Local import
        from ebiose.core.agent_engine_factory import AgentEngineFactory # Local import
        
        output = await crossover_agent.run(input_data, master_agent_id=master_agent_id, forge_cycle_id=forge_cycle_id)
        try:
            agent_name = forge_description
            agent_description = output.description
            agent_engine_configuration = {
                "graph": output.model_dump(),
                "input_model": generated_agent_input.model_json_schema() if generated_agent_input is not None else {},
                "output_model": generated_agent_output.model_json_schema() if generated_agent_output is not None else {},
            }
            agent_id = "agent-" + str(uuid.uuid4())
            generated_agent_engine = AgentEngineFactory.create_engine(
                engine_type=generated_agent_engine_type,
                agent_id=agent_id,
                configuration=agent_engine_configuration,
                model_endpoint_id=generated_model_endpoint_id,
            )

            new_agent = Agent(
                name=agent_name,
                description=agent_description,
                id=agent_id,
                architect_agent_id=architect_agent.id if architect_agent else None,
                genetic_operator_agent_id=crossover_agent.id,
                agent_engine=generated_agent_engine,
                parent_ids=parent_ids,
            )
        except Exception as e:
            logger.debug(f"Crossover agent failed creating a valid agent: {e!s}")
            new_agent = None

        return new_agent
