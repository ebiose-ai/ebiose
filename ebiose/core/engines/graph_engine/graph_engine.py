"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    model_serializer,
    model_validator,
)

from ebiose.core.agent_engine import AgentEngine
from ebiose.core.engines.graph_engine.graph import Graph
from ebiose.tools.json_schema_to_pydantic import create_pydantic_model_from_schema


class GraphEngine(AgentEngine):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    engine_type: str = "graph_engine"
    input_model: type[BaseModel] | None = Field(None)
    output_model: type[BaseModel] | None = Field(None)
    model_endpoint_id: str | None = None
    graph: Graph | None = Field(None)

    @model_serializer
    def _serialize_graph_engine(self) -> dict:
        return {
            "engine_type": self.engine_type,
            "model_endpoint_id": self.model_endpoint_id,
            "agent_id": self.agent_id,
            "configuration": self._serialize_configuration(),
        }

    def _serialize_configuration(self) -> dict:
        return {
            "input_model": self.input_model.model_json_schema() if self.input_model is not None else {},
            "output_model": self.output_model.model_json_schema() if self.output_model is not None else {},
            "graph": self.graph.model_dump() if self.graph is not None else {},
        }

    def _validate_input_output_models(self, model_name: str, io_model: dict | type[BaseModel]) -> type[BaseModel]:
        # validate input_model and output_model
        if isinstance(io_model, dict):
            return create_pydantic_model_from_schema(schema=io_model, model_name=model_name)
        if issubclass(io_model, BaseModel):
            return io_model

        msg = "input_model and output_model must either be a BaseModel or a Dict"
        raise ValueError(msg)


    def _serialize_input_output_models(self, io_model: type[BaseModel]) -> dict[str, any]:
        io_model_dict = {"name": io_model.__name__, "fields": {}}
        for field_name, field in io_model.model_fields.items():
            io_model_dict["fields"][field_name] = (field.annotation.__name__, {"description": field.description})
        return io_model_dict
