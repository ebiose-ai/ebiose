"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

import ast
import uuid
from typing import Literal

from langchain_core.messages import AIMessage, AnyMessage, ToolCall, ToolMessage
from pydantic import BaseModel, Field

from ebiose.backends.langgraph.engine.states import (
    LangGraphEngineInputState,
    LangGraphEngineOutputState,
)
from ebiose.core.engines.graph_engine.nodes.pydantic_validator_node import (
    PydanticValidatorNode,
)


class InputState(LangGraphEngineInputState):
    output_model: type[BaseModel] | None = Field(None, exclude=True)

class OutputState(LangGraphEngineOutputState):
    condition: Literal["success", "failure"] | None = None

class LangGraphPydanticValidatorNode(PydanticValidatorNode):

    input_state_model: type[BaseModel] = InputState
    output_state_model: type[BaseModel] = OutputState

    def get_messages(self, condition: str, error: Exception | None = None) -> list[AnyMessage]:
        tool_call_id=f"call_{self.id}_{uuid.uuid4()}"[40]
        tool_call = ToolCall(
            name=self.name,
            args={},
            id=tool_call_id,
        )

        messages = [
            AIMessage(
                content="",
                tool_calls=[tool_call],
            ),
        ]

        if condition == "success":
            messages.append(
                ToolMessage(
                    name=self.name,
                    content="Pydantic validation successful",
                    tool_call_id=tool_call_id,
                ),
            )
        else:
            messages.append(
                ToolMessage(
                    name=self.name,
                    content=f"Pydantic validation failed with error:\n{error!s}",
                    tool_call_id=tool_call_id,
                ),
            )

        return messages

    async def call_node(self, state: InputState | dict, config: BaseModel | None = None) -> OutputState:
        try:
            tool_messages = []
            for message in reversed(state.messages):
                if isinstance(message, ToolMessage):
                    tool_messages.append(message)
                else:
                    break

            output_model = config["configurable"]["output_model"]
            tool_contents = [
                ast.literal_eval(tool_message.content) for tool_message in tool_messages
            ]
            tool_content_args = {}
            for tool_content in tool_contents:
                tool_content_args.update(tool_content["args"])

            try:
                output = output_model.model_validate(tool_content_args)
            except Exception as e:
                return self.output_state_model(
                    messages=self.get_messages("failure", error=e),
                    output=None,
                    error_message=str(e),
                    condition="failure",
                    )

            return self.output_state_model(
                messages=self.get_messages("success"),
                output=output,
                condition="success",
            )

        except Exception as e:
            # TODO(xabier): send a different condition (eg validation_error vs other_error)
            return self.output_state_model(
                messages=self.get_messages("failure", error=e),
                output=None,
                error_message=str(e),
                condition="failure",
            )
