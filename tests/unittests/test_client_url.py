"""
Unit tests specifically for endpoint construction (base_url + path join)
in tap_teamwork.client.Client.
"""

from unittest.mock import Mock, patch
from tap_teamwork.client import Client


def make_mock_response():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True}
    return mock_response


@patch("requests.Session.request")
def test_get_with_path_no_leading_slash(mock_request):
    """
    When endpoint=None and path has no leading '/', it should join cleanly.
    """
    mock_request.return_value = make_mock_response()
    config = {"access_token": "dummy", "base_url": "https://example.com"}

    with Client(config) as client:
        client.get(endpoint=None, path="v1/users", params={}, headers={})

    called_url = mock_request.call_args[0][1]
    assert called_url == "https://example.com/v1/users"


@patch("requests.Session.request")
def test_get_with_path_leading_slash(mock_request):
    """
    When endpoint=None and path has a leading '/', it should not double slash.
    """
    mock_request.return_value = make_mock_response()
    config = {"access_token": "dummy", "base_url": "https://example.com"}

    with Client(config) as client:
        client.get(endpoint=None, path="/v1/users", params={}, headers={})

    called_url = mock_request.call_args[0][1]
    assert called_url == "https://example.com/v1/users"


@patch("requests.Session.request")
def test_post_with_path_no_leading_slash(mock_request):
    """
    POST: endpoint=None + path without leading '/' should join cleanly.
    """
    mock_request.return_value = make_mock_response()
    config = {"access_token": "dummy", "base_url": "https://example.com"}

    with Client(config) as client:
        client.post(endpoint=None, path="v1/items", params={}, headers={}, body={"k": "v"})

    called_url = mock_request.call_args[0][1]
    assert called_url == "https://example.com/v1/items"


@patch("requests.Session.request")
def test_post_with_path_leading_slash(mock_request):
    """
    POST: endpoint=None + path with leading '/' should join cleanly.
    """
    mock_request.return_value = make_mock_response()
    config = {"access_token": "dummy", "base_url": "https://example.com"}

    with Client(config) as client:
        client.post(endpoint=None, path="/v1/items", params={}, headers={}, body={"k": "v"})

    called_url = mock_request.call_args[0][1]
    assert called_url == "https://example.com/v1/items"


@patch("requests.Session.request")
def test_explicit_endpoint_bypasses_path(mock_request):
    """
    If endpoint is provided, it must be used directly and path ignored.
    """
    mock_request.return_value = make_mock_response()
    config = {"access_token": "dummy", "base_url": "https://example.com"}

    with Client(config) as client:
        client.get(endpoint="https://alt.example.com/x", path="/ignored", params={}, headers={})

    called_url = mock_request.call_args[0][1]
    assert called_url == "https://alt.example.com/x"
