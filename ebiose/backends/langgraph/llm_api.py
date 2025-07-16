"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

import asyncio
import time
import traceback
from collections import deque
from typing import TYPE_CHECKING, ClassVar, Literal

import httpx
from langchain_community.chat_models import ChatLiteLLM
from langchain_community.chat_models.azureml_endpoint import (
    AzureMLChatOnlineEndpoint,
    AzureMLEndpointApiType,
    CustomOpenAIChatContentFormatter,
)
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from litellm.cost_calculator import cost_per_token
from loguru import logger
from openai import APITimeoutError, RateLimitError
from pydantic import BaseModel

from ebiose.cloud_client.ebiose_api_client import EbioseAPIClient
from ebiose.core.model_endpoint import ModelEndpoints

if TYPE_CHECKING:
    from langchain_core.messages import AnyMessage


class LangGraphLLMApiError(Exception):
    """Custom exception for errors during LLM calls."""

    def __init__(
        self,
        message: str,
        original_exception: Exception | None = None,
        llm_identifier: str | None = None,
    ) -> None:
        super().__init__(message)
        self.original_exception = original_exception
        self.llm_identifier = llm_identifier

    def __str__(self) -> str:
        error_msg = "LangGraphLLMApiError"
        if self.llm_identifier:
            error_msg += f" (LLM: {self.llm_identifier})"
        error_msg += f": {super().__str__()}"
        if self.original_exception:
            orig_traceback = traceback.format_exception(
                type(self.original_exception),
                self.original_exception,
                self.original_exception.__traceback__,
            )
            error_msg += f"\n--- Caused by ---\n{''.join(orig_traceback)}"
        return error_msg


