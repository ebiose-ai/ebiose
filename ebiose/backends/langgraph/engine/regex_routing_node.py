from __future__ import annotations

import uuid
from collections.abc import Sequence  # noqa: TC003
from typing import ClassVar, Literal

from langchain_core.messages import AIMessage, AnyMessage, ToolCall, ToolMessage
from pydantic import BaseModel  # noqa: TC002

from ebiose.core.engines.graph_engine.nodes.regex_routing_node import (
    RegexRoutingNode,
)

from ebiose.backends.langgraph.engine.states import (
    LangGraphEngineInputState,
    LangGraphEngineOutputState,
)


class InputState(LangGraphEngineInputState):
    last_message: AnyMessage
    possible_output: Sequence[str]

class OutputState(LangGraphEngineOutputState):
    output_condition: str | None = None
    condition: Literal["found", "not_found"] | None = None

class LangGraphRegexRoutingNode(RegexRoutingNode):

    input_state_model: type[BaseModel] = InputState
    output_state_model: type[BaseModel] = OutputState

    def get_messages(self, condition: str, error_message: str | None = None) -> list[AnyMessage]:
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

        if condition == "found":
            messages.append(
                ToolMessage(
                    name=self.name,
                    content="Regex routing successful",
                    tool_call_id=tool_call_id,
                ),
            )
        else:
            messages.append(
                ToolMessage(
                    name=self.name,
                    content=f"Regex routing failed with error:\n{error_message}",
                    tool_call_id=tool_call_id,
                ),
            )

        return messages

    async def call_node(self, state: BaseModel | dict, config: None = None) -> dict:  # noqa: ARG002
        last_message_str = state.last_message.content.lower() \
            if len(state.messages)==0 else state.messages[-1].content.lower()
        possible_output = state.possible_output

        output_condition = None
        count = 0
        for condition in possible_output:
            if condition.lower() in last_message_str:
                count += 1
                output_condition = condition

        if count == 1:
            return self.output_state_model(
                messages=self.get_messages(condition="found"),
                condition="found",
                output_condition=output_condition,
            )
        error_message = "The message does not contain any of the possible conditions." \
            if count == 0 else "The message contains more than one of the possible conditions."
        return self.output_state_model(
            messages=self.get_messages("not_found", error_message=error_message),
            condition="not_found",
            error_message=error_message,
        )

