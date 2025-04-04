"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from datetime import UTC, datetime
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

from ebiose.compute_intensive_batch_processor.compute_intensive_batch_processor import (
    ComputeIntensiveBatchProcessor,
)
from ebiose.core.model_endpoint import ModelEndpoints
from ebiose.tools.llm_token_cost import LLMTokenCost
from litellm.cost_calculator import cost_per_token


if TYPE_CHECKING:
    from langchain_core.messages import AnyMessage

class LangGraphComputeIntensiveBatchProcessor(ComputeIntensiveBatchProcessor):

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
        request_timeout = LangGraphComputeIntensiveBatchProcessor._llm_api_config.request_timeout_in_minutes * 60
        max_retries = LangGraphComputeIntensiveBatchProcessor._llm_api_config.max_retries

        model_endpoint = ModelEndpoints.get_model_endpoint(model_endpoint_id)

        if ModelEndpoints.use_lite_llm_proxy():
            lite_llm_api_key, lite_llm_api_base = ModelEndpoints.get_lite_llm_config()
            return ChatOpenAI(
                openai_api_key=lite_llm_api_key,
                openai_api_base=lite_llm_api_base,
                model=model_endpoint_id,
                temperature=temperature if model_endpoint_id != "azure/o3-mini" else 1.0,
                max_tokens=max_tokens,
            )
        
        elif ModelEndpoints.use_lite_llm():
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
        llm = LangGraphComputeIntensiveBatchProcessor._get_llm(model_endpoint_id, temperature, max_tokens)

        # Add tools
        if tools:
            llm = llm.bind_tools(tools=tools)

        # Call LLM
        try:
            response = await llm.with_retry(
                retry_if_exception_type=(RateLimitError,),  # APITimeoutError
                wait_exponential_jitter=True,
                stop_after_attempt=10,
            ).ainvoke(messages)
        except Exception as e:
            logger.debug(f"Error when calling {model_endpoint_id}: {e!s}")
            return None

        # Return the response content
        return response

    @classmethod
    async def process_llm_call(
        cls,
        model_endpoint_id: str,
        messages: list[AnyMessage],
        token_guid: str,
        temperature: float = 0.0,
        max_tokens: int = 4096, # TODO(xabier): 4096 is the maximum number of tokens allowed by OpenAI GPT-4o, should be handled by
        tools: list | None = None,
    ) -> AnyMessage:

        LangGraphComputeIntensiveBatchProcessor.check_initialized()
        if not LangGraphComputeIntensiveBatchProcessor._token_manager.token_exists(token_guid):
            msg = f"Token guid {token_guid} not found"
            raise ValueError(msg)

        # TODO(xabier): reactivate when checked
        # while not await cls._can_process(model_endpoint.endpoint_id, estimated_output_tokens):
        #     await asyncio.sleep(1)  # noqa: ERA001

        try:
            # Record the request and tokens
            now = datetime.now(tz=UTC)
            cls._request_counts[model_endpoint_id].append(now)

            response = await cls._call_llm(model_endpoint_id, messages, temperature, max_tokens, tools)
            if response is None:
                return None
            total_tokens = response.response_metadata["token_usage"].get("total_tokens", 0)
            completion_tokens = response.response_metadata["token_usage"].get("completion_tokens", 0)
            prompt_tokens = response.response_metadata["token_usage"].get("prompt_tokens", 0)
            cls._token_counts[model_endpoint_id].append((now, total_tokens))

            if ModelEndpoints.use_lite_llm():
                # TODO(xabier): remove this stupid condition
                model = (
                    "azure/" + model_endpoint_id[len("azure-"):]
                    if model_endpoint_id.startswith("azure-")
                    else model_endpoint_id
                )
                cost = cost_per_token(
                    model=model, 
                    prompt_tokens=prompt_tokens, 
                    completion_tokens=completion_tokens
                )
                cost = sum(cost)

            else:
                cost = LLMTokenCost.compute_token_cost(
                    model_endpoint_id, prompt_tokens, completion_tokens
                )
                
            cls._token_costs[model_endpoint_id].append((now, cost))
            LangGraphComputeIntensiveBatchProcessor._token_manager.add_cost(token_guid, cost)

        except Exception as e:
            logger.debug(f"Error when calling {model_endpoint_id}: {e!s}")
            return None
        else:
            return response
