import pytest
from unittest.mock import patch
from ebiose.core.llm_api import LLMApi, LLMAPIConfig

class ConcreteLLMApi(LLMApi):
    async def process_llm_call(self, *args, **kwargs):
        pass

@pytest.fixture(autouse=True)
def reset_llm_api_class_vars():
    ConcreteLLMApi._cost_per_agent = {}
    ConcreteLLMApi.total_cost = 0.0
    ConcreteLLMApi._forge_cycle_costs = {}
    yield

def test_initialize():
    api = ConcreteLLMApi.initialize(mode="local", lite_llm_api_key="key", lite_llm_api_base="base")
    assert api.mode == "local"
    assert api.lite_llm_api_key == "key"
    assert api.lite_llm_api_base == "base"

@patch("ebiose.core.llm_api.ModelEndpoints.use_lite_llm", return_value=True)
@patch("ebiose.core.llm_api.ModelEndpoints.get_lite_llm_config", return_value=("key", "config_base"))
def test_initialize_local_mode_with_config(mock_get_config, mock_use_lite_llm):
    api = ConcreteLLMApi.initialize(mode="local")
    assert api.lite_llm_api_base == "config_base"

def test_cost_tracking():
    ConcreteLLMApi.add_agent_cost("agent1", 10)
    ConcreteLLMApi.add_agent_cost("agent2", 5)
    ConcreteLLMApi.add_agent_cost("agent1", 2)

    assert ConcreteLLMApi.get_agent_cost("agent1") == 12
    assert ConcreteLLMApi.get_agent_cost("agent2") == 5
    assert ConcreteLLMApi.get_agents_total_cost() == 17

    ConcreteLLMApi.add_forge_cycle_cost("cycle1", 100)
    assert ConcreteLLMApi.get_total_cost("cycle1") == 100

    ConcreteLLMApi.update_total_cost(200)
    assert ConcreteLLMApi.get_total_cost() == 200
