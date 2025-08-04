"""
Unit tests for the Client class and the raise_for_error function in tap_teamwork.client.

Covers:
- HTTP error parsing and exception raising
- Authentication header generation
- Handling of successful GET/POST requests
- Retry logic for transient network exceptions
"""

import pytest
from unittest.mock import Mock, patch
from requests.exceptions import ConnectionError, Timeout, ChunkedEncodingError

from tap_teamwork.client import Client, raise_for_error
from tap_teamwork.exceptions import teamworkError

# Tests for the raise_for_error() function

@pytest.mark.parametrize("status_code, json_data, expected_message", [
    (401, {"message": "Unauthorized"}, "Unauthorized"),
    (403, {"message": "Forbidden"}, "Forbidden"),
    (500, {"message": "Internal server error"}, "Internal server error"),
])
def test_raise_for_error_with_various_errors(status_code, json_data, expected_message):
    """
    Test that raise_for_error raises teamworkError with the correct message.
    """
    response = Mock()
    response.status_code = status_code
    response.json.return_value = json_data

    with pytest.raises(teamworkError) as exc_info:
        raise_for_error(response)
    assert expected_message in str(exc_info.value)


@pytest.mark.parametrize("status_code", [200, 201, 204])
def test_raise_for_error_success_codes_do_not_raise(status_code):
    """
    Test that raise_for_error does NOT raise for 2xx status codes.
    """
    response = Mock()
    response.status_code = status_code
    response.json.return_value = {"message": "Success"}
    try:
        raise_for_error(response)
    except Exception as e:
        pytest.fail(f"raise_for_error should not raise for status {status_code}, but got: {e}")

# Fixture for Client test setup

@pytest.fixture
def config():
    """
    Returns a sample config dict with dummy access token and base URL.
    """
    return {
        "access_token": "dummy_token",
        "base_url": "https://example.com"
    }

# Tests for Client methods

def test_authenticate_adds_headers(config):
    """
    Test that authenticate() sets Authorization and Content-Type headers correctly.
    """
    client = Client(config)
    headers, params = client.authenticate({}, {})
    assert headers["Authorization"] == "Bearer dummy_token"
    assert headers["Content-Type"] == "application/json"
    assert params == {}


@patch("requests.Session.request")
def test_get_success_response(mock_request, config):
    """
    Test that GET request returns parsed JSON response on success.
    """
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "ok"}
    mock_request.return_value = mock_response

    with Client(config) as client:
        response = client.get(endpoint="https://example.com/test", params={}, headers={})
    assert response == {"data": "ok"}


@patch("requests.Session.request")
def test_post_success_response(mock_request, config):
    """
    Test that POST request returns parsed JSON response on success.
    """
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "created"}
    mock_request.return_value = mock_response

    with Client(config) as client:
        response = client.post(endpoint="https://example.com/test", params={}, headers={}, body={"key": "value"})
    assert response == {"status": "created"}

# Tests for retry behavior on exceptions

@pytest.mark.parametrize("exception_type", [ConnectionError, Timeout, ChunkedEncodingError])
@patch("requests.Session.request")
def test_retry_on_network_exceptions(mock_request, exception_type, config):
    """
    Test that Client retries up to 5 times on transient network exceptions
    """
    mock_request.side_effect = exception_type("simulated error")
    with pytest.raises(exception_type):
        with Client(config) as client:
            client.get("https://example.com/test", params={}, headers={})
    assert mock_request.call_count == 5
