"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from datetime import UTC, datetime
import traceback
from typing import TYPE_CHECKING, ClassVar, Literal

from litellm import acompletion, completion
from loguru import logger
from openai import RateLimitError
from pydantic import BaseModel

from ebiose.cloud_client.ebiose_api_client import EbioseAPIClient
from ebiose.core.llm_api import LLMApi, LLMAPIConfig
from ebiose.core.model_endpoint import ModelEndpoints
from litellm.cost_calculator import cost_per_token, completion_cost


if TYPE_CHECKING:
    from langchain_core.messages import AnyMessage


class EbioseLLMApiError(Exception):
    """Custom exception for errors during LLM calls."""
    def __init__(self, message:str, original_exception: Exception | None=None, llm_identifier:str | None=None) -> None:
        super().__init__(message)
        self.original_exception = original_exception
        self.llm_identifier = llm_identifier

    def __str__(self) -> str:
        error_msg = f"EbioseLLMApiError"
        if self.llm_identifier:
            error_msg += f" (LLM: {self.llm_identifier})"
        error_msg += f": {super().__str__()}"
        if self.original_exception:
            orig_traceback = traceback.format_exception(
                type(self.original_exception),
                self.original_exception,
                self.original_exception.__traceback__
            )
            error_msg += f"\n--- Caused by ---\n{''.join(orig_traceback)}"
        return error_msg


class EbioseLLMApi(LLMApi):
    @classmethod
    def initialize(
        cls,
        mode: Literal["local", "cloud"], 
        lite_llm_api_key: str | None = None, 
        lite_llm_api_base: str | None = None,
        llm_api_config: LLMAPIConfig | None = None,
    ) -> EbioseLLMApi:
        cls.mode = mode
        cls.lite_llm_api_key = lite_llm_api_key
        
        # Set lite_llm_api_base based on mode and available configuration
        if lite_llm_api_base is not None:
            # Use provided base URL (typically from cloud API)
            cls.lite_llm_api_base = lite_llm_api_base
        elif mode == "local" and ModelEndpoints.use_lite_llm():
            # Use local configuration from model_endpoints.yml
            _, configured_base = ModelEndpoints.get_lite_llm_config()
            cls.lite_llm_api_base = configured_base
        else:
            # Keep as None - no LiteLLM base URL available
            cls.lite_llm_api_base = None

        if llm_api_config is not None:
            cls._llm_api_config = llm_api_config

        return cls


    @classmethod
    async def _call_llm(cls, model_endpoint_id: str, messages: list[AnyMessage], temperature: float, max_tokens: int, tools: list | None = None) -> AnyMessage:
        """Call the LLM using Langchain's AzureChatOpenAI.

        Args:
            model_endpoint_id: The ID of the model endpoint to use
            messages: List of messages to send to the LLM
            temperature: Temperature parameter for the LLM
            max_tokens: Maximum number of tokens allowed in the response
            tools: List of tools to bind to the LLM

        Returns:
            The LLM's response text
        """
        if tools is None:
            tools = []

        messages = [
            message.model_dump() for message in messages
        ]
        
        return await acompletion(
            model=model_endpoint_id,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            api_key=cls.lite_llm_api_key,
            api_base=cls.lite_llm_api_base,
            api_version="2024-12-01-preview",
        )

    @classmethod
    async def process_llm_call(
        cls,
        model_endpoint_id: str,
        messages: list[AnyMessage],
        agent_id: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        tools: list | None = None,
    ) -> AnyMessage:

        try:
            # Record the request and tokens
            response = await cls._call_llm(model_endpoint_id, messages, temperature, max_tokens, tools)
            if response is None:
                return None

            completion_tokens = response.response_metadata["token_usage"].get("completion_tokens", 0)
            prompt_tokens = response.response_metadata["token_usage"].get("prompt_tokens", 0)

            model = (
                "azure/" + model_endpoint_id[len("azure-"):]
                if model_endpoint_id.startswith("azure-")
                else model_endpoint_id
            )
            cost = cost_per_token(
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )

            cost = sum(cost)
            cls.add_agent_cost(agent_id, cost)

        except Exception as e:
            logger.debug(f"Error when calling {model_endpoint_id}: {e!s}")
            msg = "Failed during call to an LLM API"
            raise EbioseLLMApiError(msg, e, model_endpoint_id) from e
        else:
            return response
