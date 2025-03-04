import random

from pydantic import BaseModel, computed_field

from ebiose.core.engines.graph_engine.edge import Edge
from ebiose.core.engines.graph_engine.graph import Graph
from ebiose.core.engines.graph_engine.nodes import (
    get_node_types_docstrings,
)
from ebiose.core.engines.graph_engine.nodes.llm_node import LLMNode
from ebiose.core.engines.graph_engine.nodes.node import EndNode, StartNode


class AgentInput(BaseModel):
    forge_description: str
    node_types: list = ["StartNode", "LLMNode", "EndNode"]
    max_llm_nodes: int = 10
    random_n_llm_nodes: bool = True

    @computed_field
    @property
    def node_types_description(self) -> str:
        return get_node_types_docstrings(self.node_types)

    @computed_field
    @property
    def n_llm_nodes_constraint_string(self) -> str:
        if self.random_n_llm_nodes:
                return f"Be careful : The number of LLM nodes in the graph must be of {random.randint(1, self.max_llm_nodes)} exactly."
        return f"Be careful : Do not exceed {self.max_llm_nodes} LLM nodes in the graph."



class AgentOutput(Graph):
    pass


SHARED_CONTEXT_PROMPT = """As an expert in Machine Learning, deeply immersed in the
most recent advancements in prompt engineering and the innovative application of LLMs,
your task is to architect an AI model that harnesses the power of multiple LLMs in a
synergetic communication network. Drawing upon the latest scholarly articles on the
collaborative functionalities of LLMs, such as chain-of-thought processing and
self-reflection methodologies, construct a dynamic model that visualizes the interaction
between these LLMs through a well-defined graph.\n
The created graph must address the following problem:
'{forge_description}'
\n
The graph is formed by a series of nodes, each representing a distinct stage in the
problem-solving process. The nodes are connected by edges, which signify the flow of
information and decision-making within the graph.\n
NODES:
The nodes can be categorized into the following types: {node_types}.
Each node type has a specific role and function within the graph, contributing to the overall
problem-solving capacity of the AI model:\n
{node_types_description}\n
{n_llm_nodes_constraint_string}\n
EDGES:\n
The edges in the graph represent the connections between nodes, signifying the flow of information
and decision-making processes within the graph. These edges facilitate the transition between
different stages of the problem-solving process, guiding the AI model through a series of cognitive
and analytical steps. The edges can be either conditional or unconditional.\n
Conditional edges in the graph represent decision-based routing between nodes, where the transition
from one node to another is contingent upon specific conditions present in the response of the LLM
which is the starting node of the edge. Conditional edges must lead to different nodes,
ensuring that the AI model can make informed decisions based on the specific conditions present
in the LLM's output text.\nFor example, conditional edges may used to implement feedback loops
within the problem-solving process, such as moving from a critique phase back to a revision phase
based on evaluative feedback.\n\nConditional edges must obey the following rules:
- There can only be one condition per edge.\n- There cannot be conditional edges involving the \"StartNode\" node.
- A node must have either, one unconditional outgoing edge, or, several conditional outgoing edges.
There cannot be a mix of both.
- A node might have several incoming edges, if and only if the incoming edges are all conditional.\n
"""


GRAPH_OUTLINE_GENERATION_PROMPT = """Step 1:\n
Your initial focus should be on developing the foundational structure of this graph,
given the problem statement provided and the following general guidelines. Don't
generate the prompts of LLM nodes yet as they will be generated in the next step.
Be creative in your approach, leveraging the unique capabilities of each LLM to enhance the overall
problem-solving capacity of the graph.\n
Generate this graph now.
"""

