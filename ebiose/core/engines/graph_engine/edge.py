"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel


class Edge(BaseModel):
    """The Edge class represents a directed edge in a graph.

    conditional edges need to be used to implement feedback loops within the problem-solving process, such as moving from a critique phase back to a revision phase based on evaluative feedback.

    Warning:
        There can not be only one outgoing conditional edge from a node. At least two.

    Attributes:
        start_node_id: The start node **id** of the edge
        end_node_id: The last end node **id** of the edge
        condition: The condition which must be satisfied to pass from the start node to the end node

    Example:
        ```python
        edge = Edge(start_node_id="start", end_node_id="mid")
        edge = Edge(start_node_id="mid", end_node_id="end", condition="valid")
        edge = Edge(start_node_id="mid", end_node_id="fixer", condition="invalid")
        ```
    """

    start_node_id: str
    end_node_id: str
    condition: str | None = None

    def is_conditional(self: Self) -> bool:
        """Check if the edge is conditional."""
        return self.condition is not None

    def get_condition(self: Self) -> str | None:
        """Get the condition of the edge."""
        return self.condition
