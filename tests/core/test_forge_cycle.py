import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from ebiose.core.forge_cycle import ForgeCycle, LocalForgeCycleConfig
from ebiose.core.agent_forge import AgentForge
from pydantic import BaseModel, ConfigDict, Field
from ebiose.core.agent import Agent
from ebiose.core.engines.graph_engine.graph_engine import GraphEngine
from ebiose.core.engines.graph_engine.graph import Graph
from ebiose.core.engines.graph_engine.nodes.node import StartNode, EndNode
from ebiose.core.engines.graph_engine.edge import Edge
from ebiose.core.ecosystem import Ecosystem
import random
import json
import uuid


# --- Basic Models ---
class InputModel(BaseModel):
    forge_description: str = ""

class OutputModel(BaseModel):
    output: str

# --- Mock Pydantic Models for Testing ---
class MockForge(AgentForge):
    model_config = ConfigDict(extra='allow', arbitrary_types_allowed=True)
    name: str = "test_forge"
    description: str = "a test forge"
    agent_input_model: type[BaseModel] = InputModel
    agent_output_model: type[BaseModel] = OutputModel

    async def compute_fitness(self, agent, **kwargs):
        return agent.id, random.random()

class MockStartNode(StartNode):
    id: str = "start"

class MockEndNode(EndNode):
    id: str = "end"

class MockEdge(Edge):
    start_node_id: str = "start"
    end_node_id: str = "end"

class MockGraph(Graph):
    nodes: list = Field(default_factory=lambda: [MockStartNode(), MockEndNode()])
    edges: list = Field(default_factory=lambda: [MockEdge()])
    shared_context_prompt: str = "This is a mock prompt."

class MockGraphEngine(GraphEngine):
    model_config = ConfigDict(extra='allow', arbitrary_types_allowed=True)
    graph: Graph = Field(default_factory=MockGraph)
    input_model: type[BaseModel] = InputModel
    output_model: type[BaseModel] = OutputModel

    async def _run_implementation(self, agent_input: BaseModel, master_agent_id: str, forge_cycle_id: str | None = None, **kwargs: dict[str, any]) -> any:
        return {"output": "mock_output"}

# --- Pytest Fixture ---
@pytest.fixture
def setup_cycle():
    forge = MockForge()
    config = LocalForgeCycleConfig(n_generations=2, n_agents_in_population=4, replacement_ratio=0.5, tournament_size_ratio=0.5)
    cycle = ForgeCycle(forge=forge, config=config)

    mock_engine = MockGraphEngine(engine_type="graph_engine")

    agents = {}
    fitness = {}
    for i in range(4):
        agent_id = f"agent_{i}"
        agent = Agent(id=agent_id, name=f"Agent {i}", description=f"Description {i}", agent_engine=mock_engine, parent_ids=[], architect_agent_id="arch_0", genetic_operator_agent_id="gen_op_0")
        agents[agent_id] = agent
        fitness[agent_id] = (i + 1) * 0.1 # Ensure non-zero fitness

    cycle.agents = agents
    cycle.agents_fitness = fitness

    arch_agent = Agent(id="arch_0", name="Architect Agent", agent_engine=mock_engine, agent_type="architect")
    gen_op_agent = Agent(id="gen_op_0", name="Genetic Operator Agent", agent_engine=mock_engine, agent_type="genetic_operator")

    cycle.architect_agents = {"arch_0": arch_agent}
    cycle.genetic_operator_agents = {"gen_op_0": gen_op_agent}

    ecosystem = Ecosystem(agents={"arch_0": arch_agent, "gen_op_0": gen_op_agent}, initial_architect_agents=[arch_agent], initial_genetic_operator_agents=[gen_op_agent])

    cycle.llm_api = MagicMock()
    cycle.llm_api.get_total_cost.return_value = 0.0
    cycle.llm_api.get_agent_cost.return_value = 0.1

    return cycle, forge, config, ecosystem

# --- Tests ---

def test_forge_cycle_initialization():
    forge = MockForge()
    config = LocalForgeCycleConfig(n_generations=1)
    cycle = ForgeCycle(forge=forge, config=config)
    assert cycle.forge == forge
    assert cycle.config == config
    assert cycle.cur_generation == 0
    assert len(cycle.agents) == 0

@pytest.mark.asyncio
@patch("ebiose.core.forge_cycle.EbioseAPIClient.select_agents", return_value=[])
@patch("ebiose.core.forge_cycle.architect_agent_task", new_callable=AsyncMock)
async def test_initialize_population(mock_architect_task, mock_select_agents, setup_cycle):
    cycle, _, config, ecosystem = setup_cycle
    cycle.agents = {}
    config.n_agents_in_population = 5

    # Use side_effect to return new agent objects with unique IDs
    mock_architect_task.side_effect = [
        Agent(id=f"new_agent_{i}", name=f"New Agent {i}", agent_engine=MockGraphEngine()) for i in range(5)
    ]

    await cycle.initialize_population(ecosystem)

    assert mock_architect_task.call_count == 5
    assert len(cycle.agents) == 5
    assert "new_agent_0" in cycle.agents

