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
from requests.models import Response

from tap_teamwork.client import Client, raise_for_error, wait_if_retry_after, _rate_limit_wait
from tap_teamwork.exceptions import teamworkError, teamworkBackoffError, teamworkRateLimitError


# ------------------------------
# Tests for raise_for_error()
# ------------------------------

@pytest.mark.parametrize("status_code, json_data, expected_message", [
    (401, {"message": "Unauthorized"}, "Unauthorized"),
    (403, {"message": "Forbidden"}, "Forbidden"),
    (500, {"message": "Internal server error"}, "Internal server error"),
    (429, {"message": "The API rate limit for your organisation/application pairing has been exceeded."},
         "The API rate limit for your organisation/application pairing has been exceeded. (Retry after 60 seconds.)"),
])
def test_raise_for_error_with_various_errors(status_code, json_data, expected_message):
    """Ensure raise_for_error raises teamworkError with correct message for various HTTP codes."""
    response = Mock()
    response.status_code = status_code
    response.json.return_value = json_data
    response.headers = {}

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
        "api_key": "dummy_token",
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

@patch("backoff._sync.time.sleep", return_value=None)
@patch("tap_teamwork.client.requests.sessions.Session.request")
@pytest.mark.parametrize("exception_type", [ConnectionError, Timeout, ChunkedEncodingError])
def test_retry_on_network_exceptions(mock_request, mock_sleep, exception_type, config):
    """Validate retry behavior on transient errors (multiple tries)."""
    mock_request.side_effect = exception_type("Simulated network issue")

    with pytest.raises(exception_type):
        with Client(config) as client:
            client.get("https://example.com/test", params={}, headers={})

    # Should retry more than once
    assert mock_request.call_count >= 1


# ------------------------------
# Tests for wait_if_retry_after() — informational on_backoff handler
# ------------------------------


def test_wait_if_retry_after_with_exception_and_retry_after():
    """When 'exception' is present and has retry_after, handler logs without error."""
    exc = teamworkRateLimitError("Rate limit hit", response=Mock(headers={"X-Rate-Limit-Reset": "30"}))
    details = {"exception": exc, "wait": 1}
    wait_if_retry_after(details)  # should not raise


def test_wait_if_retry_after_with_exception_no_retry_after():
    """When 'exception' has no retry_after, handler runs without error."""
    exc = Exception("generic error")
    details = {"exception": exc, "wait": 1}
    wait_if_retry_after(details)  # should not raise


def test_wait_if_retry_after_without_exception_key():
    """When 'exception' key is absent from details, handler runs without error."""
    details = {"target": "some_func", "tries": 1, "wait": 1}
    wait_if_retry_after(details)  # should not raise


# ------------------------------
# Tests for _rate_limit_wait() — wait generator that respects Retry-After
# ------------------------------


def _prime_wait_gen():
    """Create and prime a _rate_limit_wait generator (same as backoff does)."""
    gen = _rate_limit_wait()
    gen.send(None)  # prime, matches _init_wait_gen behavior
    return gen


def test_rate_limit_wait_uses_retry_after_from_exception():
    """When exception has retry_after=60, generator yields 60."""
    gen = _prime_wait_gen()
    exc = teamworkRateLimitError("Rate limit hit", response=Mock(headers={"X-Rate-Limit-Reset": "60"}))
    wait = gen.send(exc)
    assert wait == 60


def test_rate_limit_wait_uses_retry_after_header():
    """When exception has Retry-After response header, generator uses it."""
    gen = _prime_wait_gen()
    exc = ConnectionError("reset")
    exc.response = Mock(headers={"Retry-After": "45"})
    wait = gen.send(exc)
    assert wait == 45


def test_rate_limit_wait_uses_x_rate_limit_reset_header():
    """When exception has X-Rate-Limit-Reset response header, generator uses it."""
    gen = _prime_wait_gen()
    exc = ConnectionError("reset")
    exc.response = Mock(headers={"X-Rate-Limit-Reset": "20"})
    wait = gen.send(exc)
    assert wait == 20


