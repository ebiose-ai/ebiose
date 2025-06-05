"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import BaseModel

from ebiose.cloud_client.mock_ebiose_endpoints import EbioseAPIClient


class LLMAPIConfig(BaseModel):
    request_timeout_in_minutes: float = 2.0
    max_retries: int = 1

class LLMApi:
    _llm_api_config: LLMAPIConfig = LLMAPIConfig()
    mode: Literal["local", "cloud"] = "cloud"
    lite_llm_api_key: str | None = None
    lite_llm_api_base: str | None = None
    _cost_per_agent: ClassVar[dict[str, float]] = {}
    total_cost: ClassVar[float] = 0.0

    @classmethod
    def initialize(
        cls,
        mode: Literal["local", "cloud"], 
        lite_llm_api_key: str | None = None, 
        llm_api_config: LLMAPIConfig | None = None,
    ) -> LLMApi:
        cls.mode = mode
        # TODO(xabier): check where to decleare api key and base
        cls.lite_llm_api_key = lite_llm_api_key
        #TODO(xabier): remove this hardcoded value
        cls.lite_llm_api_base = "https://ebiose-litellm.livelysmoke-ef8b125f.francecentral.azurecontainerapps.io/"

        if llm_api_config is not None:
            cls._llm_api_config = llm_api_config

        return cls

    @classmethod
    def update_total_cost(cls, new_cost: float | None = None) -> None:
        """Update the total cost and the cost for a specific agent."""
        if new_cost is None:
            cls.total_cost = new_cost

    @classmethod
    def get_agents_total_cost(cls) -> float:
        """Get the total cost spent on each agent."""
        return sum(cls._cost_per_agent.values())

    @classmethod
    def get_total_cost(cls) -> float:
        """Get the total cost spent on the agents."""
        return cls.total_cost

    @classmethod
    def add_agent_cost(cls, agent_id: str, cost: float) -> None:
        """Add the cost for a specific agent."""
        if agent_id in cls._cost_per_agent:
            cls._cost_per_agent[agent_id] += cost
        else:
            cls._cost_per_agent[agent_id] = cost
        cls.update_total_cost(sum(cls._cost_per_agent.values()))


    @classmethod
    def get_agent_cost(cls, agent_id: str) -> float:
        """Get the cost spent on a specific agent."""
        return cls._cost_per_agent.get(agent_id, 0.0)
    
    # @classmethod
    # def reset_cost_per_agent(cls) -> None:
    #     """Reset the cost per agent."""
    #     cls.cost_per_agent = {}

