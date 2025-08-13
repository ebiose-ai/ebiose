import pytest
import json
from unittest.mock import patch, MagicMock
from pydantic import BaseModel, Field
from ebiose.core.engines.graph_engine.graph_engine import GraphEngine


class TestInputModel(BaseModel):
    a: int = Field(description="An integer")

class TestOutputModel(BaseModel):
    b: str = Field(description="A string")

class ConcreteGraphEngine(GraphEngine):
    async def _run_implementation(self, *args, **kwargs):
        pass

from ebiose.core.engines.graph_engine.graph import Graph

@pytest.fixture
def graph_engine():
    nodes = [
        {"id": "start", "name": "start", "type": "StartNode"},
        {"id": "end", "name": "end", "type": "EndNode"},
    ]
    edges = [
        {"start_node_id": "start", "end_node_id": "end"}
    ]
    graph = Graph(nodes=nodes, edges=edges, shared_context_prompt="test")

    return ConcreteGraphEngine(
        input_model=TestInputModel,
        output_model=TestOutputModel,
        graph=graph,
        model_endpoint_id="test_endpoint",
        agent_id="test_agent"
    )

def test_serialize_configuration(graph_engine):
    config_str = graph_engine.serialize_configuration()
    config = json.loads(config_str)

    assert "input_model" in config
    assert "output_model" in config
    assert "graph" in config
    assert config["model_endpoint_id"] == "test_endpoint"
    assert config["agent_id"] == "test_agent"

@patch("ebiose.core.engines.graph_engine.graph_engine.create_pydantic_model_from_schema")
def test_validate_input_output_models_dict(mock_create_model, graph_engine):
    schema = {"type": "object", "properties": {}}
    graph_engine._validate_input_output_models("TestModel", schema)
    mock_create_model.assert_called_once_with(schema=schema, model_name="TestModel")

def test_validate_input_output_models_model(graph_engine):
    model = graph_engine._validate_input_output_models("TestModel", TestInputModel)
    assert model == TestInputModel

def test_validate_input_output_models_invalid(graph_engine):
    with pytest.raises(TypeError):
        graph_engine._validate_input_output_models("TestModel", "invalid")

def test_serialize_input_output_models(graph_engine):
    serialized = graph_engine._serialize_input_output_models(TestInputModel)
    assert serialized["name"] == "TestInputModel"
    assert "a" in serialized["fields"]
    assert serialized["fields"]["a"] == ("int", {"description": "An integer"})
