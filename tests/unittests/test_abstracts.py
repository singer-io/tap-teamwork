"""
Unit tests for validating IncrementalStream and FullTableStream abstract base classes.
Includes tests for:
- Bookmark handling
- URL formatting
- Sync process and record writing
"""

import pytest
from unittest.mock import MagicMock, patch, ANY
from tap_teamwork.streams.abstracts import IncrementalStream, FullTableStream


# Concrete dummy stream classes used for testing
class DummyIncrementalStream(IncrementalStream):
    """Concrete implementation of IncrementalStream for test purposes."""
    tap_stream_id = "dummy_incremental"
    replication_keys = ["updatedAt"]
    key_properties = ["id"]
    replication_method = "INCREMENTAL"


class DummyFullTableStream(FullTableStream):
    """Concrete implementation of FullTableStream for test purposes."""
    tap_stream_id = "dummy_full"
    replication_keys = []
    key_properties = ["id"]
    replication_method = "FULL_TABLE"


# Fixtures

@pytest.fixture
def dummy_catalog():
    """Creates a mocked catalog object with minimal schema and metadata for testing."""
    mock_catalog = MagicMock()
    mock_catalog.schema.to_dict.return_value = {
        "type": "object",
        "properties": {"id": {"type": "string"}}
    }
    mock_catalog.metadata = []
    return mock_catalog


@pytest.fixture
def dummy_client():
    """Creates a mocked API client object with sample response and base URL."""
    client = MagicMock()
    client.base_url = "https://example.com"
    client.get.return_value = {"dummy_key": [{"id": "1"}, {"id": "2"}]}
    client.config = {"start_date": "2024-01-01T00:00:00Z"}
    return client


# Tests for get_starting_timestamp

def test_get_starting_timestamp_with_bookmark(dummy_catalog, dummy_client):
    dummy_client.config["start_date"] = "2025-01-01T00:00:00Z"
    stream = DummyIncrementalStream(client=dummy_client, catalog=dummy_catalog)
    state = {}
    result = stream.get_starting_timestamp(state)
    assert result == "2025-01-01T00:00:00Z"


def test_get_starting_timestamp_without_bookmark(dummy_catalog, dummy_client):
    dummy_client.config["start_date"] = "2023-01-01T00:00:00Z"
    stream = DummyIncrementalStream(client=dummy_client, catalog=dummy_catalog)
    state = {}
    result = stream.get_starting_timestamp(state)
    assert result == "2023-01-01T00:00:00Z"


# Tests for get_url_endpoint

def test_get_url_endpoint_no_parent(dummy_catalog, dummy_client):
    stream = DummyFullTableStream(client=dummy_client, catalog=dummy_catalog)
    stream.path = "path/to/resource.json"
    result = stream.get_url_endpoint()
    assert result == "https://example.com/path/to/resource.json"


def test_get_url_endpoint_with_parent(dummy_catalog, dummy_client):
    stream = DummyFullTableStream(client=dummy_client, catalog=dummy_catalog)
    stream.path = "spaces/{spaceId}/collaborators.json"
    result = stream.get_url_endpoint(parent_obj={"spaceId": "1234"})
    assert result == "https://example.com/spaces/1234/collaborators.json"


# FullTableStream sync test

@patch("tap_teamwork.streams.abstracts.metrics.record_counter")
@patch("tap_teamwork.streams.abstracts.write_record")
@patch("tap_teamwork.streams.abstracts.Transformer")
def test_full_table_stream_sync(mock_transformer, mock_write_record, mock_counter, dummy_catalog, dummy_client):
    dummy_client.get.return_value = {"dummy_key": [{"id": "1"}, {"id": "2"}]}
    mock_counter_inst = MagicMock()
    mock_counter_inst.__enter__.return_value = mock_counter_inst
    mock_counter_inst.__exit__.return_value = False
    mock_counter_inst.value = 2
    mock_counter.return_value = mock_counter_inst

    stream = DummyFullTableStream(client=dummy_client, catalog=dummy_catalog)
    stream.data_key = "dummy_key"
    stream.is_selected = MagicMock(return_value=True)

    transformer = MagicMock()
    transformer.transform.side_effect = lambda record, schema, metadata: record
    mock_transformer.return_value = transformer

    state = {}
    count = stream.sync(state, transformer=transformer)
    assert count == 2
    assert mock_write_record.call_count == 2


# IncrementalStream sync test

@patch("tap_teamwork.streams.abstracts.metrics.record_counter")
@patch("tap_teamwork.streams.abstracts.write_bookmark")
@patch("tap_teamwork.streams.abstracts.write_record")
@patch("tap_teamwork.streams.abstracts.Transformer")
def test_incremental_stream_sync(mock_transformer, mock_write_record, mock_write_bookmark, mock_counter, dummy_catalog, dummy_client):
    dummy_client.get.return_value = {
        "dummy_key": [{"id": "1", "updatedAt": "2025-01-01T00:00:00Z"}]
    }

    mock_counter_inst = MagicMock()
    mock_counter_inst.__enter__.return_value = mock_counter_inst
    mock_counter_inst.__exit__.return_value = False
    mock_counter_inst.value = 1
    mock_counter.return_value = mock_counter_inst

    stream = DummyIncrementalStream(client=dummy_client, catalog=dummy_catalog)
    stream.data_key = "dummy_key"
    stream.is_selected = MagicMock(return_value=True)

    transformer = MagicMock()
    transformer.transform.side_effect = lambda record, schema, metadata: record
    mock_transformer.return_value = transformer

    state = {}
    count = stream.sync(state, transformer=transformer)
    assert count == 1
    # Validate bookmark call args loosely
    assert mock_write_bookmark.call_count == 1
    args, _ = mock_write_bookmark.call_args
    assert args[0] is state
    assert args[1] == "dummy_incremental"
    assert args[2] == "updatedAt"
    assert args[3] is not None
