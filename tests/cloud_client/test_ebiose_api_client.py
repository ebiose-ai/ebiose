import pytest
from unittest.mock import patch, MagicMock
from ebiose.cloud_client.ebiose_api_client import EbioseAPIClient, build_agent_input_model
from ebiose.cloud_client.client import EbioseCloudClient, EbioseCloudError
from ebiose.core.agent import Agent

@pytest.fixture(autouse=True)
def reset_api_client():
    EbioseAPIClient._client = None
    yield

@patch("ebiose.cloud_client.ebiose_api_client.ModelEndpoints")
@patch("ebiose.cloud_client.ebiose_api_client.EbioseCloudClient")
def test_set_client(mock_cloud_client, mock_model_endpoints):
    mock_model_endpoints.get_ebiose_api_base.return_value = "https://test.com"
    mock_model_endpoints.get_ebiose_api_key.return_value = "test_key"

    EbioseAPIClient.set_client()

    mock_cloud_client.assert_called_once_with(
        base_url="https://test.com",
        api_key="test_key"
    )

def test_to_snake_case():
    assert EbioseAPIClient._to_snake_case("PascalCase") == "pascal_case"
    assert EbioseAPIClient._to_snake_case("camelCase") == "camel_case"

def test_convert_data_keys():
    data = {"PascalCase": {"camelCase": 1}}
    converted = EbioseAPIClient._convert_data_keys(data)
    assert converted == {"pascal_case": {"camel_case": 1}}

@patch.object(EbioseCloudClient, "user_info")
def test_handle_api_errors(mock_user_info):
    mock_user_info.return_value = {"userId": "123"}

    # This is a bit of a hack to test the decorator
    @EbioseAPIClient._handle_api_errors
    def test_func(cls):
        return cls._client.user_info()

    with patch.object(EbioseAPIClient, "set_client") as mock_set_client:
        EbioseAPIClient._client = None
        test_func(EbioseAPIClient)
        mock_set_client.assert_called_once()

@pytest.fixture
def client():
    client = MagicMock(spec=EbioseCloudClient)
    return client

def test_get_ecosystems(client):
    EbioseAPIClient._client = client
    EbioseAPIClient.get_ecosystems()
    client.list_ecosystems.assert_called_once()
