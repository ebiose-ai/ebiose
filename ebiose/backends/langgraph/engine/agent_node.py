"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from pydantic import BaseModel

from ebiose.core.engines.graph_engine.nodes.agent_node import AgentNode


class InputState(BaseModel):
    pass

class OutputState(BaseModel):
    pass

class LangGraphAgentNode(AgentNode):

    input_state_model: type[BaseModel] = InputState
    output_state_model: type[BaseModel] = OutputState

    async def call_node(self, state: InputState, config: BaseModel | None = None) -> OutputState: # type: ignore  # noqa: PGH003
        agent_input = self.agent.agent_engine.input_model.model_validate(
            state.model_dump(),
        )
        response = await self.agent.run(
            agent_input,
            compute_token_id=config["configurable"]["compute_token"],
        )

        # TODO(xabier): return also a tool message
        return response.model_dump()

