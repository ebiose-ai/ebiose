# core/agentEngineFactory.py
from __future__ import annotations

from typing import TYPE_CHECKING

from ebiose.core.agent_engine import AgentEngine
from ebiose.backends.langgraph.engine.langgraph_engine import LangGraphEngine


if TYPE_CHECKING:
    from pydantic import BaseModel


class AgentEngineFactory:
    @staticmethod
    def create_engine(
            engine_type: str,
            configuration: str | dict,
            input_model: type[BaseModel] | None = None,
            output_model: type[BaseModel] | None = None,
            model_endpoint_id: str | None = None,
        ) -> AgentEngine:

        if engine_type == "langgraph_engine":
            return LangGraphEngine(
                configuration=configuration,
                input_model=input_model,
                output_model=output_model,
                model_endpoint_id=model_endpoint_id,
            )
        msg = f"Unknown engine type: {engine_type}"
        raise ValueError(msg)
