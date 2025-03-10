"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BaseNode(BaseModel):
    """The BaseNode abstract class represents a node in a graph.

    Attributes:
        id: The identifier of the node
        type: The type of the node
    """

    id: str
    name: str
    model_config = ConfigDict(extra="allow")

    @abstractmethod  # Must be implemented
    async def call_node(self, state: BaseModel | dict, config: BaseModel | None = None) -> dict:
        pass


class StartNode(BaseNode):
    """The StartNode class represents the starting node in a graph. There should be only one StartNode in a graph.

    The "StartNode" node serves as the initiation point for the problem-solving process,
    signifying the commencement of the AI model's reasoning cycle. It has no other function
    than to initiate the problem-solving process, and there must be only one "StartNode" node within the graph.

    Attributes:
    id: The identifier of the node
    type: The type of the node which is StartNode
    """

    id: str = Field(default="start_node")
    name: str = Field(default="start_node")
    type: Literal["StartNode"] = "StartNode"

    async def call_node(self, state: BaseModel | dict, config: BaseModel | None = None) -> dict:
        pass


class EndNode(BaseNode):
    """The EndNode class represents the ending node in a graph. There should be only one EndNode in a graph.

    The "EndNode" node signifies the completion of a thought or decision cycle, marking the conclusion
    of the AI model's reasoning process. It encapsulates the final output or decision derived from
    the problem-solving network, providing a clear endpoint for the model's cognitive journey.
    There must be only one "EndNode" node within the graph, reflecting the completion of a thought or decision cycle.

    Attributes:
    id: The identifier of the node
    type: The type of the node which is EndNode

    """

    id: str = Field(default="end_node")
    name: str = Field(default="end_node")
    type: Literal["EndNode"] = "EndNode"

    async def call_node(self, state: BaseModel | dict, config: BaseModel | None = None) -> dict:
        pass
