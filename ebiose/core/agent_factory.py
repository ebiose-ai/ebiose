from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger

from ebiose.core.agent import Agent
from ebiose.core.agent_engine_factory import AgentEngineFactory

if TYPE_CHECKING:
    from pydantic import BaseModel


class AgentFactory:
    @staticmethod
    def load_agent(
        agent_config: dict,
        input_model: BaseModel,
        output_model: BaseModel,
        model_endpoint_id: str | None = None,
    ) -> Agent:

        # creating engine
        agent_engine = AgentEngineFactory.create_engine(
            engine_type=agent_config["agent_engine"]["engine_type"],
            configuration=agent_config["agent_engine"]["configuration"],
            model_endpoint_id=model_endpoint_id,
            input_model=input_model,
            output_model=output_model,
        )

        agent_config = agent_config.copy()
        agent_config["agent_engine"] = agent_engine
        agent_config["architect_agent"] = None
        agent_config["genetic_operator_agent"] = None

        return Agent.model_validate(agent_config)

    @staticmethod
    async def generate_agent(
        architect_agent: Agent,
        agent_input: dict,
        compute_token_id: str,
        genetic_operator_agent: Agent | None = None,
        generated_agent_engine_type: str | None = None,
        generated_agent_input: type[BaseModel] | None = None,
        generated_agent_output: type[BaseModel] | None = None,
        generated_model_endpoint_id: str | None = None,
    ) -> Agent:

        output = await architect_agent.run(agent_input, compute_token_id)
        try:
            agent_name = "TODO" # TODO(xabier): generate agent name
            agent_description = output.description
            agent_engine_configuration = {"graph": output.model_dump()}

            generated_agent_engine = AgentEngineFactory.create_engine(
                generated_agent_engine_type,
                agent_engine_configuration,
                input_model=generated_agent_input,
                output_model=generated_agent_output,
                model_endpoint_id=generated_model_endpoint_id,
            )
        except Exception as e:
            logger.debug(f"Architect agent failed creating a valid agent: {e!s}")
            return None

        try:
            new_agent = Agent(
                name=agent_name,
                description=agent_description,
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
        compute_token_id: str,
        generated_agent_engine_type: str | None = None,
        generated_agent_input: type[BaseModel] | None = None,
        generated_agent_output: type[BaseModel] | None = None,
        generated_model_endpoint_id: str | None = None,
        parent_ids: list[str] | None = None,
    ) -> tuple[Agent, Agent] | Agent :

        output = await crossover_agent.run(input_data, compute_token_id)
        try:
            agent_name = "TODO" # TODO(xabier): generate agent name
            agent_description = output.description
            agent_engine_configuration = {"graph": output.model_dump()}
            generated_agent_engine = AgentEngineFactory.create_engine(
                generated_agent_engine_type,
                agent_engine_configuration,
                input_model=generated_agent_input,
                output_model=generated_agent_output,
                model_endpoint_id=generated_model_endpoint_id,
            )

            new_agent = Agent(
                name=agent_name,
                description=agent_description,
                architect_agent=None,
                genetic_operator_agent=crossover_agent,
                agent_engine=generated_agent_engine,
                parent_ids=parent_ids,
            )
        except Exception as e:
            logger.debug(f"Crossover agent failed creating a valid agent: {e!s}")
            new_agent = None

        return new_agent
