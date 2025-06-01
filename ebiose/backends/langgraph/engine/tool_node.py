"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations
import json
import traceback
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from loguru import logger
from pydantic import BaseModel, Field, computed_field

from ebiose.backends.langgraph.llm_api import (
    LangGraphLLMApi,
)
from ebiose.backends.langgraph.engine.states import (
    LangGraphEngineInputState,
    LangGraphEngineOutputState,
)
from ebiose.core.engines.graph_engine.nodes.llm_node import LLMNode
from ebiose.core.engines.graph_engine.nodes.node import BaseNode
from ebiose.core.engines.graph_engine.utils import get_placeholders


class InputState(LangGraphEngineInputState):
    pass

class OutputState(LangGraphEngineOutputState):
    pass

class LangGraphToolNode(BaseNode):
    tools: list = Field(default_factory=list)
    type: Literal["LLMNode"] = "LLMNode"
    purpose: str = Field(..., description="An explanation of what the node is used for")
    prompt: str = Field(
        ...,
        description="el",
    )
    input_state_model: type[BaseModel] = InputState
    output_state_model: type[BaseModel] = OutputState


    @computed_field
    def tools_by_name(self) -> dict:
        """Returns a dictionary mapping tool names to their respective Tool objects."""
        return {tool.name: tool for tool in self.tools}

    async def call_node(self, state: InputState, config: dict) -> OutputState:
        try:
            outputs = []
            for tool_call in state["messages"][-1].tool_calls:
                tool_result = self.tools_by_name[tool_call["name"]].invoke(tool_call["args"])
                outputs.append(
                    ToolMessage(
                        content=json.dumps(tool_result),
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"],
                    ),
                )
            return OutputState(messages=outputs)

        except Exception as e:
            logger.debug(f"Error when calling node {self.name}: {e!s}")
            msg = "Failed during call to a tool Node."
            raise ValueError(msg)
