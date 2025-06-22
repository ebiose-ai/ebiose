"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from abc import abstractmethod
import traceback

# TODO(xabier): replace when langfuse is updated to >=3.0
# from langfuse import observe
from langfuse.decorators import observe

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class AgentEngineRunError(Exception):
    """Custom exception for errors during agent run."""
    def __init__(self, message:str, original_exception: Exception | None=None, agent_identifier:str | None=None) -> None:
        super().__init__(message)
        self.original_exception = original_exception
        self.agent_identifier = agent_identifier

    def __str__(self) -> str:
        error_msg = "AgentRunError"
        if self.agent_identifier:
            error_msg += f" (Agent: {self.agent_identifier})"
        error_msg += f": {super().__str__()}"
        if self.original_exception:
            orig_traceback = traceback.format_exception(
                type(self.original_exception),
                self.original_exception,
                self.original_exception.__traceback__,
            )
            error_msg += f"\n--- Caused by ---\n{''.join(orig_traceback)}"
        return error_msg

class AgentEngine(BaseModel):
    engine_type: str
    agent_id: str
    configuration: dict | None = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True, # Allows initializing with snake_case names
    )

    async def run(self, agent_input: BaseModel, master_agent_id: str, forge_cycle_id: str | None = None, **kwargs: dict[str, any]) -> any:
        try:
            return await self._run_implementation(agent_input, master_agent_id, forge_cycle_id, **kwargs)
        except Exception as e:
            raise AgentEngineRunError(
                message="Error during agent engine run",
                original_exception=e,
                agent_identifier=self.agent_id,
            ) from e

    @observe(name="run_agent")
    @abstractmethod
    async def _run_implementation(self, agent_input: BaseModel, master_agent_id: str, forge_cycle_id: str | None = None, **kwargs: dict[str, any]) -> any:
        pass
