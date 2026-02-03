import numpy as np
import pytest
from pydantic import BaseModel

from ebiose.core.agent import Agent
from ebiose.core.agent_engine import AgentEngine, AgentEngineRunError
from ebiose.core.agent_engine_factory import AgentEngineFactory
from ebiose.core.ecosystem import Ecosystem
from ebiose.core.llm_api import LLMApi


class DummyInput(BaseModel):
    text: str


class DummyEngine(AgentEngine):
    engine_type: str = "dummy"

    async def _run_implementation(self, agent_input: BaseModel, master_agent_id: str, forge_cycle_id: str | None = None, **kwargs):
        return {"ok": True, "input": agent_input.model_dump()}


class DummyEngineFail(AgentEngine):
    engine_type: str = "dummy"

    async def _run_implementation(self, agent_input: BaseModel, master_agent_id: str, forge_cycle_id: str | None = None, **kwargs):
        raise ValueError("boom")


class DummyLLMApi(LLMApi):
    @classmethod
    async def process_llm_call(
        cls,
        model_endpoint_id: str,
        messages: list,
        agent_id: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        tools: list | None = None,
    ):
        return {"ok": True}


def test_agent_serialization_and_embedding(monkeypatch):
    def fake_embeddings(text: str):
        return [0.1, 0.2, 0.3]

    monkeypatch.setattr("ebiose.core.agent.generate_embeddings", fake_embeddings)

    engine = DummyEngine(agent_id="agent-1", configuration={})
    agent = Agent(name="test", description="hello", agent_engine=engine)

    assert agent.description_embedding == [0.1, 0.2, 0.3]
    assert agent.serialize_agent_engine(engine)["engineType"] == "dummy"
    assert agent.serialize_agent_engine(None) == {}


@pytest.mark.asyncio
async def test_agent_run_uses_engine(monkeypatch):
    engine = DummyEngine(agent_id="agent-2", configuration={})
    agent = Agent(name="runner", description="run", agent_engine=engine)

    result = await agent.run(DummyInput(text="hi"), master_agent_id="master")
    assert result["ok"] is True
    assert result["input"]["text"] == "hi"


@pytest.mark.asyncio
async def test_agent_engine_run_error_message():
    engine = DummyEngineFail(agent_id="agent-err", configuration={})
    with pytest.raises(AgentEngineRunError) as exc_info:
        await engine.run(DummyInput(text="x"), master_agent_id="master")

    msg = str(exc_info.value)
    assert "AgentRunError" in msg
    assert "agent-err" in msg
    assert "boom" in msg


def test_agent_engine_factory_unknown():
    with pytest.raises(ValueError):
        AgentEngineFactory.create_engine(
            engine_type="nope",
            agent_id="agent-1",
            configuration={},
        )


def test_agent_engine_factory_langgraph(monkeypatch):
    created = {}

    class StubLangGraphEngine:
        def __init__(self, agent_id: str, configuration: dict, model_endpoint_id: str | None = None):
            created["agent_id"] = agent_id
            created["configuration"] = configuration
            created["model_endpoint_id"] = model_endpoint_id

    monkeypatch.setattr("ebiose.core.agent_engine_factory.LangGraphEngine", StubLangGraphEngine)
    monkeypatch.setattr("ebiose.core.agent_engine_factory.ModelEndpoints.get_default_model_endpoint_id", lambda: "default-endpoint")

    AgentEngineFactory.create_engine(
        engine_type="langgraph_engine",
        agent_id="agent-1",
        configuration={"graph": {}},
    )

    assert created["agent_id"] == "agent-1"
    assert created["model_endpoint_id"] == "default-endpoint"


def test_ecosystem_new(monkeypatch):
    dummy_agent = Agent(name="a", description="desc")

    monkeypatch.setattr("ebiose.core.ecosystem.GraphUtils.get_architect_agent", lambda _: dummy_agent)
    monkeypatch.setattr("ebiose.core.ecosystem.GraphUtils.get_crossover_agent", lambda _: dummy_agent)
    monkeypatch.setattr("ebiose.core.ecosystem.GraphUtils.get_mutation_agent", lambda _: dummy_agent)
    monkeypatch.setattr("ebiose.core.ecosystem.ModelEndpoints.get_default_meta_agent_endpoint_id", lambda: "meta")

    ecosystem = Ecosystem.new()

    assert ecosystem.initial_architect_agents is not None
    assert ecosystem.initial_genetic_operator_agents is not None
    assert len(ecosystem.initial_architect_agents) == 1
    assert len(ecosystem.initial_genetic_operator_agents) == 2


@pytest.mark.asyncio
async def test_ecosystem_add_and_select_agents():
    agent_a = Agent(name="a", description="a")
    agent_b = Agent(name="b", description="b")

    agent_a.description_embedding = np.array([1.0, 0.0])
    agent_b.description_embedding = np.array([0.0, 1.0])

    ecosystem = Ecosystem(agents={agent_a.id: agent_a, agent_b.id: agent_b})

    class DummyForge:
        def __init__(self):
            self.id = "forge-1"
            self.description_embedding = np.array([1.0, 0.0])

    forge = DummyForge()
    ecosystem.add_forge(forge)

    selected = await ecosystem.select_agents_for_forge(forge, 1)
    assert len(selected) == 1
    assert selected[0].id == agent_a.id


def test_llm_api_initialize_and_costs(monkeypatch):
    DummyLLMApi.total_cost = 0.0
    DummyLLMApi._cost_per_agent = {}

    monkeypatch.setattr("ebiose.core.llm_api.ModelEndpoints.use_lite_llm", lambda: True)
    monkeypatch.setattr("ebiose.core.llm_api.ModelEndpoints.get_lite_llm_config", lambda: (None, "http://local"))

    DummyLLMApi.initialize(mode="local")
    assert DummyLLMApi.lite_llm_api_base == "http://local"

    DummyLLMApi.add_agent_cost("agent-1", 1.25)
    DummyLLMApi.add_agent_cost("agent-1", 0.75)
    assert DummyLLMApi.get_agent_cost("agent-1") == 2.0
    assert DummyLLMApi.get_total_cost() == 2.0


def test_llm_api_get_total_cost_cloud(monkeypatch):
    DummyLLMApi.mode = "cloud"
    monkeypatch.setattr("ebiose.core.llm_api.EbioseAPIClient.get_cost", lambda forge_cycle_uuid: 12.34)
    assert DummyLLMApi.get_total_cost(forge_cycle_id="forge-1") == 12.34
