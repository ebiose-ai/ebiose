"""Agent engine base classes with improved architecture."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from ebiose.core.models.exceptions import AgentEngineRunError


class AgentEngine(BaseModel, ABC):
    """Base class for all agent engines."""

    engine_type: str
    agent_id: str | None = None
    configuration: dict[str, Any] | None = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    async def run(
        self,
        agent_input: BaseModel,
        master_agent_id: str,
        forge_cycle_id: str | None = None,
        **kwargs: dict[str, Any],
    ) -> Any:
        """Run the agent engine."""
        try:
            return await self._run_implementation(
                agent_input,
                master_agent_id,
                forge_cycle_id,
                **kwargs,
            )
        except Exception as e:
            raise AgentEngineRunError(
                message="Error during agent engine run",
                original_exception=e,
                agent_identifier=self.agent_id,
            ) from e

    @abstractmethod
    async def _run_implementation(
        self,
        agent_input: BaseModel,
        master_agent_id: str,
        forge_cycle_id: str | None = None,
        **kwargs: dict[str, Any],
    ) -> Any:
        """Implementation of the agent engine run method."""
        pass
