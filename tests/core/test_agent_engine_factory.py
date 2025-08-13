import pytest
from unittest.mock import patch, MagicMock
from ebiose.core.agent_engine_factory import AgentEngineFactory
from ebiose.backends.langgraph.engine.langgraph_engine import LangGraphEngine

@patch("ebiose.core.agent_engine_factory.LangGraphEngine")
def test_create_engine_langgraph(mock_langgraph_engine):
    configuration = {"key": "value"}
    engine = AgentEngineFactory.create_engine(
        engine_type="langgraph_engine",
        agent_id="test_agent",
        configuration=configuration,
        model_endpoint_id="test_endpoint"
    )
    mock_langgraph_engine.assert_called_once_with(
        agent_id="test_agent",
        configuration=configuration,
        model_endpoint_id="test_endpoint"
    )
    assert engine == mock_langgraph_engine.return_value

@patch("ebiose.core.agent_engine_factory.ModelEndpoints.get_default_model_endpoint_id", return_value="default_endpoint")
@patch("ebiose.core.agent_engine_factory.LangGraphEngine")
def test_create_engine_langgraph_default_endpoint(mock_langgraph_engine, mock_get_default):
    configuration = {"key": "value"}
    AgentEngineFactory.create_engine(
        engine_type="langgraph_engine",
        agent_id="test_agent",
        configuration=configuration
    )
    mock_langgraph_engine.assert_called_once_with(
        agent_id="test_agent",
        configuration=configuration,
        model_endpoint_id="default_endpoint"
    )

def test_create_engine_unknown_type():
    with pytest.raises(ValueError, match="Unknown engine type: unknown_engine"):
        AgentEngineFactory.create_engine(
            engine_type="unknown_engine",
            agent_id="test_agent",
            configuration={}
        )
