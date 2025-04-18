"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class LLMAPIConfig(BaseModel):
    request_timeout_in_minutes: float = 2.0
    max_retries: int = 1

class ComputeIntensiveBatchProcessor:
    _llm_api_config: LLMAPIConfig = LLMAPIConfig()
    _mode: Literal["local", "cloud"] = "cloud"
    _cost_per_agent: dict[str, float] = {}

    @classmethod
    def initialize(cls, mode: Literal["local", "cloud"], llm_api_config: LLMAPIConfig = None) -> None:
        cls._mode = mode

        if llm_api_config is not None:
            cls._llm_api_config = llm_api_config

    @classmethod
    def get_spent_cost(cls) -> float:
        """Get the total cost spent on the agents."""
        return sum(cls._cost_per_agent.values())

    @classmethod
    def get_agent_cost(cls, agent_id: str) -> float:
        """Get the cost spent on a specific agent."""
        return cls._cost_per_agent.get(agent_id, 0.0)

