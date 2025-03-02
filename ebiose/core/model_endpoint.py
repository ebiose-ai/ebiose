from enum import Enum

from pydantic import BaseModel


class ModelType(Enum):
    LLM = "LLM"

class ModelSize(Enum):
    SMALL = "Small" # max 3B - 1M input token 10c
    MEDIUM = "Medium" # max 15B - 1M input token 50c
    LARGE = "Large" # max 90B - 1M input token 300c
    EXTRA_LARGE = "Extra Large" # 90B+ - 1M input token +300c


class ModelEndpoint(BaseModel):
    endpoint_id: str
    model_name: str
    # description: str # noqa: ERA001
    # model_type: ModelType # noqa: ERA001
    # size: ModelSize # noqa: ERA001
    # token_per_minute_limit: int # noqa: ERA001
    # request_per_minute_limit: int # noqa: ERA001