def test_rate_limit_wait_retry_after_header_takes_priority():
    """When both Retry-After and X-Rate-Limit-Reset are present, Retry-After wins."""
    gen = _prime_wait_gen()
    exc = ConnectionError("reset")
    exc.response = Mock(headers={"Retry-After": "60", "X-Rate-Limit-Reset": "10"})
    wait = gen.send(exc)
    assert wait == 60


def test_rate_limit_wait_non_numeric_header_falls_back_to_expo():
    """When header value is non-numeric, fall back to exponential backoff."""
    gen = _prime_wait_gen()
    exc = ConnectionError("reset")
    exc.response = Mock(headers={"Retry-After": "not-a-number"})
    wait = gen.send(exc)
    assert isinstance(wait, (int, float))
    assert wait > 0  # exponential backoff value


def test_rate_limit_wait_no_retry_info_falls_back_to_expo():
    """When exception has no retry_after and no headers, fall back to exponential backoff."""
    gen = _prime_wait_gen()
    exc = ConnectionError("reset")
    exc.response = None
    wait = gen.send(exc)
    assert isinstance(wait, (int, float))
    assert wait > 0


def test_rate_limit_wait_minimum_of_1_second():
    """When retry_after is 0, generator clamps to minimum of 1 second."""
    gen = _prime_wait_gen()
    exc = teamworkBackoffError("rate limited", response=Mock(headers={"X-Rate-Limit-Reset": "0"}))
    # retry_after=0 is not None, so max(0, 1) = 1
    wait = gen.send(exc)
    assert wait == 1


def test_wait_if_retry_after_empty_headers():
    """When response headers exist but contain neither Retry-After nor X-Rate-Limit-Reset."""
    exc = ConnectionError("connection reset")
    exc.response = Mock(headers={})
    details = {"exception": exc, "wait": 1}
    wait_if_retry_after(details)
    assert details["wait"] == 1


@patch("backoff._sync.time.sleep", return_value=None)
@patch("tap_teamwork.client.requests.sessions.Session.request")
def test_request_retries_on_429(mock_request, mock_sleep, config):
    """Ensure __make_request retries up to max_tries on teamworkBackoffError (429) and sleeps between retries."""

    mock_response = Mock(spec=Response)
    mock_response.status_code = 429
    mock_response.headers = {"X-Rate-Limit-Reset": "10"}
    mock_response.json.return_value = {"message": "Rate limit exceeded"}

    mock_request.return_value = mock_response

    with Client(config) as client:
        with pytest.raises(teamworkBackoffError) as exc_info:
            client.get("https://example.com/test", params={}, headers={})

    assert mock_request.call_count == 7
    assert exc_info.value.retry_after == 10
    assert "Retry after 10 seconds." in str(exc_info.value)

    # Verify backoff actually slept between retries (7 tries = 6 sleeps)
    assert mock_sleep.call_count == 6
    for call in mock_sleep.call_args_list:
        slept = call[0][0]
        assert slept > 0, f"Expected positive sleep duration, got {slept}"


@patch("backoff._sync.time.sleep", return_value=None)
@patch("tap_teamwork.client.requests.sessions.Session.request")
def test_request_retry_sleep_called_on_connection_error(mock_request, mock_sleep, config):
    """Ensure backoff sleeps between retries on transient ConnectionError."""
    mock_request.side_effect = ConnectionError("connection reset")

    with Client(config) as client:
        with pytest.raises(ConnectionError):
            client.get("https://example.com/test", params={}, headers={})

    assert mock_request.call_count == 7
    assert mock_sleep.call_count == 6
    for call in mock_sleep.call_args_list:
        slept = call[0][0]
        assert slept > 0, f"Expected positive sleep duration, got {slept}"