@pytest.mark.asyncio
async def test_evaluate_population(setup_cycle):
    cycle, _, _, _ = setup_cycle

    with patch.object(cycle.forge, 'compute_fitness', new_callable=AsyncMock) as mock_compute_fitness:
        mock_compute_fitness.side_effect = [(f"agent_{i}", (i + 1) * 0.1) for i in range(4)]

        total_cost = await cycle._evaluate_population()

        assert mock_compute_fitness.call_count == 4
        assert total_cost == pytest.approx(0.4)
        assert cycle.agents_fitness["agent_0"] == 0.1

def test_tournament_selection(setup_cycle):
    cycle, _, config, _ = setup_cycle
    config.tournament_size_ratio = 0.5

    with patch('random.sample', return_value=[cycle.agents['agent_0'], cycle.agents['agent_1']]):
        with patch('random.choices', return_value=[cycle.agents['agent_1'].id, cycle.agents['agent_3'].id]) as mock_choices:
            selected_ids = cycle.tournament_selection(n_to_select=2)
            assert len(selected_ids) == 2
            assert 'agent_1' in selected_ids
            assert 'agent_3' in selected_ids

def test_roulette_wheel_selection(setup_cycle):
    cycle, _, _, _ = setup_cycle

    # Total fitness: 0.1+0.2+0.3+0.4 = 1.0
    with patch('random.uniform', side_effect=[0.05, 0.15, 0.45, 0.85]):
        selected_agents = cycle.roulette_wheel_selection(n_to_select=4)
        assert len(selected_agents) == 4
        assert 'agent_0' in selected_agents
        assert 'agent_1' in selected_agents
        assert 'agent_2' in selected_agents
        assert 'agent_3' in selected_agents

@pytest.mark.asyncio
@patch("ebiose.core.forge_cycle.crossover_agent_task", new_callable=AsyncMock)
async def test_crossover_and_mutate(mock_crossover_task, setup_cycle):
    cycle, _, _, _ = setup_cycle
    parent_ids = ['agent_0', 'agent_1']

    new_agent = Agent(id="child_agent", name="Child", agent_engine=MockGraphEngine())
    mock_crossover_task.return_value = new_agent

    offspring, cost = await cycle.crossover_and_mutate(parent_ids)

    assert mock_crossover_task.call_count == 2
    assert len(offspring) == 2
    assert offspring[0].id == "child_agent"

@pytest.mark.asyncio
@patch("ebiose.core.forge_cycle.ForgeCycle._evaluate_population", new_callable=AsyncMock, return_value=(0.5))
@patch("ebiose.core.forge_cycle.ForgeCycle.roulette_wheel_selection")
@patch("ebiose.core.forge_cycle.ForgeCycle.tournament_selection")
@patch("ebiose.core.forge_cycle.ForgeCycle.crossover_and_mutate", new_callable=AsyncMock)
async def test_run_generation(mock_crossover, mock_tournament, mock_roulette, mock_evaluate, setup_cycle):
    cycle, _, _, _ = setup_cycle

    mock_roulette.return_value = {'agent_3': cycle.agents['agent_3']}
    mock_tournament.return_value = ['agent_0', 'agent_1']
    # Fix validation error by providing a 'name'
    new_agent = Agent(id="new", name="New crossover agent", agent_engine=MockGraphEngine())
    mock_crossover.return_value = ([new_agent], 0.1)

    eval_cost, genetic_cost = await cycle.run_generation()

    mock_evaluate.assert_called_once()
    mock_roulette.assert_called_once()
    mock_tournament.assert_called_once()
    mock_crossover.assert_called_once_with(['agent_0', 'agent_1'])
    assert len(cycle.agents) == 2
    assert "new" in cycle.agents
    assert "agent_3" in cycle.agents

def test_save_current_state(setup_cycle, tmp_path):
    cycle, _, config, _ = setup_cycle
    config.local_results_path = tmp_path

    cycle.save_current_state(generation=1)

    gen_path = tmp_path / "generation=1"
    assert gen_path.exists()

    agents_path = gen_path / "agents"
    assert agents_path.exists()

    fitness_path = gen_path / "fitness.json"
    assert fitness_path.exists()

    with open(fitness_path) as f:
        data = json.load(f)
        assert data["agent_0"] == 0.1

    agent_file = agents_path / "agent_0.json"
    assert agent_file.exists()
    with open(agent_file) as f:
        agent_data = json.load(f)
        assert agent_data["name"] == "Agent 0"
