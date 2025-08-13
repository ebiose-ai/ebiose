import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from pydantic import BaseModel
from ebiose.core.agent import Agent
from ebiose.core.agent_engine import AgentEngine

from typing import Type

class MockAgentEngine(AgentEngine):
    engine_type: str = "mock"
    input_model: Type[BaseModel] | None = None
    output_model: Type[BaseModel] | None = None

    async def _run_implementation(self, agent_input: BaseModel, master_agent_id: str, forge_cycle_id: str | None = None, **kwargs: dict[str, any]) -> any:
        return "mocked run"

@pytest.fixture
def mock_agent_engine():
    return MockAgentEngine(agent_id="mock_agent")

@pytest.fixture
def agent_data(mock_agent_engine):
    return {
        "name": "Test Agent",
        "description": "A test agent.",
        "agent_engine": mock_agent_engine
    }

def test_agent_initialization(agent_data):
    agent = Agent(**agent_data)
    assert agent.name == "Test Agent"
    assert agent.description == "A test agent."
    assert isinstance(agent.agent_engine, AgentEngine)
    assert agent.id.startswith("agent-")

@patch("ebiose.core.agent.generate_embeddings", return_value=[0.1, 0.2, 0.3])
def test_generate_embeddings(mock_generate_embeddings, agent_data):
    agent = Agent(**agent_data)
    mock_generate_embeddings.assert_called_once_with("A test agent.")
    assert agent.description_embedding == [0.1, 0.2, 0.3]

@pytest.mark.asyncio
@patch("ebiose.core.agent.AgentEngine.run", new_callable=AsyncMock)
async def test_agent_run(mock_run, agent_data, mock_agent_engine):
    mock_run.return_value = "mocked run"
    agent = Agent(**agent_data)
    agent.agent_engine = mock_agent_engine

    class InputModel(BaseModel):
        data: str

    input_data = InputModel(data="test")
    result = await agent.run(input_data, "master_id", "cycle_id")

    mock_run.assert_called_once_with(input_data, "master_id", "cycle_id")
    assert result == "mocked run"

def test_update_io_models(agent_data):
    agent = Agent(**agent_data)

    class InputModel(BaseModel):
        pass

    class OutputModel(BaseModel):
        pass

    agent.update_io_models(agent_input_model=InputModel, agent_output_model=OutputModel)

    assert agent.agent_engine.input_model == InputModel
    assert agent.agent_engine.output_model == OutputModel

@patch("ebiose.core.agent.AgentEngineFactory.create_engine")
def test_validate_agent_engine_from_dict(mock_create_engine):
    engine_data = {
        "engine_type": "some_engine",
        "configuration": {"key": "value"},
        "agent_id": "agent-123"
    }
    Agent.validate_agent_engine(engine_data)
    mock_create_engine.assert_called_once_with(
        engine_type="some_engine",
        configuration={"key": "value"},
        agent_id="agent-123"
    )

def test_validate_agent_engine_with_instance(mock_agent_engine):
    engine = Agent.validate_agent_engine(mock_agent_engine)
    assert engine == mock_agent_engine

def test_validate_agent_engine_with_invalid_type():
    with pytest.raises(TypeError, match="Invalid agent engine type"):
        Agent.validate_agent_engine("not an engine")
