"""Copyright (c) 2024, Inria.

Pre-release Version - DO NOT DISTRIBUTE
This software is licensed under the MIT License. See LICENSE for details.
"""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator

from ebiose.core.agent_engine import AgentEngine
from ebiose.core.engines.graph_engine.graph import Graph
from ebiose.core.engines.graph_engine.utils import json_schema_to_pydantic


class GraphEngine(AgentEngine):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    engine_type: str = "graph_engine"
    input_model: type[BaseModel] | None = Field(None, serialization_exclude=True)
    output_model: type[BaseModel] | None = Field(None, serialization_exclude=True)
    model_endpoint_id: str = "azure-gpt-4o-mini"
    graph: Graph | None = Field(None, serialization_exclude=True)

    @model_validator(mode="after")
    def _load_configuration(self) -> Self:
        # instantiate graph
        self.graph = Graph.model_validate(self.configuration["graph"])

        # instantiate input_model and output_model
        if self.input_model is None:
            self.input_model = self._validate_input_output_models("InputModel", self.configuration["input_model"])
        if self.output_model is None:
            self.output_model = self._validate_input_output_models("OutputModel", self.configuration["output_model"])
        return self

    @model_serializer
    def _serialize_configuration(self) -> dict[str, any]:
        self.configuration = {
            "engine_type": self.engine_type,
            "graph": self.graph.model_dump(),
            "input_model": self.input_model.model_json_schema(),
            "output_model": self.output_model.model_json_schema(),
            "model_endpoint_id": self.model_endpoint_id,
        }
        return self.configuration

    def _validate_input_output_models(self, model_name: str, io_model: dict | type[BaseModel]) -> type[BaseModel]:
        # validate input_model and output_model
        if isinstance(io_model, dict):
            return json_schema_to_pydantic(io_model, model_name)
        if issubclass(io_model, BaseModel):
            return io_model

        msg = "input_model and output_model must either be a BaseModel or a Dict"
        raise ValueError(msg)


    def _serialize_input_output_models(self, io_model: type[BaseModel]) -> dict[str, any]:
        io_model_dict = {"name": io_model.__name__, "fields": {}}
        for field_name, field in io_model.model_fields.items():
            io_model_dict["fields"][field_name] = (field.annotation.__name__, {"description": field.description})
        return io_model_dict
