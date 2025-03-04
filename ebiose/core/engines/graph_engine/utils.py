
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, create_model

from ebiose.backends.langgraph.engine.base_agents.architect_agent import (
    init_architect_agent,
)
from ebiose.backends.langgraph.engine.base_agents.crossover_agent import (
    init_crossover_agent,
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
    _routing_agent: BaseModel | None = None
    _structured_output_agent_registry: dict[str, BaseModel] = {}

    @classmethod
    def get_routing_agent(cls, model_endpoint_id: str | None) -> BaseModel:
        if cls._routing_agent is None:
            if model_endpoint_id is None:
                model_endpoint_id = ModelEndpoints.get_default_model_endpoint()
            cls._routing_agent = init_routing_agent(model_endpoint_id)
        return cls._routing_agent

    @classmethod
    def get_structured_output_agent(cls, output_model: type[BaseModel], model_endpoint_id: str | None) -> BaseModel:
        # TODO(xabier): find a way to handle multiple structured output agents
        output_model_id = id(output_model)
        if output_model_id not in cls._structured_output_agent_registry:
            if model_endpoint_id is None:
                model_endpoint_id = ModelEndpoints.get_default_model_endpoint()
            logger.debug(f"\nInitializing structured output agent for model {output_model.__name__} ({len(cls._structured_output_agent_registry)+1})")
            cls._structured_output_agent_registry[id(output_model)] = init_structured_output_agent(output_model, model_endpoint_id)
        return cls._structured_output_agent_registry[output_model_id]

    @classmethod
    def get_architect_agent(cls, model_endpoint_id: str | None) -> BaseModel:
        if cls._architect_agent is None:
            if model_endpoint_id is None:
                model_endpoint_id = ModelEndpoints.get_default_model_endpoint()
            cls._architect_agent = init_architect_agent(model_endpoint_id)
        return cls._architect_agent

    @classmethod
    def get_crossover_agent(cls, model_endpoint_id: str | None) -> BaseModel:
        if cls._crossover_agent is None:
            if model_endpoint_id is None:
                model_endpoint_id = ModelEndpoints.get_default_model_endpoint()
            cls._crossover_agent = init_crossover_agent(model_endpoint_id)
        return cls._crossover_agent




def find_placeholders(text: str) -> list[str]:
    """Find placeholders like {math_problem} in prompts and return them with {}."""
    pattern = r"\{([^{}]+)\}"
    return re.findall(pattern, text)

def json_schema_to_pydantic(
    schema: dict[str, any],
    class_name: str = "GeneratedModel",
    root_schema: dict[str, any]| None = None,
) -> type[BaseModel]:
    """Convert a JSON schema to a Pydantic model with support for $ref and $defs.

    Args:
        schema (Dict[str, Any]): JSON schema dictionary
        class_name (str, optional): Name of the generated Pydantic model. Defaults to 'GeneratedModel'.
        root_schema (Dict[str, Any], optional): Root schema for resolving references. Defaults to None.

    Returns:
        Type[BaseModel]: Dynamically created Pydantic model
    """
    # Use the provided schema as root_schema if not specified
    root_schema = root_schema or schema

    def resolve_ref(ref: str) -> dict[str, any]:
        """Resolve JSON schema references.

        Supports:
        - Local references like '#/definitions/SomeDefinition'
        - Relative references like '#/defs/SomeDefinition'
        """
        # Remove leading '#/' if present
        ref = ref.removeprefix("#/")

        # Split the reference path
        parts = ref.split("/")

        # Navigate through the schema to find the referenced definition
        current = root_schema
        for part in parts:
            if part not in current:
                msg = f"Reference '{ref}' not found in schema"
                raise ValueError(msg)
            current = current[part]

        return current

    def convert_type(type_def: str | list[str] | dict[str, any]) -> type:
        """Convert JSON schema type to Python type."""
        # Handle $ref first
        if isinstance(type_def, dict) and "$ref" in type_def:
            # Resolve the reference and convert to a type
            ref_schema = resolve_ref(type_def["$ref"])
            return convert_type(ref_schema)

        # Handle multiple types
        if isinstance(type_def, list):
            # If multiple types, use Optional
            converted_types = [convert_type(t) for t in type_def]
            return tuple(converted_types) | None

        # Handle dictionary type definitions
        if isinstance(type_def, dict):
            if "type" in type_def:
                type_def = type_def["type"]
            else:
                # If no type specified, default to Any
                return any

        # Normalize type string
        type_def = type_def.lower() if isinstance(type_def, str) else type_def

        # Type mapping
        type_map = {
            "string": str,
            "number": float,
            "integer": int,
            "boolean": bool,
            "array": list[any],
            "object": dict[str, any],
        }

        return type_map.get(type_def, any)

    def process_field(prop_name: str, prop_def: dict[str, any]) -> tuple:
        """Process a single field for create_model."""
        # Handle $ref first
        if "$ref" in prop_def:
            # Resolve the reference
            prop_def = resolve_ref(prop_def["$ref"])

        # Determine field type
        field_type = convert_type(prop_def)

        # Handle optional fields
        required = schema.get("required", [])
        is_optional = prop_name not in required

        # Add default value if specified
        default = prop_def.get("default", ... if is_optional else None)

        # Create field with description and other metadata
        field_kwargs = {}
        if "description" in prop_def:
            field_kwargs["description"] = prop_def["description"]

        # Handle nested objects
        if prop_def.get("type") == "object" and "properties" in prop_def:
            # Recursively create nested Pydantic model
            nested_model = json_schema_to_pydantic(
                prop_def,
                class_name=f"{class_name}{prop_name.capitalize()}",
                root_schema=root_schema,
            )
            field_type = nested_model

        # Handle arrays with specific item types
        if prop_def.get("type") == "array" and "items" in prop_def:
            items = prop_def["items"]
            item_type = convert_type(items)
            field_type = list[item_type]

        # Handle enums
        if "enum" in prop_def:
            field_type = str  # Use string type with validation
            field_kwargs["pattern"] = f"^({'|'.join(map(str, prop_def['enum']))})$"

        # Create field with optional default and metadata
        return (field_type, Field(default, **field_kwargs))

    # Prepare fields for create_model
    model_fields = {}

    # Handle $defs or definitions
    defs = schema.get("$defs", schema.get("definitions", {}))
    if defs:
        # Preprocess definitions to create named models
        for def_name, def_schema in defs.items():
            json_schema_to_pydantic(
                def_schema,
                class_name=f"{def_name.capitalize()}Model",
                root_schema=root_schema,
            )

    # Process properties
    if "properties" in schema:
        for prop_name, prop_def in schema["properties"].items():
            model_fields[prop_name] = process_field(prop_name, prop_def)

    # Create model with additional configuration
    return create_model(
        class_name,
        __config__=ConfigDict(extra="allow", arbitrary_types_allowed=True),
        __doc__=schema.get("description"),
        **model_fields,
    )
