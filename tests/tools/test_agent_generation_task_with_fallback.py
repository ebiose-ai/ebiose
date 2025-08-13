import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from pydantic import BaseModel, ConfigDict
from ebiose.tools.agent_generation_task_with_fallback import (
    architect_agent_task,
    crossover_agent_task,
)

from pydantic import ConfigDict

class MockAgent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str
    agent_engine: MagicMock = MagicMock()

class MockForge(BaseModel):
    default_generated_agent_engine_type: str = "test_engine"
    default_model_endpoint_id: str = "test_endpoint"
    agent_input_model: type[BaseModel] = BaseModel
    agent_output_model: type[BaseModel] = BaseModel
    description: str = "test_forge"
    name: str = "test_forge"

class InputModel(BaseModel):
    pass

@pytest.mark.asyncio
@patch("ebiose.tools.agent_generation_task_with_fallback.AgentFactory.generate_agent", new_callable=AsyncMock)
async def test_architect_agent_task(mock_generate_agent):
    forge = MockForge()
    architect_agent = MockAgent(id="architect")
    genetic_operator_agent = MockAgent(id="genetic_operator")

    await architect_agent_task(forge, architect_agent, InputModel(), genetic_operator_agent)

    mock_generate_agent.assert_called_once()

@pytest.mark.asyncio
@patch("ebiose.tools.agent_generation_task_with_fallback.AgentFactory.generate_agent", new_callable=AsyncMock)
async def test_architect_agent_task_fallback(mock_generate_agent):
    mock_generate_agent.side_effect = [Exception("fail"), "success"]
    forge = MockForge()
    architect_agent = MockAgent(id="architect")
    genetic_operator_agent = MockAgent(id="genetic_operator")

    await architect_agent_task(forge, architect_agent, InputModel(), genetic_operator_agent)

    assert mock_generate_agent.call_count == 2

@pytest.mark.asyncio
@patch("ebiose.tools.agent_generation_task_with_fallback.AgentFactory.crossover_agents", new_callable=AsyncMock)
async def test_crossover_agent_task(mock_crossover_agents):
    forge = MockForge()
    genetic_operator_agent = MockAgent(id="genetic_operator")
    parent1 = MockAgent(id="parent1")

    await crossover_agent_task(forge, genetic_operator_agent, InputModel(), None, parent1, None)

    mock_crossover_agents.assert_called_once()

@pytest.mark.asyncio
@patch("ebiose.tools.agent_generation_task_with_fallback.AgentFactory.crossover_agents", new_callable=AsyncMock)
@patch("ebiose.tools.agent_generation_task_with_fallback.AgentFactory.generate_agent", new_callable=AsyncMock)
async def test_crossover_agent_task_fallback(mock_generate_agent, mock_crossover_agents):
    mock_crossover_agents.side_effect = Exception("fail")
    forge = MockForge()
    architect_agent = MockAgent(id="architect")
    genetic_operator_agent = MockAgent(id="genetic_operator")
    parent1 = MockAgent(id="parent1")

    await crossover_agent_task(forge, genetic_operator_agent, InputModel(), architect_agent, parent1, None)

    mock_generate_agent.assert_called_once()
