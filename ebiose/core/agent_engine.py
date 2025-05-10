"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from abc import abstractmethod

from langfuse.decorators import observe
from pydantic import BaseModel


class AgentEngine(BaseModel):
    engine_type: str
    agent_id: str
    configuration: dict | None = None

    async def run(self, agent_input: BaseModel, master_agent_id: str | None = None) -> any:
        return await self._run_implementation(agent_input, master_agent_id)

    @observe(name="run_agent")
    @abstractmethod
    async def _run_implementation(self, agent_input: BaseModel, master_agent_id: str | None = None) -> any:
        pass
