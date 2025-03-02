"""LLMNode Node subclass.

This module contains the LLMNode class which represents a node containing a large language model.
"""

from __future__ import annotations

import abc
from typing import Literal

from pydantic import BaseModel, Field

from ebiose.core.engines.graph_engine.nodes.node import BaseNode


class LLMNode(BaseNode, abc.ABC):
    """The LLM node denotes the involvement of a Large Language Model in processing or decision-making stages within the graph.

    Each LLM node should be assigned a meaningful name and a clear purpose, reflecting
    its role in the problem-solving process. The LLM nodes contribute to the overall problem-solving capacity
    of the AI model, leveraging the unique capabilities of each LLM to enhance the network's reasoning and
    decision-making capabilities.

    A "LLMNode" node denotes the involvement of a Large Language Model in processing or decision-making stages
    within the graph. Each LLM node should be assigned a meaningful name and a clear purpose, reflecting
    its role in the problem-solving process. The LLM nodes contribute to the overall problem-solving capacity
    of the AI model, leveraging the unique capabilities of each LLM to enhance the network's reasoning and
    decision-making capabilities.

    Attributes:
        name: A convenient name for aesthetic purposes (displayed in the graph)
        purpose: An explanation of what the node is used for
        prompt: The prompt used to generate the output of the model

    """

    type: Literal["LLMNode"] = "LLMNode"
    purpose: str = Field(..., description="An explanation of what the node is used for")
    prompt: str = Field(
        ...,
        description="The prompt used to generate the output of the model",
    )
    # TODO(xabier): which others fields should be generated here? llm_model, temperature, etc.

    # TODO(xabier):  abstract class
    # https://github.com/ebiose-ai/ebiose/issues/44

    async def call_node(self, agent_state: BaseModel | dict, config: BaseModel | None = None) -> dict:  # noqa: ARG002 TODO: remove this noqa
        """Basic call_node where there is only a common prompt in the graph and a list of messages where there are additively stacked."""
        msg = "This method depends on the backend used to call the LLM model"
        raise NotImplementedError(
            msg,
        )
