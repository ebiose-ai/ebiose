import pytest
from unittest.mock import patch, MagicMock
import requests
from ebiose.cloud_client.client import (
    EbioseCloudClient,
    EbioseCloudHTTPError,
    EbioseCloudError,
    ApiKeyInputModel,
)
from datetime import datetime

@pytest.fixture
def client():
    return EbioseCloudClient(base_url="https://test.com", api_key="test_key")

@patch("requests.request")
def test_request_success(mock_request, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success"}
    mock_request.return_value = mock_response

    response = client._request("GET", "/test")

    mock_request.assert_called_once()
    assert response["status"] == "success"

@patch("requests.request")
def test_request_http_error(mock_request, client):
    mock_response = MagicMock()
    http_error = requests.exceptions.HTTPError()
    http_error.request = MagicMock()
    http_error.request.method = "GET"
    http_error.request.url = "https://test.com/test"
    mock_response.raise_for_status.side_effect = http_error
    mock_response.text = "error"
    mock_response.status_code = 404
    mock_request.return_value = mock_response

    with pytest.raises(EbioseCloudHTTPError):
        client._request("GET", "/test")

@patch("requests.request")
def test_request_other_error(mock_request, client):
    mock_request.side_effect = requests.exceptions.RequestException

    with pytest.raises(EbioseCloudError):
        client._request("GET", "/test")

@patch.object(EbioseCloudClient, "_request")
def test_get_api_keys(mock_request, client):
    client.get_api_keys()
    mock_request.assert_called_once_with("GET", "/apikeys")

@patch.object(EbioseCloudClient, "_request")
def test_add_api_key(mock_request, client):
    data = ApiKeyInputModel(expirationDate=datetime.now())
    client.add_api_key(data)
    mock_request.assert_called_once_with("POST", "/apikeys", json_data=data)

@patch.object(EbioseCloudClient, "_request")
def test_update_api_key(mock_request, client):
    data = ApiKeyInputModel(expirationDate=datetime.now())
    client.update_api_key("key123", data)
    mock_request.assert_called_once_with("PUT", "/apikeys/key123", json_data=data)

@patch.object(EbioseCloudClient, "_request")
def test_delete_api_key(mock_request, client):
    client.delete_api_key("key123")
    mock_request.assert_called_once_with("DELETE", "/apikeys/key123")
