"""Utility functions for the ebiose backend."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ebiose.core.engines.graph_engine.utils import GraphUtils

if TYPE_CHECKING:
    from pydantic import BaseModel

    from ebiose.core.engines.graph_engine.edge import Edge

from langgraph.graph.graph import END


class UnsupportedModelError(ValueError):
    """Exception raised for unsupported models."""

    def __init__(self, model: str) -> None:
        """Exception raised for unsupported models."""
        super().__init__(f"Model {model} is not supported")


class NodesCoherenceError(ValueError):
    """Exception raised when multiple StartNode are found."""

    def __init__(self, start_node_id: set[str]) -> None:
        """Exception raised when multiple StartNode are found."""
        super().__init__(f"Multiple start nodes found in the ids {start_node_id}")


class EdgeConditionError(ValueError):
    """Exception raised when the condition is not found in the edge."""

    def __init__(self, condition: str) -> None:
        message = f"No edge found with the condition {condition}."
        super().__init__(message)



def get_path(conditional_edges: list[Edge], end_node_id: str) -> callable:
    """Decide in which node to go next depending on the condition.

    Args:
        conditional_edges (list[Edge]): List of conditional edges.
        end_node_id (str): ID of the end node.

    Returns:
        callable: Function to determine the next node.
    """
    start_node_id = {edge.start_node_id for edge in conditional_edges}
    if len(start_node_id) > 1:
        raise NodesCoherenceError(start_node_id)
    start_node_id = start_node_id.pop()

    async def path(state: BaseModel, config: dict[str, any]) -> str:
        condition = None
        if "condition" in state.model_fields and state.condition is not None and len(state.condition) > 0:
            condition = state.condition
        else:
            # call the routing agent
            model_endpoint_id = config["configurable"]["model_endpoint_id"]
            compute_token = config["configurable"]["compute_token"]
            routing_agent = GraphUtils.get_routing_agent(model_endpoint_id)
            routing_agent_input = routing_agent.agent_engine.input_model(
                last_message=state.messages[-1],
                possible_output=[edge.condition for edge in conditional_edges],
            )
            routing_final_state = await routing_agent.run(routing_agent_input, compute_token)
            condition = routing_final_state.output_condition

        for edge in conditional_edges:
            if edge.condition == condition:
                return edge.end_node_id if edge.end_node_id != end_node_id else END

        message = f"No condition found in the last {start_node_id} response." \
            if condition is None else f"No edge found with the condition {condition}."
        raise ValueError(message)

    # Unlike LangGraph's documentation indicates, the path_map is required
    path_map = [
        edge.end_node_id if edge.end_node_id != end_node_id else END
        for edge in conditional_edges
    ]
    return path, path_map
