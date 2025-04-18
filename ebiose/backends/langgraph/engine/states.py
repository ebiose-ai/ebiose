"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from collections.abc import Sequence  # noqa: TC003
from typing import Annotated

from langchain_core.messages import AnyMessage  # noqa: TC002
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field, computed_field


class LangGraphEngineInputState(BaseModel):
    messages: Annotated[Sequence[AnyMessage], add_messages] = []
    input: BaseModel = Field(..., serialization_exclude=True)
    error_message: str = ""

class LangGraphEngineOutputState(BaseModel):
    messages: Annotated[Sequence[AnyMessage], add_messages] = []
    error_message: str = ""
    output: BaseModel | None = Field(default=None, serialization_exclude=True)

    @computed_field
    @property
    def n_messages(self) -> int:
        return len(self.messages)


class LangGraphEngineState(LangGraphEngineInputState, LangGraphEngineOutputState):
    pass

class LangGraphEngineConfig(BaseModel):
    model_endpoint_id: str = Field(..., description="The id of the model endpoint to use")
    output_model: type[BaseModel] | None = Field(default=None, serialization_exclude=True)
    shared_context_prompt: str
    callbacks: list
    recursion_limit: int = Field(default=15)
    tags: list[str] = Field(default_factory=list)
    agent_id: str
    master_agent_id: str | None = Field(default=None)
