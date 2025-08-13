import pytest
from unittest.mock import patch, MagicMock
from pydantic import BaseModel
from ebiose.core.ecosystem import Ecosystem
from ebiose.core.agent import Agent
from ebiose.core.agent_forge import AgentForge

class MockAgent(Agent):
    id: str
    name: str
    description_embedding: list[float]

class MockForge(AgentForge):
    id: str
    description_embedding: list[float]

    async def compute_fitness(self, agent: Agent, **kwargs: dict[str, any]) -> tuple[str, float]:
        return "test_fitness", 1.0

@pytest.fixture
def mock_agents():
    return {
        "agent1": MockAgent(id="agent1", name="agent1", description_embedding=[1, 0, 0]),
        "agent2": MockAgent(id="agent2", name="agent2", description_embedding=[0, 1, 0]),
        "agent3": MockAgent(id="agent3", name="agent3", description_embedding=[0, 0, 1]),
    }

@pytest.fixture
def ecosystem(mock_agents):
    Ecosystem.forge_list = []
    Ecosystem.agent_forge_distances = {}
    return Ecosystem(agents=mock_agents)

@patch("ebiose.core.ecosystem.ModelEndpoints.get_default_model_endpoint_id", return_value="default_endpoint")
@patch("ebiose.core.ecosystem.GraphUtils.get_architect_agent", return_value=MockAgent(id="arch", name="arch", description_embedding=[]))
@patch("ebiose.core.ecosystem.GraphUtils.get_crossover_agent", return_value=MockAgent(id="cross", name="cross", description_embedding=[]))
@patch("ebiose.core.ecosystem.GraphUtils.get_mutation_agent", return_value=MockAgent(id="mut", name="mut", description_embedding=[]))
def test_new_ecosystem(mock_mutation, mock_crossover, mock_architect, mock_get_default):
    eco = Ecosystem.new(initial_agents={})
    mock_architect.assert_called_once_with("default_endpoint")
    mock_crossover.assert_called_once_with("default_endpoint")
    mock_mutation.assert_called_once_with("default_endpoint")
    assert len(eco.initial_architect_agents) == 1
    assert len(eco.initial_genetic_operator_agents) == 2

def test_get_agent(ecosystem):
    agent = ecosystem.get_agent("agent1")
    assert agent.id == "agent1"
    assert ecosystem.get_agent("non_existent_agent") is None

@patch("ebiose.core.ecosystem.embedding_distance", side_effect=lambda x, y: sum(abs(a-b) for a, b in zip(x,y)))
def test_add_forge(mock_embedding_distance, ecosystem):
    forge = MockForge(
        id="forge1",
        name="forge1",
        description="a forge",
        agent_input_model=BaseModel,
        agent_output_model=BaseModel,
        description_embedding=[1, 1, 1]
    )
    ecosystem.add_forge(forge)

    assert forge in ecosystem.forge_list
    assert forge.id in ecosystem.agent_forge_distances
    assert len(ecosystem.agent_forge_distances[forge.id]) == 3

@pytest.mark.asyncio
@patch("ebiose.core.ecosystem.embedding_distance")
async def test_select_agents_for_forge(mock_embedding_distance, ecosystem):
    mock_embedding_distance.side_effect = [3, 2, 1]
    forge = MockForge(
        id="forge1",
        name="forge1",
        description="a forge",
        agent_input_model=BaseModel,
        agent_output_model=BaseModel,
        description_embedding=[0.1, 0.2, 0.7]
    )

    selected_agents = await ecosystem.select_agents_for_forge(forge, 2)

    assert len(selected_agents) == 2
    assert selected_agents[0].id == "agent3"
    assert selected_agents[1].id == "agent2"

@patch("ebiose.core.ecosystem.embedding_distance")
def test_add_new_born_agent(mock_embedding_distance, ecosystem):
    mock_embedding_distance.side_effect = [3, 2, 1, 0.5]
    new_agent = MockAgent(id="agent4", name="agent4", description_embedding=[0.5, 0.5, 0.5])

    forge = MockForge(
        id="forge1",
        name="forge1",
        description="a forge",
        agent_input_model=BaseModel,
        agent_output_model=BaseModel,
        description_embedding=[1, 1, 1]
    )
    ecosystem.add_forge(forge)

    ecosystem._add_new_born_agent(new_agent)

    assert "agent4" in ecosystem.agents
    assert len(ecosystem.agent_forge_distances[forge.id]) == 4
