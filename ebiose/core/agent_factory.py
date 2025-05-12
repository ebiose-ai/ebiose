"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
import uuid

from loguru import logger

from ebiose.core.agent import Agent
from ebiose.core.agent_engine_factory import AgentEngineFactory

if TYPE_CHECKING:
    from pydantic import BaseModel


class AgentFactory:
    @staticmethod
    def load_agent(
        agent_config: dict,
        model_endpoint_id: str | None = None,
    ) -> Agent:

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
    async def generate_agent(
        architect_agent: Agent,
        agent_input: dict,
        genetic_operator_agent: Agent | None = None,
        generated_agent_engine_type: str | None = None,
        generated_agent_input: type[BaseModel] | None = None,
        generated_agent_output: type[BaseModel] | None = None,
        generated_model_endpoint_id: str | None = None,
    ) -> Agent:

        output = await architect_agent.run(agent_input, master_agent_id=architect_agent.id)
        try:
            agent_name = "TODO" # TODO(xabier): generate agent name
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
                architect_agent=architect_agent,
                genetic_operator_agent=genetic_operator_agent,
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
        parent_ids: list[str] | None = None,
    ) -> tuple[Agent, Agent] | Agent :

        output = await crossover_agent.run(input_data)
        try:
            agent_name = "TODO" # TODO(xabier): generate agent name
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
                architect_agent=None,
                genetic_operator_agent=crossover_agent,
                agent_engine=generated_agent_engine,
                parent_ids=parent_ids,
            )
        except Exception as e:
            logger.debug(f"Crossover agent failed creating a valid agent: {e!s}")
            new_agent = None

        return new_agent
