from __future__ import annotations

from abc import abstractmethod

from langfuse.decorators import observe
from pydantic import BaseModel


class AgentEngine(BaseModel):
    engine_type: str
    configuration: str | dict

    async def run(self, agent_input: BaseModel, compute_token_id: str) -> any:
        return await self._run_implementation(agent_input, compute_token_id)

    @observe(name="run_agent")
    @abstractmethod
    async def _run_implementation(self, agent_input: BaseModel, compute_token_id: str) -> any:
        pass
