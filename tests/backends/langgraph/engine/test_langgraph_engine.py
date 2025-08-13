import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from pydantic import BaseModel
from typing import Any
from ebiose.backends.langgraph.engine.langgraph_engine import LangGraphEngine

class MockNode(BaseModel):
    id: str
    name: str
    type: str
    input_state_model: type[BaseModel] = BaseModel
    output_state_model: type[BaseModel] = BaseModel

from ebiose.core.engines.graph_engine.nodes.llm_node import LLMNode

class MockLLMNode(LLMNode):
    type: str = "LLMNode"
    model_extra: dict = {}
    input_state_model: Any
    output_state_model: Any

class MockGraph(BaseModel):
    nodes: list[MockLLMNode]
    edges: list = []

    def get_outgoing_edges(self, *args, **kwargs):
        return []

    def get_outgoing_nodes(self, *args, **kwargs):
        return []

@pytest.fixture
def langgraph_engine():
    return LangGraphEngine(
        configuration={
            "input_model": {},
            "output_model": {},
            "graph": {
                "nodes": [{"id": "start", "name": "start", "type": "StartNode"}, {"id": "end", "name": "end", "type": "EndNode"}],
                "edges": [{"start_node_id": "start", "end_node_id": "end"}],
                "shared_context_prompt": "test"
            },
        },
        model_endpoint_id="test_endpoint"
    )

@patch("ebiose.backends.langgraph.engine.langgraph_engine.create_pydantic_model_from_schema")
def test_set_llm_models_create_models(mock_create_model, langgraph_engine):
    langgraph_engine.input_model = None
    langgraph_engine.output_model = None
    langgraph_engine._set_llm_models()
    assert mock_create_model.call_count == 2

@patch("ebiose.backends.langgraph.engine.langgraph_engine.Graph.model_validate")
def test_set_llm_models_validate_graph(mock_validate, langgraph_engine):
    langgraph_engine.graph = None
    langgraph_engine._set_llm_models()
    mock_validate.assert_called_once()

def test_set_llm_models_replace_nodes(langgraph_engine):
    langgraph_engine.graph = MockGraph(nodes=[MockLLMNode(id="1", name="llm_node", purpose="", prompt="", input_state_model=BaseModel, output_state_model=BaseModel)])
    langgraph_engine._set_llm_models()
    assert langgraph_engine.graph.nodes[0].__class__.__name__ == "LangGraphLLMNode"

@pytest.mark.asyncio
@patch("ebiose.backends.langgraph.engine.langgraph_engine.LangGraphEngine.invoke_graph", new_callable=AsyncMock)
async def test_run_implementation(mock_invoke_graph, langgraph_engine):
    class InputModel(BaseModel):
        pass
    mock_invoke_graph.return_value = {"output": "success"}
    result = await langgraph_engine._run_implementation(InputModel(), "master_id")
    assert result == "success"

def test_build_state(langgraph_engine):
    langgraph_engine.graph = MockGraph(nodes=[MockLLMNode(id="1", name="llm_node", purpose="", prompt="", input_state_model=BaseModel, output_state_model=BaseModel)])
    langgraph_engine._build_state()
    assert langgraph_engine._state is not None

def test_build_config(langgraph_engine):
    langgraph_engine.graph = MockGraph(nodes=[MockLLMNode(id="1", name="llm_node", purpose="", prompt="", input_state_model=BaseModel, output_state_model=BaseModel)])
    langgraph_engine._build_config()
    assert langgraph_engine._config is not None
