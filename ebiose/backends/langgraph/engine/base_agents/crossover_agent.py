"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from pydantic import BaseModel, Field

from ebiose.core.engines.graph_engine.edge import Edge
from ebiose.core.engines.graph_engine.graph import Graph
from ebiose.core.engines.graph_engine.nodes import (
    get_node_types_docstrings,
    node_types_names,
)
from ebiose.core.engines.graph_engine.nodes.llm_node import LLMNode
from ebiose.core.engines.graph_engine.nodes.node import EndNode, StartNode


class AgentInput(BaseModel):
    forge_description: str
    node_types: list = ["StartNode", "LLMNode", "EndNode"]
    max_llm_nodes: int = 10
    node_types_description: str = Field(
        default_factory=lambda: get_node_types_docstrings(
            node_types_names,
        ),
    )
    parent_configuration1: dict
    parent_configuration2: dict

class AgentOutput(Graph):
    pass

SHARED_CONTEXT_PROMPT = """As an expert in Machine Learning, deeply immersed in the most
recent advancements in prompt engineering and the innovative application of LLMs, your
task is to architect an AI model that harnesses the power of multiple LLMs in a synergetic
communication network. You must act as a genetic crossover operator to cross two AI models
that were originally designed to\nsolve the following problem description. The resulting
new AI model should also be capable to solve\nthe same kind of problems, which is:\n
'{forge_description}'.
The goal of the crossover is to create an offspring made of the best of its parents
to improve the model's performance.\nYou can cross both the structure and the individual nodes of the graphs\n
Graphs are formed by a serie of nodes, each representing a distinct stage in the problem-solving
process. The nodes are connected by edges, which signify the flow of information and decision-making
within the graph.\n
NODES:\nThe nodes can be categorized into the following types: {node_types}.
Each node type has a specific role and function within the graph, contributing to the overall
problem-solving capacity of the AI model:\n
{node_types_description}\n
Be careful : Do not exceed {max_llm_nodes} LLM nodes in the graph.\n
EDGES:
The edges in the graph represent the connections between nodes, signifying the
flow of information and decision-making processes within the graph. These edges facilitate the
transition between different stages of the problem-solving process, guiding the AI model through
a series of cognitive and analytical steps. The edges can be either conditional or unconditional.\n
Conditional edges in the graph represent decision-based routing between nodes, where the transition
from one node to another is contingent upon specific conditions present in the response of the LLM
which is the starting node of the edge. Conditional edges must lead to different nodes,
ensuring that the AI model can make informed decisions based on the specific conditions present
in the LLM's output text.
For example, conditional edges may used to implement feedback loops within the problem-solving process,
such as moving from a critique phase back to a revision phase based on evaluative feedback.\n
Conditional edges must obey the following rules:\n- There can only be one condition per edge.
- There cannot be conditional edges involving the \"StartNode\" node.
- A node that has outgoing conditional edges must have at least two outgoing conditional edges.\n
"""


CROSSOVER_PROMPT = """The configuration graph of parent 1 is the following:
{parent_configuration1}
The configuration graph of parent 2 is the following:
{parent_configuration2}\n
Be creative in your approach, leveraging the unique capabilities of each parent graph to enhance the overall
problem-solving capacity of the offspring graph.\n
Create the offspring graph now and return it into the same format as its parents.",
"""

def init_crossover_agent(model_endpoint_id: str) -> None:
        from ebiose.core.agent import Agent
        from ebiose.core.agent_engine_factory import AgentEngineFactory

        crossover_node = LLMNode(
            id="crossover",
            name="Crossover",
            purpose="Step 1: Generate the outline of the graph",
            prompt=CROSSOVER_PROMPT,
            temperature=0.7,
        )

        start_node = StartNode()
        end_node = EndNode()

        graph = Graph(shared_context_prompt=SHARED_CONTEXT_PROMPT)

        graph.add_node(start_node)
        graph.add_node(crossover_node)
        graph.add_node(end_node)

        graph.add_edge(
            Edge(start_node_id=start_node.id, end_node_id=crossover_node.id),
        )

        graph.add_edge(
            Edge(start_node_id=crossover_node.id, end_node_id=end_node.id, condition="not_found"),
        )

        agent_configuration = {"graph": graph}

        agent_engine = AgentEngineFactory.create_engine(
            "langgraph_engine",
            agent_configuration,
            model_endpoint_id=model_endpoint_id,
            input_model=AgentInput,
            output_model=AgentOutput,
        )

        agent_engine.tags = ["crossover_agent"]

        return Agent(
            name="crossover_agent",
            description="Crossover agent that crosses two agents",
            architect_agent=None,
            genetic_operator_agent=None,
            agent_engine=agent_engine,
        )
