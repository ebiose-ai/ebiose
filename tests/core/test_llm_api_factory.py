import pytest
from unittest.mock import patch
from ebiose.core.llm_api_factory import LLMApiFactory

@patch("ebiose.backends.langgraph.llm_api.LangGraphLLMApi")
def test_initialize(mock_langgraph_llm_api):
    LLMApiFactory.initialize(
        mode="local",
        lite_llm_api_key="key",
        lite_llm_api_base="base"
    )

    mock_langgraph_llm_api.initialize.assert_called_once_with(
        "local",
        "key",
        "base",
        None
    )
