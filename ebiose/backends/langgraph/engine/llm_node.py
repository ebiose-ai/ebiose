"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from pydantic import BaseModel, Field

from ebiose.backends.langgraph.compute_intensive_batch_processor import (
    LangGraphComputeIntensiveBatchProcessor,
)
from ebiose.backends.langgraph.engine.states import (
    LangGraphEngineInputState,
    LangGraphEngineOutputState,
)
from ebiose.core.engines.graph_engine.nodes.llm_node import LLMNode
from ebiose.core.engines.graph_engine.utils import find_placeholders


class InputState(LangGraphEngineInputState):
    pass

class OutputState(LangGraphEngineOutputState):
    pass

class LangGraphLLMNode(LLMNode):
    temperature: float
    tools: list = Field(default_factory=list)
    input_state_model: type[BaseModel] = InputState
    output_state_model: type[BaseModel] = OutputState


    async def call_node(self, state: InputState, config: dict) -> OutputState:
        # All nodes have access to the shared context prompt
        shared_context_prompt = config["configurable"]["shared_context_prompt"]
        model_endpoint_id = config["configurable"]["model_endpoint_id"]
        output_conditions = []
        if self.id in config["configurable"] and "output_conditions" in config["configurable"][self.id]:
            output_conditions = config["configurable"][self.id]["output_conditions"]

        has_placeholders = find_placeholders(shared_context_prompt)
        if has_placeholders:
            shared_context_prompt = shared_context_prompt.format(
                **state.input.model_dump(),
            )
        else:
            shared_context_prompt += "\nInput: " + state.input.model_dump_json()
        prompts = [
            SystemMessage(
                shared_context_prompt + f"\nYour are the {self.name} node.",
            ),
        ]
        prompts += state.messages

        human_prompt = ""
        if len(state.error_message) == 0:
            human_prompt = self.prompt.format(
                output_schema=config["configurable"]["output_model"].schema_json(indent=2),
                **state.input.model_dump(),
            )
        else:
            # TODO(issue): improve the error message
            human_prompt = f"Your last response triggered the following error:\n{state.error_message}\nFix it."

        if len(output_conditions) > 0:
            human_prompt += f"\nAccording to your response, append at the end of your response one of the following conditions: {output_conditions}"

        prompts.append(HumanMessage(human_prompt))

        # instantiate model
        response = await LangGraphComputeIntensiveBatchProcessor.process_llm_call(
            model_endpoint_id=model_endpoint_id,
            messages=prompts,
            token_guid=config["configurable"]["compute_token"],
            tools=self.tools,
            temperature=self.temperature,
        )

        if response is None:
            return None

        messages = [response]
        if self.tools is not None and len(self.tools) > 0:
            for tool in response.tool_calls:
                messages.append(ToolMessage(content=tool, tool_call_id=tool["id"]))  # noqa: PERF401

        return OutputState(messages=messages)
