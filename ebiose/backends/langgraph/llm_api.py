"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from datetime import UTC, datetime
import traceback
from typing import TYPE_CHECKING

from langchain_community.chat_models.azureml_endpoint import (
    AzureMLChatOnlineEndpoint,
    AzureMLEndpointApiType,
    CustomOpenAIChatContentFormatter,
)
from langchain_community.chat_models import ChatLiteLLM

from langchain_openai import AzureChatOpenAI, ChatOpenAI
from loguru import logger
from openai import RateLimitError

from ebiose.llm_api.llm_api import (
    LLMApi,
)
from ebiose.core.model_endpoint import ModelEndpoints
from litellm.cost_calculator import cost_per_token, completion_cost


if TYPE_CHECKING:
    from langchain_core.messages import AnyMessage


class LangGraphLLMApiError(Exception):
    """Custom exception for errors during LLM calls."""
    def __init__(self, message:str, original_exception: Exception | None=None, llm_identifier:str | None=None) -> None:
        super().__init__(message)
        self.original_exception = original_exception
        self.llm_identifier = llm_identifier

    def __str__(self) -> str:
        error_msg = f"LangGraphLLMApiError"
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

class LangGraphLLMApi(LLMApi):

    @staticmethod
    def _get_llm(model_endpoint_id: str, temperature: float, max_tokens: int) -> AzureChatOpenAI:
        """Get the LLM model from the model endpoint id.

        Args:
            model_endpoint_id: The ID of the model endpoint to use
            temperature: Temperature parameter for the LLM
            max_tokens: Maximum number of tokens allowed in the response

        Returns:
            The LLM model
        """
        request_timeout = LangGraphLLMApi._llm_api_config.request_timeout_in_minutes * 60
        max_retries = LangGraphLLMApi._llm_api_config.max_retries

        model_endpoint = ModelEndpoints.get_model_endpoint(model_endpoint_id)

        if LangGraphLLMApi.mode == "cloud":
            return ChatOpenAI(
                openai_api_key=LangGraphLLMApi.lite_llm_api_key,
                openai_api_base=LangGraphLLMApi.lite_llm_api_base,
                model=model_endpoint_id,
                temperature=temperature if model_endpoint_id != "azure/o3-mini" else 1.0,
                max_tokens=max_tokens,
            )

        if ModelEndpoints.use_lite_llm(): # if model is compatible with LiteLLM, otherwise, custom implementation
            # TODO(xabier): check/test
            lite_llm_api_key, lite_llm_api_base = ModelEndpoints.get_lite_llm_config()
            default_model_id = ModelEndpoints.get_default_model_endpoint_id()

            return ChatLiteLLM(
                model=f"azure/{default_model_id}",
                azure_api_key=lite_llm_api_key,
                api_base=lite_llm_api_base,
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

        if model_endpoint.provider == "AzureML":
            # TODO(xabier): Add the max tokens argument
            return AzureMLChatOnlineEndpoint(
                endpoint_url=model_endpoint.endpoint_url.get_secret_value(),
                endpoint_api_type=AzureMLEndpointApiType.serverless,
                endpoint_api_key=model_endpoint.api_key.get_secret_value(),
                content_formatter=CustomOpenAIChatContentFormatter(),
                timeout=request_timeout,
                max_retries=max_retries,
                model_kwargs={"temperature": temperature},
            )

        if model_endpoint.provider == "Anthropic":
            from langchain_anthropic import (  # type: ignore  # noqa: PGH003
                ChatAnthropic,
            )
            return ChatAnthropic(
                model=model_endpoint_id,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=model_endpoint.api_key.get_secret_value(),
            )

        if model_endpoint.provider == "HuggingFace":
            from langchain_huggingface import (  # type: ignore  # noqa: PGH003
                ChatHuggingFace,
                HuggingFaceEndpoint,
            )

            llm = HuggingFaceEndpoint(
                repo_id=model_endpoint_id,
                task="text-generation",
                max_new_tokens=max_tokens,
            )

            return ChatHuggingFace(llm=llm, verbose=True)


        msg = f"Model endpoint {model_endpoint_id} not found"
        raise ValueError(msg)

    @staticmethod
    async def _call_llm(model_endpoint_id: str, messages: list[AnyMessage], temperature: float, max_tokens: int, tools: list | None = None) -> AnyMessage:
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
        llm = LangGraphLLMApi._get_llm(model_endpoint_id, temperature, max_tokens)

        # Add tools
        if tools:
            llm = llm.bind_tools(tools=tools)

        # Call LLM
        # TODO(xabier): check if LiteLLM also does retry
        return await llm.with_retry(
            retry_if_exception_type=(RateLimitError,),  # APITimeoutError
            wait_exponential_jitter=True,
            stop_after_attempt=10,
        ).ainvoke(messages)

    @classmethod
    async def process_llm_call(
        cls,
        model_endpoint_id: str,
        messages: list[AnyMessage],
        agent_id: str,
        temperature: float = 0.0,
        max_tokens: int = 4096, # TODO(xabier): 4096 is the maximum number of tokens allowed by OpenAI GPT-4o, should be handled by
        tools: list | None = None,
    ) -> AnyMessage:

        try:
            # Record the request and tokens
            response = await cls._call_llm(model_endpoint_id, messages, temperature, max_tokens, tools)
            if response is None:
                return None

            if LangGraphLLMApi.mode == "cloud":
                # TODO(xabier): remove this conditional formatting
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
                if agent_id not in cls.cost_per_agent:
                    cls.cost_per_agent[agent_id] = 0.0
                cls.cost_per_agent[agent_id] += cost
            else:
                # TODO(xabier): remove compute cost for local mode
                pass

        except Exception as e:
            logger.debug(f"Error when calling {model_endpoint_id}: {e!s}")
            msg = "Failed during call to an LLM API"
            raise LangGraphLLMApiError(msg, e, model_endpoint_id) from e
        else:
            return response