PROMPT_GENERATION_PROMPT = """Step 2:\n
With the foundational structure of the graph established in Step 1, your next task is to meticulously
craft the prompts for each LLM node, aligning with their distinct roles and purposes within the network.
This step is crucial for imbuing the AI model with the capability to navigate complex problem-solving
scenarios. The construction of these prompts should not only leverage the specialized skills of each
LLM but also ensure their integration into a cohesive system that promotes effective communication and
collaborative problem-solving.\n
For each LLM node identified in the graph, you will develop a custom prompt that guides the LLM in
executing its designated function. These prompts must be crafted with precision, incorporating elements
of chain-of-thought reasoning, self-reflection, and evaluative feedback mechanisms where applicable.
However, these mentioned techniques are merely examples of the vast array of cognitive and analytical
tools at your disposal. You are encouraged to explore beyond these strategies, tapping into the rich
landscape of computational thinking, creative problem-solving, and adaptive learning methods to enrich
the LLMs' problem-solving prowess.\n
The prompt of a LLM node must be specific to the role of the node in the graph and is in charge of guiding the LLM
to perform the task that is expected from it and to transmit all necessary information to the next node.\n
All LLM nodes will also share a contextual system prompt that describes the graph, the role of each node
and any other information that is relevant to the problem to be solved.\n
The goal is to enable each LLM to contribute meaningfully to the problem-solving process.\n
You must NEVER use placeholders in the prompts, such as {{placeholder}} or [placeholder], as
they will never be taken into account.\n
Respect these instructions but remain creative as the prompts will be determinant for the AI model's performance
and problem-solving capacity.\n
Generate the prompts now for each LLM node.
"""
# Generate the prompts and return the whole graph with prompts under the following format: \n {output_schema}".

FORMAT_PROMPT = """Step 3:\n
Now that the graph structure and LLM node prompts have been defined, the final step is to format the
entire graph with the prompts under the following format:\n
{output_schema}
"""


def init_architect_agent(
        model_endpoint_id: str,
        add_format_node: bool = True,  # noqa: FBT001, FBT002

    ) -> None:
        from ebiose.core.agent import Agent
        from ebiose.core.agent_engine_factory import AgentEngineFactory

        graph_outline_generation_node = LLMNode(
            id="graph_outline_generation",
            name="Graph Outline Generation",
            purpose="Step 1: Generate the outline of the graph",
            prompt=GRAPH_OUTLINE_GENERATION_PROMPT,
            temperature=0.7,
        )

        prompt_generation_prompt = PROMPT_GENERATION_PROMPT
        if add_format_node:
            prompt_generation_prompt + "Generate the prompts now for each LLM node."
        else:
            prompt_generation_prompt + "Generate the prompts and return the whole graph with prompts under the following format: \n {output_schema}"

        prompt_generation_node = LLMNode(
            id="prompt_generation",
            name="Prompt Generation",
            purpose="Step 2: Generate the prompts for each LLM node",
            prompt=PROMPT_GENERATION_PROMPT,
            temperature=0.7,
        )

        if add_format_node:
            format_node = LLMNode(
                id="format",
                name="Format",
                purpose="Step 3: Format the entire graph with the prompts",
                prompt=FORMAT_PROMPT,
                temperature=0,
                tools=[AgentOutput],
            )

        start_node = StartNode()
        end_node = EndNode()

        graph = Graph(shared_context_prompt=SHARED_CONTEXT_PROMPT)

        graph.add_node(start_node)
        graph.add_node(graph_outline_generation_node)
        graph.add_node(prompt_generation_node)
        graph.add_node(end_node)
        if add_format_node:
            graph.add_node(format_node)

        graph.add_edge(
            Edge(start_node_id=start_node.id, end_node_id=graph_outline_generation_node.id),
        )

        graph.add_edge(
            Edge(start_node_id=graph_outline_generation_node.id, end_node_id=prompt_generation_node.id),
        )

        if not add_format_node:
            graph.add_edge(
                Edge(start_node_id=prompt_generation_node.id, end_node_id=end_node.id),
            )
        else:
            graph.add_edge(
                Edge(start_node_id=prompt_generation_node.id, end_node_id=format_node.id),
            )
            graph.add_edge(
                Edge(start_node_id=format_node.id, end_node_id=end_node.id),
            )

        agent_configuration = {"graph": graph}

        agent_engine = AgentEngineFactory.create_engine(
            "langgraph_engine",
            agent_configuration,
            model_endpoint_id=model_endpoint_id,
            input_model=AgentInput,
            output_model=AgentOutput,
        )

        agent_engine.tags = ["architect_agent"]

        return Agent(
            name="architect_agent",
            description="Architect agent that generate agents",
            architect_agent=None,
            genetic_operator_agent=None,
            agent_engine=agent_engine,
        )
