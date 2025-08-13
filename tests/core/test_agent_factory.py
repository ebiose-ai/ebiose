import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from pydantic import BaseModel

from ebiose.core.agent_factory import AgentFactory
from ebiose.cloud_client.client import AgentOutputModel, AgentEngineOutputModel

class MockAgent:
    def __init__(self, **kwargs):
        self.id = "mock_agent_id"
        for k, v in kwargs.items():
            setattr(self, k, v)

@pytest.fixture
def mock_agent():
    return MockAgent()

@patch("ebiose.core.agent.Agent.model_validate")
@patch("ebiose.core.agent_engine_factory.AgentEngineFactory.create_engine")
def test_load_agent(mock_create_engine, mock_model_validate):
    agent_config = {
        "id": "agent123",
        "agent_engine": {
            "engine_type": "langgraph_engine",
            "configuration": json.dumps({"key": "value"})
        }
    }

    AgentFactory.load_agent(agent_config, "test_endpoint")

    mock_create_engine.assert_called_once_with(
        engine_type="langgraph_engine",
        configuration={"key": "value"},
        agent_id="agent123",
        model_endpoint_id="test_endpoint"
    )

    expected_config = agent_config.copy()
    expected_config["agent_engine"] = mock_create_engine.return_value
    expected_config["architect_agent"] = None
    expected_config["genetic_operator_agent"] = None

    mock_model_validate.assert_called_once_with(expected_config)

@patch("ebiose.core.agent.Agent")
@patch("ebiose.core.agent_engine_factory.AgentEngineFactory.create_engine")
def test_load_agent_from_api(mock_create_engine, mock_agent_class):
    response_dict = AgentOutputModel(
        uuid="agent123",
        name="test architect agent",
        description="A test agent",
        architectAgentUuid=None,
        geneticOperatorAgentUuid=None,
        parentAgentUuids=[],
        agentEngine=AgentEngineOutputModel(
            engineType="langgraph_engine",
            configuration=json.dumps({"key": "value"})
        ),
        computeBankInDollars=0.0,
        agentType=2
    )

    AgentFactory.load_agent_from_api(response_dict, "test_endpoint")

    mock_create_engine.assert_called_once_with(
        engine_type="langgraph_engine",
        configuration={"key": "value"},
        model_endpoint_id="test_endpoint",
        agent_id="agent123"
    )

    mock_agent_class.assert_called_once_with(
        id="agent123",
        name="test architect agent",
        agent_type="architect",
        description="A test agent",
        architect_agent_id=None,
        genetic_operator_agent_id=None,
        agent_engine=mock_create_engine.return_value,
        parent_ids=[]
    )

class MockOutput(BaseModel):
    description: str = "mock description"

    def model_dump(self):
        return {"description": self.description}

@pytest.mark.asyncio
@patch("ebiose.core.agent.Agent", new=MockAgent)
@patch("ebiose.core.agent_engine_factory.AgentEngineFactory.create_engine")
async def test_generate_agent(mock_create_engine):
    architect_agent = MockAgent()
    architect_agent.run = AsyncMock(return_value=MockOutput())

    class Input(BaseModel):
        pass

    class Output(BaseModel):
        pass

    await AgentFactory.generate_agent(
        architect_agent=architect_agent,
        agent_input={},
        generated_agent_engine_type="test_engine",
        generated_agent_input=Input,
        generated_agent_output=Output,
        generated_model_endpoint_id="test_endpoint",
        forge_cycle_id="cycle123",
        forge_description="test_forge"
    )

    architect_agent.run.assert_called_once_with({}, master_agent_id="mock_agent_id", forge_cycle_id="cycle123")

@pytest.mark.asyncio
@patch("ebiose.core.agent.Agent", new=MockAgent)
@patch("ebiose.core.agent_engine_factory.AgentEngineFactory.create_engine")
async def test_crossover_agents(mock_create_engine):
    crossover_agent = MockAgent()
    crossover_agent.run = AsyncMock(return_value=MockOutput())

    class Input(BaseModel):
        pass

    class Output(BaseModel):
        pass

    await AgentFactory.crossover_agents(
        crossover_agent=crossover_agent,
        input_data=Input(),
        generated_agent_engine_type="test_engine",
        generated_agent_input=Input,
        generated_agent_output=Output,
        generated_model_endpoint_id="test_endpoint",
        master_agent_id="master123",
        forge_cycle_id="cycle123",
        forge_description="test_forge"
    )

    crossover_agent.run.assert_called_once_with(Input(), master_agent_id="master123", forge_cycle_id="cycle123")
