"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations
import uuid

from langchain_core.messages import AnyMessage  # noqa: TC002
from pydantic import BaseModel

from ebiose.backends.langgraph.engine.pydantic_validator_node import (
        LangGraphPydanticValidatorNode,
)
from ebiose.core.engines.graph_engine.edge import Edge
from ebiose.core.engines.graph_engine.graph import Graph
from ebiose.core.engines.graph_engine.nodes.llm_node import LLMNode
from ebiose.core.engines.graph_engine.nodes.node import EndNode, StartNode

SHARED_CONTEXT_PROMPT = """You are part of a graph agent which goal is to format the following message
into a given structured output.
The message is:
{last_message}
"""

def init_structured_output_agent(output_model: type[BaseModel], model_endpoint_id: str) -> None:
        from ebiose.core.agent import Agent
        from ebiose.core.agent_engine_factory import AgentEngineFactory

        class AgentInput(BaseModel):
            last_message: AnyMessage | None = None

        class AgentOutput(output_model):
            pass

        shared_context_prompt = SHARED_CONTEXT_PROMPT

        llm_formatter_node = LLMNode(
            id="llm_with_structured_output",
            name="llm_with_structured_output",
            purpose="This node uses an LLM to format an input into a given structured output",
            prompt="Format the input into a structured output following the schema given as a tool.",
            tools= [output_model],
            temperature=0.0,
        )

        pydantic_validator_node = LangGraphPydanticValidatorNode(id="validator_node", name="validator_node")

        start_node = StartNode()
        end_node = EndNode()

        graph = Graph(shared_context_prompt=shared_context_prompt)

        graph.add_node(start_node)
        graph.add_node(llm_formatter_node)
        graph.add_node(pydantic_validator_node)
        graph.add_node(end_node)

        graph.add_edge(
            Edge(start_node_id=start_node.id, end_node_id=llm_formatter_node.id),
        )
        graph.add_edge(
            Edge(start_node_id=llm_formatter_node.id, end_node_id=pydantic_validator_node.id),
        )
        graph.add_edge(
            Edge(start_node_id=pydantic_validator_node.id, end_node_id=end_node.id, condition="success"),
        )
        graph.add_edge(
            Edge(start_node_id=pydantic_validator_node.id, end_node_id=llm_formatter_node.id, condition="failure"),
        )

        agent_configuration = {"graph": graph}
        agent_id = "agent-" + str(uuid.uuid4())

        agent_engine = AgentEngineFactory.create_engine(
            "langgraph_engine",
            agent_configuration,
            agent_id=agent_id,
            model_endpoint_id=model_endpoint_id,
            input_model=AgentInput,
            output_model=AgentOutput,
        )

        agent_engine.recursion_limit = 7

        return Agent(
            name="structured_output_agent",
            id=agent_id,
            description="Agent to structure an input message into a given structured output",
            architect_agent=None,
            genetic_operator_agent=None,
            agent_engine=agent_engine,
        )
