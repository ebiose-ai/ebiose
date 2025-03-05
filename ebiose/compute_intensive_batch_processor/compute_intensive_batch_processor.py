from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import ClassVar

from pydantic import BaseModel

from ebiose.compute_intensive_batch_processor.token_manager import TokenManager
from ebiose.core.model_endpoint import ModelEndpoint, ModelEndpoints


class LLMAPIConfig(BaseModel):
    request_timeout_in_minutes: float = 2.0
    max_retries: int = 1

class ComputeIntensiveBatchProcessor:
    _initialized = False
    _token_manager = TokenManager()
    _request_counts: ClassVar[dict[str, list[datetime]]] = {}
    _token_counts: ClassVar[dict[str, list[tuple[datetime, int]]]] = {}
    _token_costs: ClassVar[dict[str, list[tuple[datetime, float]]]] = {}
    _llm_api_config: LLMAPIConfig = LLMAPIConfig()

    @classmethod
    def initialize(cls, available_model_endpoints: list[ModelEndpoint] | None = None, llm_api_config: LLMAPIConfig = None) -> None:
        if available_model_endpoints is None:
            available_model_endpoints = ModelEndpoints.get_all_model_endpoints()
        cls._initialized = True
        cls._request_counts = {model_endpoint.endpoint_id: [] for model_endpoint in available_model_endpoints}
        cls._token_counts = {model_endpoint.endpoint_id: [] for model_endpoint in available_model_endpoints}
        cls._token_costs = {model_endpoint.endpoint_id: [] for model_endpoint in available_model_endpoints}
        if llm_api_config is not None:
            cls._llm_api_config = llm_api_config

    @classmethod
    def _clean_old_requests(cls, model_endpoint_id: str) -> None:
        now = datetime.now(tz=UTC)
        minute_ago = now - timedelta(minutes=1)

        # Clean request counters
        cls._request_counts[model_endpoint_id] = [
            ts for ts in cls._request_counts[model_endpoint_id]
            if ts > minute_ago
        ]

        # Clean token counters
        cls._token_counts[model_endpoint_id] = [
            (ts, tokens) for ts, tokens in cls._token_counts[model_endpoint_id]
            if ts > minute_ago
        ]

    # TODO(xabier): reactivate when checked
    """ @classmethod
    async def _can_process(cls, model_endpoint_id: str, tokens: int) -> bool:
        cls._clean_old_requests(model_endpoint_id)

        # Find the appropriate endpoint in the list of available endpoints
        model_endpoint = next(
            (endpoint for endpoint in cls._model_endpoints if endpoint.endpoint_id == model_endpoint_id),
            None,
        )

        if not model_endpoint:
            msg = f"Model endpoint {model_endpoint_id} not found"
            raise ValueError(msg)

        # Check RPM
        current_rpm = len(cls._request_counts[model_endpoint_id])
        if current_rpm >= model_endpoint.request_per_minute_limit:
            return False

        # Check TPM
        current_tpm = sum(tokens for _, tokens in cls._token_counts[model_endpoint_id])
        return not current_tpm + tokens > model_endpoint.token_per_minute_limit """



    # limit is in dollars
    @staticmethod
    def generate_token(limit: float, master_token: str) -> str:
        return ComputeIntensiveBatchProcessor._token_manager.generate_token(limit, master_token)

    @staticmethod
    def get_token_cost(token_guid: str) -> float:
        return ComputeIntensiveBatchProcessor._token_manager.get_token_cost(token_guid)

    @staticmethod
    def get_master_token_cost() -> float:
        return ComputeIntensiveBatchProcessor._token_manager.get_master_token_cost()

    @staticmethod
    def check_initialized() -> None:
        if not ComputeIntensiveBatchProcessor._initialized:
            msg = "ComputeIntensiveBatchProcessor has not been initialized. Call ComputeIntensiveBatchProcessor.initialize() first."
            raise RuntimeError(msg)

    @staticmethod
    def acquire_master_token(budget: float) -> str:
        return ComputeIntensiveBatchProcessor._token_manager.acquire_master_token(budget)
