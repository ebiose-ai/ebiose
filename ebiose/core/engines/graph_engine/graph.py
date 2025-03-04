"""This module contains the Graph class which is the basis of an Agent."""

from __future__ import annotations

from typing import Literal, LiteralString, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    ValidationInfo,
    field_validator,
    model_validator,
)

from ebiose.core.engines.graph_engine.edge import Edge
from ebiose.core.engines.graph_engine.nodes import NodeTypes, node_types_map
from ebiose.core.engines.graph_engine.nodes.node import BaseNode, EndNode


class Graph(BaseModel):
    """Graph used to represent the agent workflow on solving a problem.

    The graph is formed by a series of nodes, each representing a distinct stage in the problem-solving
    process.
    The nodes are connected by edges, which signify the flow of information and decision-making
    within the graph.

    Each node type has a specific role and function within the graph, contributing to the overall
    problem-solving capacity of the AI model.


    Attributes:
            edges: list of edges in the graph
            nodes: list of nodes in the graph
            description: Description of the graph purpose
            shared_context_prompt: Prompt shared among all nodes in the graph

    """

    edges: list[Edge] = Field(
        default_factory=list,
        description="list of edges in the graph",
    )
    nodes: list[NodeTypes] = Field(
        default_factory=list,
        description="list of nodes in the graph",
    )

    description: str = ""
    shared_context_prompt: str = Field(min_length=1)

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="after")
    def validate_graph(self, info: ValidationInfo) -> Graph:  # noqa: ARG002
        """Validate the graph by checking placeholders and outgoing conditional edges."""
        msg = ""

        # Validate outgoing conditional edges
        msg += self.__validate_outgoing_conditional_edges()

        # check edges and nodes
        node_ids = {node.id for node in self.nodes}
        node_ids_in_edges = set([edge.start_node_id for edge in self.edges] + [edge.end_node_id for edge in self.edges])

        # add a message for nodes that are not in the edges
        for node_id in node_ids - node_ids_in_edges:
            msg += f"Node with id {node_id} is not connected to any edge."

        # add a message for edges that points to non-existing nodes
        for node_id in node_ids_in_edges - node_ids:
            msg += f"Edge with id {node_id} is pointing to a non-existing node."

        # check for duplicated edges
        msg += self.__validate_edges()

        if msg != "":
            raise ValueError(msg)

        return self

    def __validate_edges(self) -> str:
        duplicated_transition_keys = set()
        transitions = {}
        for edge in self.edges:
            transition_key = (edge.start_node_id, edge.end_node_id)
            if transition_key in transitions:
                duplicated_transition_keys.add(transition_key)
            transitions[transition_key] = edge
        if len(duplicated_transition_keys) > 0:
            return f"Edges between the following nodes are duplicated: {duplicated_transition_keys}. Keep only one edge between two same nodes."

        return ""

    def __validate_outgoing_conditional_edges(self) -> str:
        """Check for each node that has outgoing conditional edges, if it has at least two conditional edges."""
        nodes_with_errors = []
        for node in self.nodes:
            # Count the number of condtionnal outgoing edges and check if number is less than 2
            conditional_outgoing_edges = [
                edge
                for edge in self.edges
                if edge.start_node_id == node.id and edge.is_conditional()
            ]
            outgoing_edges = [
                edge
                for edge in self.edges
                if edge.start_node_id == node.id
            ]
            if len(conditional_outgoing_edges) == 1 and len(outgoing_edges) == 1:
                # if node has a unique edge which is conditional, remove condition
                for edge in self.edges:
                    if edge.start_node_id == node.id:
                        edge.condition = None
            elif len(conditional_outgoing_edges)>0 and len(conditional_outgoing_edges) != len(outgoing_edges):
                # if node has several edges but not all are conditional
                nodes_with_errors.append(node.id)

        if len(nodes_with_errors) > 0:
            nodes_str = ", ".join(nodes_with_errors)
            return f"The following nodes have several outgoing edges but not all are conditional: {nodes_str}. In this case, all outgoing edges must be conditional. Add conditions to all outgoing edges."

        return ""

    @field_validator("nodes", mode="before")
    @classmethod
    def validate_nodes(cls, nodes: any) -> list[NodeTypes]:
        """Validate the nodes in the graph and generate explicit errors for retries."""
        if not isinstance(nodes, list):
            msg = "Field 'nodes' should be a list"
            raise TypeError(msg)

        if len(nodes) == 0:
            msg = "Field 'nodes' cannot be empty."
            raise ValueError(msg)

        errors, validated_nodes = Graph.__validate_nodes(nodes)
        if errors:
            raise ValidationError.from_exception_data(
                title=cls.__name__,
                line_errors=errors,
            )

        return validated_nodes

    @field_validator("edges", mode="before")
    @classmethod
    def validate_edges(cls, edges: any) -> list[Edge]:
        """Validate the nodes in the graph and generate explicit errors for retries."""
        if not isinstance(edges, list):
            msg = "Field 'edges' should be a list"
            raise TypeError(msg)

        if len(edges) == 0:
            msg = "Field 'edges' cannot be empty."
            raise ValueError(msg)

        return edges

    @classmethod
    def __validate_nodes(cls, nodes: list[dict]) -> tuple[list, list] | None:
        validated_nodes = []
        errors = []

        for index, node in enumerate(nodes):
            if not isinstance(node, dict):
                errors.append(
                    {
                        "loc": (index),
                        "type": "value_error",
                        "input": node,
                        "ctx": {
                            "error": ValueError(
                                f"Type of node should be a dict, got {type(node)}",
                            ),
                        },
                    },
                )

            # turn int id into str
            if "id" in node and isinstance(node["id"], int):
                node["id"] = str(node["id"])
            if "id" in node and ":" in node["id"]:
                node["id"] = node["id"].replace(":", "_")

            node_type = node.get("type", None)

            if node_type is None:
                # missing node type
                errors.append(
                    {
                        "loc": (index, "type"),
                        "msg": "Field required",
                        "type": "missing",
                        "input": node,
                    },
                )
                continue

            if node_type not in node_types_map:
                # invalid node type
                errors.append(
                    {
                        "loc": (index, "type"),
                        "type": "value_error",
                        "input": node,
                        "ctx": {"error": ValueError(f"Invalid node type: {node_type}")},
                    },
                )
                continue

            try:
                validated_nodes.append(
                    node_types_map[node_type].model_validate(node),
                )
            except ValidationError as e:
                for error in e.errors():
                    error["loc"] = (index,) + error["loc"]
                    errors.append(error)

        return errors, validated_nodes


    def add_edge(self: Self, edge: Edge) -> None:
        """Add an edge to the graph.

        Args:
                edge: An instance of the Edge class
        """
        self.edges.append(edge)

    def add_node(self: Self, node: BaseNode) -> None:
        """Add a node to the graph.

        Args:
                node: An instance of the Node class
        """
        # TODO(xabier): Improve performance
        # https://github.com/ebiose-ai/ebiose/issues/43
        if (
            node not in self.nodes
        ):  # TODO(xabier): add the node in ascending order in respect to id and edit get_node to have a binary search O(log(n))
            self.nodes.append(node)

    def get_node(self: Self, node_id: str) -> BaseNode:
        """Get a node from the graph.

        Args:
                node_id: The id of the node

        Returns:
                The node with the given id
        """
        # TODO(xabeir): Improve performance
        # https://github.com/ebiose-ai/ebiose/issues/43
        for node in self.nodes:
            if node.id == node_id:
                return node
        msg = f"Node with id {node_id} not found in the graph"
        raise ValueError(msg)

    def get_last_node_ids(self: Self) -> list[BaseNode]:
        """Get the ids of the last nodes in the graph.

        Returns:
                A list of ids of the nodes that have the EndNode as outgoing edges
        """
        return [
            edge.start_node_id
            for edge in self.edges
            if edge.end_node_id == self.get_end_node_id()
        ]

    def get_outgoing_nodes(
        self: Self,
        node_id: str,
        conditional: bool | None = None,
    ) -> list[BaseNode]:
        """Get the outgoing nodes of a node. By default, return all nodes connected to the node.

        Args:
                node_id: The id of the node
                conditional: If True, only return nodes that are connected by a conditional edge.If False, only return nodes that are connected by a non-conditional edge. If None, return all nodes.

        Returns:
                A list of nodes that are connected to the node
        """
        if conditional is None:
            return [
                self.get_node(edge.end_node_id)
                for edge in self.edges
                if edge.start_node_id == node_id
            ]
        if conditional:
            return [
                self.get_node(edge.end_node_id)
                for edge in self.edges
                if edge.start_node_id == node_id and edge.is_conditional()
            ]

        return [
            self.get_node(edge.end_node_id)
            for edge in self.edges
            if edge.start_node_id == node_id and not edge.is_conditional()
        ]

    def get_end_node_id(self) -> str:
        """Get the id of the end node in the graph.

        Returns: The id of the end node
        """
        for node in self.nodes:
            if isinstance(node, EndNode):
                return node.id
        msg = "End node not found in the graph"
        raise ValueError(msg)

    def get_outgoing_edges(
        self: Self,
        node_id: str,
        conditional: bool | None = None,
    ) -> list[Edge]:
        """Get the outgoing edges of a node. By default, return all edges connected to the node.

        node_id: The id of the node
        conditional: If True, only return edges that are conditional. If False, only return edges that are non-conditional. If None, return all edges.

        Returns: A list of edges that are connected to the node
        """
        if conditional is None:
            return [edge for edge in self.edges if edge.start_node_id == node_id]
        if conditional:
            return [
                edge
                for edge in self.edges
                if edge.start_node_id == node_id and edge.is_conditional()
            ]

        return [
            edge
            for edge in self.edges
            if edge.start_node_id == node_id and not edge.is_conditional()
        ]

    def to_mermaid_str(
        self: Self,
        orientation: Literal["TB", "TR", "TD", "RL", "LR"] = "TD",
    ) -> LiteralString | str:
        """Generate a mermaid string representation of the graph.

        Note:
                                The orientation of the graph can be set to one of the following values:

                                - **TB**: Top to bottom
                                - **TR**: Top to right
                                - **TD**: Top to down
                                - **RL**: Right to left
                                - **LR**: Left to right

        Args:
                                orientation: The orientation of the graph.
        """
        node_type_display_name = {
            "LLMNode": "({node_name})",
            "StartNode": "[{node_name}]",
            "EndNode": "[{node_name}]",
        }
        mermaid_str = f"graph {orientation}\n"

        for edge in self.edges:
            start_node = self.get_node(edge.start_node_id)
            end_node = self.get_node(edge.end_node_id)

            start_node_name = getattr(start_node, "name", start_node.id)
            end_node_name = getattr(end_node, "name", end_node.id)

            start_node_id = edge.start_node_id.replace(" ", "").title()
            end_node_id = edge.end_node_id.replace(" ", "").title()

            # Determine the appropriate brackets for the node type
            start_node_block = node_type_display_name.get(
                start_node.type,
                "[/{node_name}/]",
            ).format(node_name=start_node_name)
            end_node_block = node_type_display_name.get(
                end_node.type,
                "[/{node_name}/]",
            ).format(node_name=end_node_name)

            if edge.is_conditional():
                # replace the [ with #91; and ] with #93; to avoid mermaid syntax error
                condition = edge.condition.replace("[", "#91;").replace("]", "#93;")
                mermaid_str += f"\t{start_node_id}{start_node_block} -->|{condition}| {end_node_id}{end_node_block}\n"
            else:
                mermaid_str += f"\t{start_node_id}{start_node_block} --> {end_node_id}{end_node_block}\n"

        return mermaid_str
