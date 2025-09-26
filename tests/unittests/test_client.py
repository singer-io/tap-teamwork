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


# ------------------------------
# Tests for raise_for_error()
# ------------------------------

@pytest.mark.parametrize("status_code, json_data, expected_message", [
    (401, {"message": "Unauthorized"}, "Unauthorized"),
    (403, {"message": "Forbidden"}, "Forbidden"),
    (500, {"message": "Internal server error"}, "Internal server error"),
])
def test_raise_for_error_with_various_errors(status_code, json_data, expected_message):
    """Ensure raise_for_error raises teamworkError with correct message for various HTTP codes."""
    response = Mock()
    response.status_code = status_code
    response.json.return_value = json_data

    with pytest.raises(teamworkError) as exc_info:
        raise_for_error(response)

    assert expected_message in str(exc_info.value)


@pytest.mark.parametrize("status_code", [200, 201, 204])
def test_raise_for_error_success_codes_do_not_raise(status_code):
    """Ensure raise_for_error does NOT raise exceptions for 2xx codes."""
    response = Mock()
    response.status_code = status_code
    response.json.return_value = {"message": "Success"}
    raise_for_error(response)  # no exception expected


def test_raise_for_error_204_without_json():
    """204 responses without JSON should not raise."""
    response = Mock()
    response.status_code = 204
    response.json.side_effect = ValueError("No JSON")
    raise_for_error(response)  # should not raise


# ------------------------------
# Fixture for Client setup
# ------------------------------

@pytest.fixture
def config():
    """Returns test config with dummy token."""
    return {
        "access_token": "dummy_token",
        "base_url": "https://example.com",
        "subdomain": "example"
    }


# ------------------------------
# Tests for Client methods
# ------------------------------

def test_authenticate_adds_headers(config):
    """Test that authenticate adds Bearer token and content type."""
    client = Client(config)
    headers, params = client.authenticate({}, {})
    assert headers["Authorization"] == "Bearer dummy_token"
    assert headers["Content-Type"] == "application/json"
    assert params == {}


@patch("tap_teamwork.client.requests.sessions.Session.request")
def test_get_success_response(mock_request, config):
    """Ensure GET request returns valid response JSON."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "ok"}
    mock_request.return_value = mock_response

    with Client(config) as client:
        response = client.get(endpoint="https://example.com/test", params={}, headers={})
    assert response == {"data": "ok"}


@patch("tap_teamwork.client.requests.sessions.Session.request")
def test_post_success_response(mock_request, config):
    """Ensure POST request returns valid response JSON."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "created"}
    mock_request.return_value = mock_response

    with Client(config) as client:
        response = client.post(endpoint="https://example.com/test", params={}, headers={}, body={"key": "value"})
    assert response == {"status": "created"}


# ------------------------------
# Retry logic tests
# ------------------------------

@patch("tap_teamwork.client.requests.sessions.Session.request")
@pytest.mark.parametrize("exception_type", [ConnectionError, Timeout, ChunkedEncodingError])
def test_retry_on_network_exceptions(mock_request, exception_type, config):
    """Validate retry behavior on transient errors (multiple tries)."""
    mock_request.side_effect = exception_type("Simulated network issue")

    with pytest.raises(exception_type):
        with Client(config) as client:
            client.get("https://example.com/test", params={}, headers={})

    # Should retry more than once
    assert mock_request.call_count >= 2
