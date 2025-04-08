"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from enum import Enum
from pathlib import Path
from typing import ClassVar

import yaml
from pydantic import BaseModel, SecretStr


class ModelType(Enum):
    LLM = "LLM"

class ModelSize(Enum):
    SMALL = "Small" # max 3B - 1M input token 10c
    MEDIUM = "Medium" # max 15B - 1M input token 50c
    LARGE = "Large" # max 90B - 1M input token 300c
    EXTRA_LARGE = "Extra Large" # 90B+ - 1M input token +300c

class ModelEndpoint(BaseModel):
    endpoint_id: str
    provider: str
    # model_name: str  # noqa: ERA001

    # description: str # noqa: ERA001
    # model_type: ModelType # noqa: ERA001
    # size: ModelSize # noqa: ERA001
    # token_per_minute_limit: int # noqa: ERA001
    # request_per_minute_limit: int # noqa: ERA001

    # model endpoint config
    api_key: SecretStr | None = None
    endpoint_url: SecretStr | None = None
    api_version: str | None = None
    deployment_name: str | None = None


# Compute the project root and set the default file path for model_endpoints.yml.
DEFAULT_MODEL_ENDPOINTS_PATH = Path(__file__).resolve().parents[2] / "model_endpoints.yml"

class ModelEndpoints:
    _default_endpoint_id: str | None = None
    _default_architect_endpoint_id: str | None = None
    _lite_llm: dict[str, str] = {"use": False, "use_proxy": False}
    _endpoints: ClassVar[list[ModelEndpoint]] = []

    @staticmethod
    def get_default_model_endpoint_id() -> str:
        if ModelEndpoints._default_endpoint_id is None:
            ModelEndpoints.load_model_endpoints()
        return ModelEndpoints._default_endpoint_id
    
    @staticmethod
    def get_default_architect_model_endpoint_id() -> str:
        if ModelEndpoints._default_architect_endpoint_id is None:
            ModelEndpoints.load_model_endpoints()
        if ModelEndpoints._default_architect_endpoint_id is None:
            return ModelEndpoints.get_default_model_endpoint_id()
        return ModelEndpoints._default_architect_endpoint_id
    
    @staticmethod
    def use_lite_llm() -> bool:
        return ModelEndpoints._lite_llm["use"]
    
    @staticmethod
    def use_lite_llm_proxy() -> bool:
        return ModelEndpoints._lite_llm["use_proxy"]

    @staticmethod
    def get_lite_llm_config() -> tuple[str, str] :
        return ModelEndpoints._lite_llm["api_key"], ModelEndpoints._lite_llm["api_base"]

    @staticmethod
    def load_model_endpoints(file_path: str | None = None) -> list[ModelEndpoint]:
        if file_path is None:
            file_path = str(DEFAULT_MODEL_ENDPOINTS_PATH)
        full_path = Path(file_path)
        with full_path.open("r", encoding="utf-8") as stream:
            data = yaml.safe_load(stream)
            
        ModelEndpoints._default_endpoint_id = data.get("default_endpoint_id", None)

        if "default_architect_endpoint_id" in data:
            ModelEndpoints._default_architect_endpoint_id = data.get("default_architect_endpoint_id", None)

        if "lite_llm" in data:
            ModelEndpoints._lite_llm["use"] = data["lite_llm"].get("use", False)
            ModelEndpoints._lite_llm["use_proxy"] = data["lite_llm"].get("use_proxy", False)
            ModelEndpoints._lite_llm["api_key"] = data["lite_llm"].get("api_key", None)
            ModelEndpoints._lite_llm["api_base"] = data["lite_llm"].get("api_base", None)

        if ModelEndpoints._default_endpoint_id is None:
            msg = "No default endpoint id found in model_endpoints.yml file. Check if 'default_endpoint_id' is set."
            raise ValueError(msg)

        endpoints_data = data.get("endpoints", [])
        ModelEndpoints._endpoints = [ModelEndpoint(**endpoint) for endpoint in endpoints_data]
        return ModelEndpoints._endpoints

    @staticmethod
    def get_model_endpoint(model_endpoint_id: str, file_path: str | None = None) -> ModelEndpoint | None:
        if len(ModelEndpoints._endpoints) == 0:
            ModelEndpoints.load_model_endpoints(file_path)
        for endpoint in ModelEndpoints._endpoints:
            if endpoint.endpoint_id == model_endpoint_id:
                return endpoint
        return None

    @staticmethod
    def get_all_model_endpoints(file_path: str | None = None) -> list[ModelEndpoint]:
        if len(ModelEndpoints._endpoints) == 0:
            ModelEndpoints.load_model_endpoints(file_path)
        return ModelEndpoints._endpoints

