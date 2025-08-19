"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ebiose.core.llm_api import LLMApi, LLMAPIConfig


class LLMApiFactory:
    """Factory for creating and managing LLM API instances."""

    llm_api: LLMApi | None = None

    @classmethod
    def initialize(
        cls,
        mode: Literal["local", "cloud"], 
        lite_llm_api_key: str | None = None, 
        lite_llm_api_base: str | None = None,
        llm_api_config: LLMAPIConfig | None = None,
        llm_api_type: Literal["ebiose", "langgraph"] = "langgraph", 
    ) -> LLMApi:
        """Initialize the LLM API and return the instance."""
        if cls.llm_api is not None:
            return cls.llm_api
        if llm_api_type == "ebiose":
            from ebiose.llm_api.ebiose import EbioseLLMApi
            cls.llm_api = EbioseLLMApi.initialize(mode, lite_llm_api_key, lite_llm_api_base, llm_api_config)
        elif llm_api_type == "langgraph":
            # Import LangGraph LLM API only if needed to avoid circular imports
            from ebiose.llm_api.langchain import LangChainLLMApi
            return LangChainLLMApi.initialize(mode, lite_llm_api_key, lite_llm_api_base, llm_api_config)
        else:
            raise ValueError(f"Unsupported LLM API type: {llm_api_type}")
        return cls.llm_api
    
    @classmethod
    def get_llm_api(cls) -> LLMApi:
        """Get the initialized LLM API instance."""
        if cls.llm_api is None:
            raise RuntimeError("LLM API has not been initialized. Call initialize() first.")
        return cls.llm_api