class RateLimiter:
    """Rate limiter using sliding window approach to limit calls per minute."""

    def __init__(self, max_calls_per_minute: int = 500):
        self.max_calls_per_minute = max_calls_per_minute
        self.call_times = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire permission to make a call, waiting if necessary."""
        async with self._lock:
            while True:
                current_time = time.time()

                # Remove calls older than 1 minute
                while self.call_times and current_time - self.call_times[0] >= 60:
                    self.call_times.popleft()

                # If we're at the limit, wait until we can make a call
                if len(self.call_times) >= self.max_calls_per_minute:
                    # Calculate how long to wait (until the oldest call is 1 minute old)
                    wait_time = (
                        60 - (current_time - self.call_times[0]) + 0.1
                    )  # Add small buffer
                    if wait_time > 0:
                        # logger.debug(
                        #     f"Rate limit reached. Waiting {wait_time:.2f} seconds...",
                        # )
                        # Release the lock while waiting
                        self._lock.release()
                        try:
                            await asyncio.sleep(wait_time)
                        finally:
                            # Re-acquire the lock
                            await self._lock.acquire()
                        # Continue the loop to check again
                        continue

                # We can make a call - record this call and exit
                self.call_times.append(current_time)
                # logger.debug(
                #     f"Rate limiter: {len(self.call_times)}/{self.max_calls_per_minute} calls in current minute",
                # )
                break


class LLMAPIConfig(BaseModel):
    request_timeout_in_minutes: float = 5.0  # Increased from 2.0 to 5.0
    max_retries: int = 3  # Increased from 1 to 3
    max_calls_per_minute: int = 500  # Rate limiting parameter
    exponential_backoff_base: float = 2.0  # New parameter for backoff
    max_backoff_time: float = 60.0  # New parameter for max backoff


class LangGraphLLMApi:
    _llm_api_config: LLMAPIConfig = LLMAPIConfig()
    mode: Literal["local", "cloud"] = "cloud"
    lite_llm_api_key: str | None = None
    lite_llm_api_base: str | None = None
    _cost_per_agent: ClassVar[dict[str, float]] = {}
    total_cost: ClassVar[float] = 0.0
    _rate_limiter: ClassVar[RateLimiter | None] = None

    @classmethod
    def initialize(
        cls,
        mode: Literal["local", "cloud"],
        lite_llm_api_key: str | None = None,
        lite_llm_api_base: str | None = None,
        llm_api_config: LLMAPIConfig | None = None,
    ) -> LangGraphLLMApi:
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

        # Initialize rate limiter
        cls._rate_limiter = RateLimiter(cls._llm_api_config.max_calls_per_minute)

        return cls

    # @classmethod
    # def update_total_cost(cls, new_cost: float | None = None) -> None:
    #     """Update the total cost and the cost for a specific agent."""
    #     if new_cost is None:
    #         cls.total_cost = new_cost

    @classmethod
    def get_agents_total_cost(cls) -> float:
        """Get the total cost spent on each agent."""
        return sum(cls._cost_per_agent.values())

    @classmethod
    def get_total_cost(cls, forge_cycle_id: str | None = None) -> float:
        """Get the total cost spent on the agents."""
        if cls.mode == "cloud" and forge_cycle_id is not None:
            # If in cloud mode, get the total cost from the API
            cls.total_cost = EbioseAPIClient.get_cost(forge_cycle_uuid=forge_cycle_id)
        return cls.get_agents_total_cost()

    @classmethod
    def add_agent_cost(cls, agent_id: str, cost: float) -> None:
        """Add the cost for a specific agent."""
        if agent_id in cls._cost_per_agent:
            cls._cost_per_agent[agent_id] += cost
        else:
            cls._cost_per_agent[agent_id] = cost

    @classmethod
    def get_agent_cost(cls, agent_id: str) -> float:
        """Get the cost spent on a specific agent."""
        return cls._cost_per_agent.get(agent_id, 0.0)

    # @classmethod
    # def reset_cost_per_agent(cls) -> None:
    #     """Reset the cost per agent."""
    #     cls.cost_per_agent = {}

    @classmethod
    def _get_llm(
        cls,
        model_endpoint_id: str,
        temperature: float,
        max_tokens: int,
    ) -> AzureChatOpenAI:
        """Get the LLM model from the model endpoint id.

        Args:
            model_endpoint_id: The ID of the model endpoint to use
            temperature: Temperature parameter for the LLM
            max_tokens: Maximum number of tokens allowed in the response

        Returns:
            The LLM model
        """
        request_timeout = cls._llm_api_config.request_timeout_in_minutes * 60
        max_retries = cls._llm_api_config.max_retries

        model_endpoint = ModelEndpoints.get_model_endpoint(model_endpoint_id)

        if cls.mode == "cloud":
            return ChatOpenAI(
                openai_api_key=cls.lite_llm_api_key,
                openai_api_base=cls.lite_llm_api_base,
                model=model_endpoint_id,
                temperature=temperature
                if model_endpoint_id != "azure/o3-mini"
                else 1.0,
                request_timeout=request_timeout,
                # max_tokens=max_tokens,  # TODO(xabier): some models such as ministral-3b does not support max_tokens
            )

        if ModelEndpoints.use_lite_llm() and ModelEndpoints.use_lite_llm_proxy():
            lite_llm_api_key, lite_llm_api_base = ModelEndpoints.get_lite_llm_config()
            return ChatOpenAI(
                openai_api_key=lite_llm_api_key,
                openai_api_base=lite_llm_api_base,
                model=model_endpoint_id,
                temperature=temperature
                if model_endpoint_id != "azure/o3-mini"
                else 1.0,
                request_timeout=request_timeout,
                # max_tokens=max_tokens,
            )

        if (
            ModelEndpoints.use_lite_llm()
        ):  # if model is compatible with LiteLLM, otherwise, custom implementation
            # TODO(xabier): check/test

            return ChatLiteLLM(
                model=f"azure/{model_endpoint.deployment_name}",
                azure_api_key=model_endpoint.api_key.get_secret_value(),
                api_base=model_endpoint.endpoint_url.get_secret_value(),
                temperature=temperature,
                request_timeout=request_timeout,
                max_retries=max_retries,
                max_tokens=max_tokens,
            )

        if model_endpoint.provider == "OpenAI":
            return ChatOpenAI(
                model=model_endpoint_id,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=model_endpoint.api_key.get_secret_value(),
            )

        if model_endpoint.provider == "OpenRouter":
            return ChatOpenAI(
                openai_api_base=model_endpoint.endpoint_url.get_secret_value(),
                model=model_endpoint_id,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=model_endpoint.api_key.get_secret_value(),
            )

        if model_endpoint.provider == "Azure OpenAI":
            return AzureChatOpenAI(
                azure_deployment=model_endpoint.deployment_name,
                azure_endpoint=model_endpoint.endpoint_url.get_secret_value(),
                openai_api_key=model_endpoint.api_key.get_secret_value(),
                openai_api_version=model_endpoint.api_version,
                temperature=temperature,
                request_timeout=request_timeout,
                max_retries=max_retries,
                max_tokens=max_tokens,
            )

        if model_endpoint.provider == "Azure AI":
            return AzureMLChatOnlineEndpoint(
                endpoint_url=model_endpoint.endpoint_url.get_secret_value(),
                endpoint_api_type=AzureMLEndpointApiType.serverless,
                endpoint_api_key=model_endpoint.api_key.get_secret_value(),
                content_formatter=CustomOpenAIChatContentFormatter(),
                timeout=request_timeout,
                max_retries=max_retries,
                max_tokens=max_tokens,
                model_kwargs={"temperature": temperature},
            )

        if model_endpoint.provider == "Anthropic":
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model=model_endpoint_id,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=model_endpoint.api_key.get_secret_value(),
            )

        if model_endpoint.provider == "HuggingFace":
            from langchain_huggingface import HuggingFaceEndpoint

            return HuggingFaceEndpoint(
                repo_id=model_endpoint_id,
                task="text-generation",
                max_new_tokens=max_tokens,
            )

        if model_endpoint.provider == "Google":
            from langchain_google_genai import ChatGoogleGenerativeAI

            return ChatGoogleGenerativeAI(
                model=model_endpoint_id,
                google_api_key=model_endpoint.api_key.get_secret_value(),
            )

        if model_endpoint.provider == "Ollama":
            from langchain_ollama import ChatOllama

            return ChatOllama(
                model=model_endpoint_id.replace("ollama/", ""),
                temperature=temperature,
                num_predict=max_tokens,
                base_url=model_endpoint.endpoint_url.get_secret_value(),
            )

        msg = f"Model endpoint {model_endpoint_id} not found"
        raise ValueError(msg)

    @classmethod
    async def _call_llm(
        cls,
        model_endpoint_id: str,
        messages: list[AnyMessage],
        temperature: float,
        max_tokens: int,
        tools: list | None = None,
    ) -> AnyMessage:
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
        llm = cls._get_llm(model_endpoint_id, temperature, max_tokens)

        # Add tools
        if tools:
            llm = llm.bind_tools(tools=tools)

        # Call LLM
        return await llm.with_retry(
            retry_if_exception_type=(
                RateLimitError,
                APITimeoutError,
                httpx.ReadTimeout,
                httpx.ConnectTimeout,
                httpx.TimeoutException,
            ),
            wait_exponential_jitter=True,
            stop_after_attempt=cls._llm_api_config.max_retries,
        ).ainvoke(messages)

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
        # Apply rate limiting before making the call
        if cls._rate_limiter is not None:
            await cls._rate_limiter.acquire()

        max_attempts = cls._llm_api_config.max_retries
        base_delay = cls._llm_api_config.exponential_backoff_base
        max_delay = cls._llm_api_config.max_backoff_time

        for attempt in range(max_attempts):
            try:
                # Record the request and tokens
                response = await cls._call_llm(
                    model_endpoint_id,
                    messages,
                    temperature,
                    max_tokens,
                    tools,
                )
                if response is None:
                    return None

                completion_tokens = response.response_metadata["token_usage"].get(
                    "completion_tokens",
                    0,
                )
                prompt_tokens = response.response_metadata["token_usage"].get(
                    "prompt_tokens",
                    0,
                )

                model = (
                    "azure/" + model_endpoint_id[len("azure-") :]
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
                return response

            except (
                APITimeoutError,
                httpx.ReadTimeout,
                httpx.ConnectTimeout,
                httpx.TimeoutException,
            ) as e:
                if attempt == max_attempts - 1:
                    logger.error(
                        f"Timeout error after {max_attempts} attempts for {model_endpoint_id}: {e!s}",
                    )
                    msg = f"Request timed out after {max_attempts} attempts"
                    raise LangGraphLLMApiError(msg, e, model_endpoint_id) from e

                # Calculate exponential backoff delay
                delay = min(base_delay**attempt, max_delay)
                logger.warning(
                    f"Timeout on attempt {attempt + 1}/{max_attempts} for {model_endpoint_id}. Retrying in {delay:.2f}s...",
                )
                await asyncio.sleep(delay)

            except RateLimitError as e:
                if attempt == max_attempts - 1:
                    logger.error(
                        f"Rate limit error after {max_attempts} attempts for {model_endpoint_id}: {e!s}",
                    )
                    msg = f"Rate limit exceeded after {max_attempts} attempts"
                    raise LangGraphLLMApiError(msg, e, model_endpoint_id) from e

                # For rate limits, use a longer delay
                delay = min(base_delay ** (attempt + 2), max_delay)
                logger.warning(
                    f"Rate limit on attempt {attempt + 1}/{max_attempts} for {model_endpoint_id}. Retrying in {delay:.2f}s...",
                )
                await asyncio.sleep(delay)

            except Exception as e:
                logger.debug(f"Error when calling {model_endpoint_id}: {e!s}")
                msg = "Failed during call to an LLM API"
                raise LangGraphLLMApiError(msg, e, model_endpoint_id) from e

        # This should never be reached due to the loop logic, but just in case
        msg = f"Unexpected error: exceeded maximum attempts ({max_attempts})"
        raise LangGraphLLMApiError(msg, None, model_endpoint_id)
