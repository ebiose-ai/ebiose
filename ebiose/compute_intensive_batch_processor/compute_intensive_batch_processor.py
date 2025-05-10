"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import BaseModel


class LLMAPIConfig(BaseModel):
    request_timeout_in_minutes: float = 2.0
    max_retries: int = 1

class ComputeIntensiveBatchProcessor:
    _llm_api_config: LLMAPIConfig = LLMAPIConfig()
    mode: Literal["local", "cloud"] = "cloud"
    lite_llm_api_key: str | None = None
    lite_llm_api_base: str | None = None
    cost_per_agent: ClassVar[dict[str, float]] = {}

    @classmethod
    def initialize(
        cls, 
        mode: Literal["local", "cloud"], 
        lite_llm_api_key: str | None = None, 
        llm_api_config: LLMAPIConfig | None = None,
    ) -> None:
        cls.mode = mode
        # TODO(xabier): check where to declare api key and base
        cls.lite_llm_api_key = lite_llm_api_key
        cls.lite_llm_api_base = "https://ebiose-litellm.livelysmoke-ef8b125f.francecentral.azurecontainerapps.io/"

        if llm_api_config is not None:
            cls._llm_api_config = llm_api_config

    @classmethod
    def get_spent_cost(cls) -> float:
        """Get the total cost spent on the agents."""
        return sum(cls.cost_per_agent.values())

    @classmethod
    def get_agent_cost(cls, agent_id: str) -> float:
        """Get the cost spent on a specific agent."""
        return cls.cost_per_agent.get(agent_id, 0.0)
    
    @classmethod
    def reset_cost_per_agent(cls) -> None:
        """Reset the cost per agent."""
        cls.cost_per_agent = {}

