"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations
import uuid

from langchain_core.messages import AnyMessage  # noqa: TC002
from pydantic import BaseModel

from ebiose.backends.langgraph.engine.routing_node import (
    LangGraphRoutingNode,
)
from ebiose.core.engines.graph_engine.edge import Edge
from ebiose.core.engines.graph_engine.graph import Graph
from ebiose.core.engines.graph_engine.nodes.llm_node import LLMNode
from ebiose.core.engines.graph_engine.nodes.node import EndNode, StartNode

SHARED_CONTEXT_PROMPT = """You are part of a router agent that must analyse the
following message and decide which condition applies best amongst: {possible_output}.
The message is:
{last_message}
"""

class AgentInput(BaseModel):
    last_message: AnyMessage
    possible_output: list[str]

class AgentOutput(BaseModel):
    output_condition: str | None = None

def init_routing_agent(model_endpoint_id: str) -> None:
        from ebiose.core.models.agent_models import Agent
        from ebiose.backends.langgraph.engine.langgraph_engine import LangGraphEngine

        shared_context_prompt = SHARED_CONTEXT_PROMPT

        llm_router_node = LLMNode(
            id="llm_router_node",
            name="llm_router",
            purpose="This node is a router to select the next node to route to.",
            prompt="Append the selected condition to the end of your response.",
            temperature=0.0,
        )

        routing_node = LangGraphRoutingNode(id="routing_node", name="routing_node")

        start_node = StartNode()
        end_node = EndNode()

        graph = Graph(shared_context_prompt=shared_context_prompt)

        graph.add_node(start_node)
        graph.add_node(routing_node)
        graph.add_node(llm_router_node)
        graph.add_node(end_node)

        graph.add_edge(
            Edge(start_node_id=start_node.id, end_node_id=routing_node.id),
        )

        graph.add_edge(
            Edge(start_node_id=routing_node.id, end_node_id=end_node.id, condition="found"),
        )

        graph.add_edge(
            Edge(start_node_id=routing_node.id, end_node_id=llm_router_node.id, condition="not_found"),
        )

        graph.add_edge(
            Edge(start_node_id=llm_router_node.id, end_node_id=routing_node.id),
        )

        agent_id = "agent-cb88834e-cb03-4cf9-b983-2b18fdbbcdc9"

        agent_engine = LangGraphEngine(
            agent_id=agent_id,
            graph=graph,
            model_endpoint_id=model_endpoint_id,
            input_model=AgentInput,
            output_model=AgentOutput,
            tags = ["routing_agent"],
        )

        agent_engine.recursion_limit = 7

        return Agent(
            name="routing_agent",
            id=agent_id,
            description="Agent to route to the next node",
            agent_engine=agent_engine,
        )
