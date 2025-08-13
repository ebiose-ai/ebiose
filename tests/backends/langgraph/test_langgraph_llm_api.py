import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from ebiose.backends.langgraph.llm_api import LangGraphLLMApi, LangGraphLLMApiError
from ebiose.core.model_endpoint import ModelEndpoint
from pydantic import SecretStr

@pytest.fixture(autouse=True)
def reset_llm_api_class_vars():
    LangGraphLLMApi.mode = "cloud"
    LangGraphLLMApi.total_cost = 0.0
    yield

def test_langgraph_llm_api_error():
    error = LangGraphLLMApiError("test message")
    assert "test message" in str(error)

@patch("ebiose.cloud_client.ebiose_api_client.EbioseAPIClient.get_cost", return_value=123.45)
def test_get_total_cost_cloud_mode(mock_get_cost):
    LangGraphLLMApi.get_total_cost("cycle1")
    mock_get_cost.assert_called_once_with(forge_cycle_uuid="cycle1")

@patch("ebiose.backends.langgraph.llm_api.ModelEndpoints.get_model_endpoint")
@patch("ebiose.backends.langgraph.llm_api.ChatOpenAI", new_callable=MagicMock)
def test_get_llm_openai(mock_chat_openai, mock_get_endpoint):
    mock_get_endpoint.return_value = ModelEndpoint(
        endpoint_id="gpt-4",
        provider="OpenAI",
        api_key=SecretStr("key")
    )
    LangGraphLLMApi.mode = "local"
    llm = LangGraphLLMApi._get_llm("gpt-4", 0.7, 1024)
    mock_chat_openai.assert_called_once()
    assert llm is not None

@pytest.mark.asyncio
@patch("ebiose.backends.langgraph.llm_api.LangGraphLLMApi._get_llm")
async def test_call_llm(mock_get_llm):
    mock_llm = MagicMock()
    mock_llm.with_retry.return_value.ainvoke = AsyncMock()
    mock_get_llm.return_value = mock_llm

    await LangGraphLLMApi._call_llm("gpt-4", [], 0.7, 1024)

    mock_get_llm.assert_called_once_with("gpt-4", 0.7, 1024)
    mock_llm.with_retry.return_value.ainvoke.assert_called_once()

@pytest.mark.asyncio
@patch("ebiose.backends.langgraph.llm_api.LangGraphLLMApi._call_llm")
@patch("ebiose.backends.langgraph.llm_api.cost_per_token", return_value=(0.1, 0.2))
async def test_process_llm_call(mock_cost, mock_call_llm):
    mock_response = MagicMock()
    mock_response.response_metadata = {"token_usage": {"completion_tokens": 10, "prompt_tokens": 20}}
    mock_call_llm.return_value = mock_response

    await LangGraphLLMApi.process_llm_call("gpt-4", [], "agent1")

    mock_call_llm.assert_called_once()
    mock_cost.assert_called_once()
    assert LangGraphLLMApi.get_agent_cost("agent1") > 0
