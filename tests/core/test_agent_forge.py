import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from pydantic import BaseModel
from ebiose.core.agent_forge import AgentForge
from ebiose.core.agent import Agent

class ConcreteForge(AgentForge):
    async def compute_fitness(self, agent: Agent, **kwargs: dict[str, any]) -> tuple[str, float]:
        return "test_fitness", 1.0

class InputModel(BaseModel):
    pass

class OutputModel(BaseModel):
    pass

@pytest.fixture
def forge():
    return ConcreteForge(
        name="Test Forge",
        description="A test forge.",
        agent_input_model=InputModel,
        agent_output_model=OutputModel
    )

@patch("ebiose.core.agent_forge.generate_embeddings", return_value=[0.1, 0.2, 0.3])
def test_description_embedding(mock_generate_embeddings, forge):
    embedding = forge.description_embedding
    mock_generate_embeddings.assert_called_once_with("A test forge.")
    assert embedding == [0.1, 0.2, 0.3]
    # Test caching
    embedding2 = forge.description_embedding
    mock_generate_embeddings.assert_called_once()
    assert embedding2 == [0.1, 0.2, 0.3]

@patch("ebiose.core.agent_forge.ModelEndpoints.get_default_model_endpoint_id", return_value="default_endpoint")
def test_validate_default_model_endpoint_id_none(mock_get_default):
    forge = ConcreteForge(
        name="Test Forge",
        description="A test forge.",
        agent_input_model=InputModel,
        agent_output_model=OutputModel,
        default_model_endpoint_id=None
    )
    assert forge.default_model_endpoint_id == "default_endpoint"

def test_validate_default_model_endpoint_id_provided():
    forge = ConcreteForge(
        name="Test Forge",
        description="A test forge.",
        agent_input_model=InputModel,
        agent_output_model=OutputModel,
        default_model_endpoint_id="provided_endpoint"
    )
    assert forge.default_model_endpoint_id == "provided_endpoint"

@pytest.mark.asyncio
@patch("ebiose.core.agent_forge.ForgeCycle")
async def test_run_new_cycle(mock_forge_cycle, forge):
    mock_cycle_instance = MagicMock()
    mock_cycle_instance.execute_a_cycle = AsyncMock(return_value=[])
    mock_forge_cycle.return_value = mock_cycle_instance

    config = MagicMock()
    ecosystem = MagicMock()

    await forge.run_new_cycle(config, ecosystem)

    mock_forge_cycle.assert_called_once_with(forge=forge, config=config)
    mock_cycle_instance.execute_a_cycle.assert_called_once_with(ecosystem)

@patch("ebiose.core.agent_forge.get_ipython", return_value=None)
@patch("ebiose.core.agent_forge.logger")
def test_display_results_no_ipython(mock_logger, mock_get_ipython, forge):
    agent = MagicMock()
    agent.agent_engine.graph.to_mermaid_str.return_value = "mermaid"
    agents = {"agent1": agent}
    agents_fitness = {"agent1": 0.9}

    forge.display_results(agents, agents_fitness)

    mock_logger.info.assert_called()

@patch("ebiose.core.agent_forge.get_ipython", return_value=True)
@patch("ebiose.core.agent_forge.display", create=True)
@patch("ebiose.core.agent_forge.Markdown", create=True)
def test_display_results_with_ipython(mock_markdown, mock_display, mock_get_ipython, forge):
    agent = MagicMock()
    agent.agent_engine.graph.to_mermaid_str.return_value = "mermaid"
    agent.agent_engine.graph.shared_context_prompt = "shared"
    agent.agent_engine.graph.nodes = []
    agents = {"agent1": agent}
    agents_fitness = {"agent1": 0.9}

    forge.display_results(agents, agents_fitness)

    mock_display.assert_called()
    mock_markdown.assert_called()
