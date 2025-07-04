"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

import uuid
from pydantic import BaseModel, Field, computed_field

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
    parent_configuration: dict
    node_types_description: str | None = None
    n_llm_nodes_constraint_string: str | None = None

    # @computed_field
    # @property
    # def node_types_description(self) -> str:
    #     return get_node_types_docstrings(self.node_types)

class AgentOutput(Graph):
    pass

SHARED_CONTEXT_PROMPT = """As an expert in Machine Learning, deeply immersed in the most
recent advancements in prompt engineering and the innovative application of LLMs, your
task is to architect an AI model that harnesses the power of multiple LLMs in a synergetic
communication network. You must act as a genetic mutation operator to mutate an AI model
that was originally designed to\nsolve the following problem description. The resulting
new AI model should also be capable to solve\nthe same kind of problems, which is:\n
'{forge_description}'.
The goal of the mutation is to create an offspring that improves the performance of its parent.
Recall that graphs are formed by a serie of nodes, each representing a distinct stage in the problem-solving
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


MUTATION_PROMPT = """The graph to be mutated is the following:
{parent_configuration}
You can modify the graph structure by removing or adding one or more LLM nodes. 
The goal of this mutation is to improve the model's performance by exploring new avenues. 
If necessary, you can also modify any field of 
other existing nodes and edges.
You may also only improve the prompts of the existing nodes, or the conditions of the edges.
Be creative in your approach, leveraging the unique capabilities of each parent graph to enhance the overall
problem-solving capacity of the offspring graph.\n
Create the offspring graph now and return it into the same format as its parents.",
"""

def init_mutation_agent(model_endpoint_id: str | None) -> None:
    from ebiose.core.models.agent_models import Agent
    from ebiose.backends.langgraph.engine.langgraph_engine import LangGraphEngine

    mutation_node = LLMNode(
        id="mutation",
        name="Mutation",
        purpose="Mutate an existing agent",
        prompt=MUTATION_PROMPT,
        temperature=0.7,
    )

    start_node = StartNode()
    end_node = EndNode()

    graph = Graph(shared_context_prompt=SHARED_CONTEXT_PROMPT)

    graph.add_node(start_node)
    graph.add_node(mutation_node)
    graph.add_node(end_node)

    graph.add_edge(
        Edge(start_node_id=start_node.id, end_node_id=mutation_node.id),
    )

    graph.add_edge(
        Edge(start_node_id=mutation_node.id, end_node_id=end_node.id, condition="not_found"),
    )

    agent_id = "agent-b0d53155-4525-4d4a-92c8-145426f4a4bf"

    agent_engine = LangGraphEngine(
        agent_id=agent_id,
        graph=graph,
        model_endpoint_id=model_endpoint_id,
        input_model=AgentInput,
        output_model=AgentOutput,
        tags = ["mutation_agent"],
    )

    return Agent(
        name="mutation_agent",
        agent_type="genetic_operator",
        id=agent_id,
        description="Mutation agent that mutates an existingagent",
        agent_engine=agent_engine,
    )
