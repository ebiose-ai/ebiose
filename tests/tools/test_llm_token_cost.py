import pytest
from unittest.mock import patch, mock_open
from ebiose.tools.llm_token_cost import load_model_prices_and_context_window

@patch("pathlib.Path.open", new_callable=mock_open, read_data='{"gpt-4": {"input_cost_per_token": 0.00001}}')
def test_load_model_prices_and_context_window(mock_file):
    data = load_model_prices_and_context_window()
    assert "gpt-4" in data
    assert data["gpt-4"]["input_cost_per_token"] == 0.00001
