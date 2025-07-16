"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

import hashlib
import re
from typing import TYPE_CHECKING, ClassVar, get_type_hints

from loguru import logger
from pydantic import BaseModel

from ebiose.backends.langgraph.engine.base_agents.architect_agent import (
    init_architect_agent,
)
from ebiose.backends.langgraph.engine.base_agents.crossover_agent import (
    init_crossover_agent,
)
from ebiose.backends.langgraph.engine.base_agents.mutation_agent import (
    init_mutation_agent,
)
from ebiose.backends.langgraph.engine.base_agents.routing_agent import (
    init_routing_agent,
)
from ebiose.backends.langgraph.engine.base_agents.structured_output_agent import (
    init_structured_output_agent,
)
from ebiose.core.model_endpoint import ModelEndpoints

if TYPE_CHECKING:
    from pydantic import BaseModel


class GraphUtils:
    _architect_agent: BaseModel | None = None
    _crossover_agent: BaseModel | None = None
    _mutation_agent: BaseModel | None = None
    _routing_agent: BaseModel | None = None
    _structured_output_agent_registry: ClassVar[dict[str, BaseModel]] = {}

    @classmethod
    def get_routing_agent(cls) -> BaseModel:
        model_endpoint_id = ModelEndpoints.get_default_utility_agent_endpoint_id()
        if cls._routing_agent is None:
            cls._routing_agent = init_routing_agent(model_endpoint_id)
        return cls._routing_agent

    @staticmethod
    def _get_model_hash(model: type[BaseModel]) -> str:
        """Generate a unique hash for a Pydantic model based on its fields and types."""
        fields = get_type_hints(model)
        fields_str = ",".join(
            f"{name}:{field_type!s}" for name, field_type in sorted(fields.items())
        )
        return hashlib.sha256(fields_str.encode()).hexdigest()

    @classmethod
    def get_structured_output_agent(
        cls,
        output_model: type[BaseModel],
    ) -> BaseModel:
        # TODO(xabier): find a way to handle multiple structured output agents
        model_endpoint_id = ModelEndpoints.get_default_utility_agent_endpoint_id()
        model_hash = cls._get_model_hash(output_model)
        if model_hash not in cls._structured_output_agent_registry:
            logger.debug(
                f"\nInitializing structured output agent for model {output_model.__name__} ({len(cls._structured_output_agent_registry) + 1})",
            )
            cls._structured_output_agent_registry[model_hash] = (
                init_structured_output_agent(output_model, model_endpoint_id)
            )
        return cls._structured_output_agent_registry[model_hash]

    @classmethod
    def get_architect_agent(cls, model_endpoint_id: str | None = None) -> BaseModel:
        if cls._architect_agent is None:
            cls._architect_agent = init_architect_agent(model_endpoint_id)
        return cls._architect_agent

    @classmethod
    def get_crossover_agent(cls, model_endpoint_id: str | None = None) -> BaseModel:
        if cls._crossover_agent is None:
            cls._crossover_agent = init_crossover_agent(model_endpoint_id)
        return cls._crossover_agent

    @classmethod
    def get_mutation_agent(cls, model_endpoint_id: str | None = None) -> BaseModel:
        if cls._mutation_agent is None:
            cls._mutation_agent = init_mutation_agent(model_endpoint_id)
        return cls._mutation_agent


def get_placeholders(text: str) -> list[str]:
    """Find placeholders like {math_problem} in prompts and return them with {}."""
    pattern = r"\{([^{}]+)\}"
    return re.findall(pattern, text)
