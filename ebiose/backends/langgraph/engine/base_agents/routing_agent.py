from __future__ import annotations

from langchain_core.messages import AnyMessage
from pydantic import BaseModel

from ebiose.core.engines.graph_engine.edge import Edge
from ebiose.core.engines.graph_engine.graph import Graph
from ebiose.core.engines.graph_engine.nodes.llm_node import LLMNode
from ebiose.core.engines.graph_engine.nodes.node import EndNode, StartNode
from ebiose.backends.langgraph.engine.regex_routing_node import (
        LangGraphRegexRoutingNode,
)

SHARED_CONTEXT_PROMPT = """You are part of a router agent that must analyse the
following message and decide which condition applies best amongst: {possible_output}.
The message is:
{last_message}
"""

def init_routing_agent(model_endpoint_id: str) -> None:
        from ebiose.core.agent import Agent
        from ebiose.core.agent_engine_factory import AgentEngineFactory

        class AgentInput(BaseModel):
            last_message: AnyMessage
            possible_output: list[str]

        class AgentOutput(BaseModel):
            output_condition: str | None = None

        shared_context_prompt = SHARED_CONTEXT_PROMPT

        llm_router_node = LLMNode(
            id="llm_router_node",
            name="llm_router",
            purpose="This node is a router to select the next node to route to.",
            prompt="Append the selected condition to the end of your response.",
            temperature=0.0,
        )

        regex_routing_node = LangGraphRegexRoutingNode(id="regex_routing_node", name="regex_routing_node")

        start_node = StartNode()
        end_node = EndNode()

        graph = Graph(shared_context_prompt=shared_context_prompt)

        graph.add_node(start_node)
        graph.add_node(regex_routing_node)
        graph.add_node(llm_router_node)
        graph.add_node(end_node)

        graph.add_edge(
            Edge(start_node_id=start_node.id, end_node_id=regex_routing_node.id),
        )

        graph.add_edge(
            Edge(start_node_id=regex_routing_node.id, end_node_id=end_node.id, condition="found"),
        )

        graph.add_edge(
            Edge(start_node_id=regex_routing_node.id, end_node_id=llm_router_node.id, condition="not_found"),
        )

        graph.add_edge(
            Edge(start_node_id=llm_router_node.id, end_node_id=regex_routing_node.id),
        )

        agent_configuration = {"graph": graph}

        agent_engine = AgentEngineFactory.create_engine(
            "langgraph_engine",
            agent_configuration,
            model_endpoint_id=model_endpoint_id,
            input_model=AgentInput,
            output_model=AgentOutput,
        )

        agent_engine.recursion_limit = 7

        return Agent(
            name="routing_agent",
            description="Agent to route to the next node",
            architect_agent=None,
            genetic_operator_agent=None,
            agent_engine=agent_engine,
        )
