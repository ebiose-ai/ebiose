import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open
from pydantic import SecretStr

from ebiose.core.model_endpoint import ModelEndpoints, ModelEndpoint

@pytest.fixture
def mock_yaml_file(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "model_endpoints.yml"
    p.write_text("""
default_endpoint_id: "gpt-4"
ebiose:
  api_key: "ebiose_key"
  api_base: "https://api.ebiose.com"
lite_llm:
  use: true
  use_proxy: true
  api_key: "lite_llm_key"
  api_base: "https://lite.llm"
endpoints:
  - endpoint_id: "gpt-4"
    provider: "openai"
  - endpoint_id: "claude-2"
    provider: "anthropic"
""")
    return str(p)

@pytest.fixture(autouse=True)
def reset_model_endpoints_class_vars():
    ModelEndpoints._default_endpoint_id = None
    ModelEndpoints._ebiose_api_config = None
    ModelEndpoints._lite_llm = {"use": False, "use_proxy": False}
    ModelEndpoints._endpoints = []
    yield

def test_load_model_endpoints(mock_yaml_file):
    endpoints = ModelEndpoints.load_model_endpoints(mock_yaml_file)

    assert ModelEndpoints.get_default_model_endpoint_id() == "gpt-4"
    assert ModelEndpoints.get_ebiose_api_key() == "ebiose_key"
    assert ModelEndpoints.get_ebiose_api_base() == "https://api.ebiose.com"
    assert ModelEndpoints.use_lite_llm() is True
    assert ModelEndpoints.use_lite_llm_proxy() is True
    key, base = ModelEndpoints.get_lite_llm_config()
    assert key == "lite_llm_key"
    assert base == "https://lite.llm"
    assert len(endpoints) == 2
    assert endpoints[0].endpoint_id == "gpt-4"

def test_get_model_endpoint(mock_yaml_file):
    endpoint = ModelEndpoints.get_model_endpoint("claude-2", mock_yaml_file)
    assert endpoint.provider == "anthropic"
    assert ModelEndpoints.get_model_endpoint("non_existent", mock_yaml_file) is None

def test_get_all_model_endpoints(mock_yaml_file):
    endpoints = ModelEndpoints.get_all_model_endpoints(mock_yaml_file)
    assert len(endpoints) == 2

def test_load_model_endpoints_no_default_id(tmp_path):
    p = tmp_path / "model_endpoints.yml"
    p.write_text("endpoints: []")
    with pytest.raises(ValueError):
        ModelEndpoints.load_model_endpoints(str(p))
