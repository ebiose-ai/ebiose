"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

# core/agentEngineFactory.py
from __future__ import annotations

from typing import TYPE_CHECKING

from ebiose.backends.langgraph.engine.langgraph_engine import LangGraphEngine
from ebiose.core.agent_engine import AgentEngine
from ebiose.core.model_endpoint import ModelEndpoints

if TYPE_CHECKING:
    from pydantic import BaseModel


class AgentEngineFactory:
    @staticmethod
    def create_engine(
            engine_type: str,
            agent_id: str,
            configuration: dict,
            model_endpoint_id: str | None = None,
        ) -> AgentEngine:

        if engine_type == "langgraph_engine":
            if model_endpoint_id is None:
                model_endpoint_id = ModelEndpoints.get_default_model_endpoint_id()
            return LangGraphEngine(
                agent_id=agent_id,
                configuration=configuration,
                model_endpoint_id=model_endpoint_id,
            )
        msg = f"Unknown engine type: {engine_type}"
        raise ValueError(msg)
    
    # @staticmethod
    # def create_engine_from_api(
    #         engine_type: str,
    #         configuration: dict,
    #         model_endpoint_id: str | None = None,
    #     ) -> AgentEngine:

    #     if engine_type == "langgraph_engine":
    #         if model_endpoint_id is None:
    #             model_endpoint_id = ModelEndpoints.get_default_model_endpoint_id()
    #         return LangGraphEngine(
    #             engine_type=engine_type,
    #             agent_id=configuration["agent_id"],
    #             input_model=configuration["input_model"],
    #             output_model=configuration["output_model"],
    #             graph=configuration["graph"],
    #             # configuration=configuration["configuration"], # TODO(xabier): check if configuration can be removed
    #             model_endpoint_id=model_endpoint_id,
    #         )
    #     msg = f"Unknown engine type: {engine_type}"
    #     raise ValueError(msg)
