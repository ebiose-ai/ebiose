
import json
from pathlib import Path
from typing import ClassVar

from loguru import logger


def load_model_prices_and_context_window() -> dict:
    # TODO(xabier): fix the path to the json file
    # Compute the project root relative to this file
    project_root = Path(__file__).parents[2]
    json_path = project_root / "ebiose" / "tools" / "model_prices_and_context_window.json"
    
    with json_path.open() as f:
        return json.load(f)



class LLMTokenCost:
    _model_prices: ClassVar[dict] = load_model_prices_and_context_window()
    _model_ids: ClassVar[dict] = {
        "azure-gpt-4o-mini": "azure/gpt-4o-mini",
        "azure-gpt-4o": "azure/gpt-4o",

    }

    @staticmethod
    def compute_token_cost(model_endpoint_id: str, prompt_tokens: int, completion_tokens: int) -> float:

        model_id = LLMTokenCost._model_ids.get(model_endpoint_id, model_endpoint_id)
        if model_id is None:
            error = f"Model {model_endpoint_id} not found"
            logger.error(error)
            raise ValueError(error)

        model_prices = LLMTokenCost._model_prices.get(model_id, None)
        if model_prices is None:
            error = f"Model {model_id} not found"
            logger.error(error)
            raise ValueError(error)

        input_cost_per_token = model_prices.get("input_cost_per_token", None)
        if input_cost_per_token is None:
            error = f"Input cost per token not found for model {model_id}"
            logger.error(error)
            raise ValueError(error)

        output_cost_per_token = model_prices.get("output_cost_per_token", None)
        if output_cost_per_token is None:
            error = f"Output cost per token not found for model {model_id}"
            logger.error(error)
            raise ValueError(error)

        input_cost = input_cost_per_token * prompt_tokens
        output_cost = output_cost_per_token * completion_tokens

        return input_cost + output_cost
