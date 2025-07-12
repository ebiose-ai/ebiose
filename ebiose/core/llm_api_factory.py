"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ebiose.llm_api.llm_api import LLMApi, LLMAPIConfig


class LLMApiFactory:
    """Factory for creating and managing LLM API instances."""
    
    _current_implementation: type[LLMApi] | None = None
    
    @classmethod
    def register_implementation(cls, implementation: type[LLMApi]) -> None:
        """Register the concrete LLM API implementation to use."""
        cls._current_implementation = implementation
    
    @classmethod
    def get_api(cls) -> type[LLMApi]:
        """Get the current LLM API implementation."""
        if cls._current_implementation is None:
            # Default to LangGraph implementation
            from ebiose.backends.langgraph.llm_api import LangGraphLLMApi
            cls._current_implementation = LangGraphLLMApi
        return cls._current_implementation
    
    @classmethod
    def initialize(
        cls,
        mode: Literal["local", "cloud"], 
        lite_llm_api_key: str | None = None, 
        lite_llm_api_base: str | None = None,
        llm_api_config: LLMAPIConfig | None = None,
    ) -> LLMApi:
        """Initialize the LLM API with the current implementation."""
        api = cls.get_api()
        return api.initialize(mode, lite_llm_api_key, lite_llm_api_base, llm_api_config)
    
    @classmethod
    def get_total_cost(cls, forge_cycle_id: str | None = None) -> float:
        """Get the total cost spent on the agents."""
        api = cls.get_api()
        return api.get_total_cost(forge_cycle_id)
    
    @classmethod
    def get_agent_cost(cls, agent_id: str) -> float:
        """Get the cost spent on a specific agent."""
        api = cls.get_api()
        return api.get_agent_cost(agent_id)
