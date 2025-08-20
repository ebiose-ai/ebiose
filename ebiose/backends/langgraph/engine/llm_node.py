"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations
import traceback

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from loguru import logger
from pydantic import BaseModel, Field

from ebiose.backends.langgraph.llm_api import (
    LangGraphLLMApi,
)
from ebiose.backends.langgraph.engine.states import (
    LangGraphEngineInputState,
    LangGraphEngineOutputState,
)
from ebiose.core.engines.graph_engine.nodes import get_n_llm_nodes_constraint_string, get_node_types_docstrings
from ebiose.core.engines.graph_engine.nodes.llm_node import LLMNode
from ebiose.core.engines.graph_engine.utils import get_placeholders
from langgraph.runtime import Runtime

class InputState(LangGraphEngineInputState):
    pass

class OutputState(LangGraphEngineOutputState):
    pass

class LangGraphLLMNodeError(Exception):
    """Custom exception for errors during LLM calls."""
    def __init__(self, message:str, original_exception: Exception | None=None, llm_identifier:str | None=None) -> None:
        super().__init__(message)
        self.original_exception = original_exception
        self.llm_identifier = llm_identifier

    def __str__(self) -> str:
        error_msg = f"LangGraphLLMNodeError"
        if self.llm_identifier:
            error_msg += f" (LLM: {self.llm_identifier})"
        error_msg += f": {super().__str__()}"
        if self.original_exception:
            orig_traceback = traceback.format_exception(
                type(self.original_exception),
                self.original_exception,
                self.original_exception.__traceback__,
            )
            error_msg += f"\n--- Caused by ---\n{''.join(orig_traceback)}"
        return error_msg

class LLMNodeContext(BaseModel):
    shared_context_prompt: str = Field(
        default="",
        description="A shared context prompt that is used by all nodes in the graph.",
    )
    model_endpoint_id: str = Field(
        default="",
        description="The ID of the model endpoint to use for LLM calls.",
    )
    agent_id: str = Field(
        default="",
        description="The ID of the agent that owns this node.",
    )

class LangGraphLLMNode(LLMNode):
    temperature: float
    tools: list = Field(default_factory=list)
    input_state_model: type[BaseModel] = InputState
    output_state_model: type[BaseModel] = OutputState

    async def call_node(self, state: InputState, runtime: Runtime[BaseModel]) -> OutputState:

        try:
            # All nodes have access to the shared context prompt
            shared_context_prompt = runtime.context.shared_context_prompt
            model_endpoint_id = runtime.context.model_endpoint_id
            agent_id = runtime.context.agent_id

            output_conditions = []
            if hasattr(runtime.context, self.id):
                node_context = getattr(runtime.context, self.id)
                if "output_conditions" in node_context:
                    output_conditions = node_context["output_conditions"]

            placeholders = get_placeholders(shared_context_prompt)
            # TODO(xabier): this is a temporary solution to generate missing fields for achitect agents
            if "node_types_description" in placeholders:
                state.input.node_types_description = get_node_types_docstrings(state.input.node_types)
            if "n_llm_nodes_constraint_string" in placeholders:
                state.input.n_llm_nodes_constraint_string = get_n_llm_nodes_constraint_string(
                    random_n_llm_nodes=state.input.random_n_llm_nodes,
                    max_llm_nodes=state.input.max_llm_nodes,
                )
            if len(placeholders) > 0:
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
                    output_schema=runtime.context.output_model.schema_json(indent=2),
                    **state.input.model_dump(),
                )
            else:
                # TODO(issue): improve the error message
                human_prompt = f"Your last response triggered the following error:\n{state.error_message}\nFix it."

            if len(output_conditions) > 0:
                human_prompt += f"\nAccording to your response, append at the end of your response one of the following conditions: {output_conditions}"

            prompts.append(HumanMessage(human_prompt))

            # instantiate model
            response = await LangGraphLLMApi.process_llm_call(
                model_endpoint_id=model_endpoint_id,
                agent_id=agent_id,
                messages=prompts,
                tools=self.tools,
                temperature=self.temperature,
            )
            messages = [response]
            if self.tools is not None and len(self.tools) > 0:
                for tool in response.tool_calls:
                    messages.append(ToolMessage(content=tool, tool_call_id=tool["id"]))  # noqa: PERF401

            return OutputState(messages=messages)

        except Exception as e:
            logger.debug(f"Error when calling node {self.name}: {e!s}")
            msg = "Failed during call to an LLM Node."
            raise LangGraphLLMNodeError(msg, e, f"{self.name}({self.id})") from e
