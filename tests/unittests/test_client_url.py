"""
Unit tests specifically for endpoint construction (subdomain-built base URL + path join)
in tap_teamwork.client.Client.
"""

from unittest.mock import Mock, patch
from tap_teamwork.client import Client


def make_mock_response():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True}
    return mock_response


DUMMY_SUBDOMAIN = "testsubdomain"
EXPECTED_BASE = f"https://{DUMMY_SUBDOMAIN}.teamwork.com"


@patch("requests.Session.request")
def test_get_with_path_no_leading_slash(mock_request):
    mock_request.return_value = make_mock_response()
    config = {"api_key": "dummy", "subdomain": DUMMY_SUBDOMAIN}

    with Client(config) as client:
        client.get(endpoint=None, path="v1/users", params={}, headers={})

    called_url = mock_request.call_args[0][1]
    assert called_url == f"{EXPECTED_BASE}/v1/users"


@patch("requests.Session.request")
def test_get_with_path_leading_slash(mock_request):
    mock_request.return_value = make_mock_response()
    config = {"api_key": "dummy", "subdomain": DUMMY_SUBDOMAIN}

    with Client(config) as client:
        client.get(endpoint=None, path="/v1/users", params={}, headers={})

    called_url = mock_request.call_args[0][1]
    assert called_url == f"{EXPECTED_BASE}/v1/users"


@patch("requests.Session.request")
def test_post_with_path_no_leading_slash(mock_request):
    mock_request.return_value = make_mock_response()
    config = {"api_key": "dummy", "subdomain": DUMMY_SUBDOMAIN}

    with Client(config) as client:
        client.post(endpoint=None, path="v1/items", params={}, headers={}, body={"k": "v"})

    called_url = mock_request.call_args[0][1]
    assert called_url == f"{EXPECTED_BASE}/v1/items"


@patch("requests.Session.request")
def test_post_with_path_leading_slash(mock_request):
    mock_request.return_value = make_mock_response()
    config = {"api_key": "dummy", "subdomain": DUMMY_SUBDOMAIN}

    with Client(config) as client:
        client.post(endpoint=None, path="/v1/items", params={}, headers={}, body={"k": "v"})

    called_url = mock_request.call_args[0][1]
    assert called_url == f"{EXPECTED_BASE}/v1/items"


@patch("requests.Session.request")
def test_explicit_endpoint_bypasses_path(mock_request):
    mock_request.return_value = make_mock_response()
    config = {"api_key": "dummy", "subdomain": DUMMY_SUBDOMAIN}

    with Client(config) as client:
        client.get(endpoint="https://alt.example.com/x", path="/ignored", params={}, headers={})

    called_url = mock_request.call_args[0][1]
    assert called_url == "https://alt.example.com/x"
