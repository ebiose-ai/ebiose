"""Agent Node subclass.

This node is used to select an agent from the agent pool.
"""

from __future__ import annotations

import abc
from typing import Literal

from pydantic import BaseModel, Field

from ebiose.core.agent import Agent
from ebiose.core.engines.graph_engine.nodes.node import BaseNode


class AgentNode(BaseNode, abc.ABC):

    type: Literal["AgentNode"] = "AgentNode"
    name: str = Field(default_factory=lambda: id)  # if name isn't provided, use id
    # TODO(xabier): agent_id instead of agent, as agent embeds the agent_engine for now
    # and an architect agent will select an agent without considering the type of agent engine
    agent: Agent = Field(..., description="The agent to be used")

    def get_input_model(self) -> type[BaseModel]:
        return self.agent.agent_engine.input_model

    def get_output_model(self) -> type[BaseModel]:
        return self.agent.agent_engine.output_model

    # TODO(issue):  abstract class
    # https://github.com/ebiose-ai/ebiose/issues/44
    async def call_node(self, agent_state: BaseModel | dict, config: BaseModel | None = None) -> dict:
        """Basic call_node where there is only a common prompt in the graph and a list of messages where there are additively stacked."""
        msg = "This method depends on the backend used to call the LLM model"
        raise NotImplementedError(
            msg,
        )
