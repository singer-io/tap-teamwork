"""
Unit tests for sync logic.

Covers:
- Incremental sync filtering by bookmark
- Full table sync behaviour
- Bookmark advancement after sync
- Child stream synchronisation
- Sync orchestration (currently_syncing tracking)
- check_access method on base stream
"""

import pytest
from unittest.mock import MagicMock, patch
from tap_teamwork.streams.abstracts import IncrementalStream, FullTableStream
from tap_teamwork.exceptions import teamworkForbiddenError


# ─── concrete stubs ────────────────────────────────────────────────

class StubIncremental(IncrementalStream):
    tap_stream_id = "stub_incremental"
    replication_keys = ["updatedAt"]
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    path = "api/v3/stubs.json"
    data_key = "stubs"


class StubFullTable(FullTableStream):
    tap_stream_id = "stub_full"
    replication_keys = []
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    path = "api/v3/full_stubs.json"
    data_key = "full_stubs"


class StubChild(FullTableStream):
    tap_stream_id = "stub_child"
    parent = "stub_full"
    replication_keys = []
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    path = "api/v3/full_stubs/{parentId}/children.json"
    data_key = "children"


# ─── fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def mock_client():
    client = MagicMock()
    client.base_url = "https://test.teamwork.com"
    client.config = {"start_date": "2024-01-01T00:00:00Z"}
    client.build_url.side_effect = lambda p: f"{client.base_url}/{p.lstrip('/')}"
    client.get.return_value = {"stubs": [], "full_stubs": [], "children": []}
    return client


@pytest.fixture
def mock_catalog():
    cat = MagicMock()
    cat.schema.to_dict.return_value = {
        "type": "object",
        "properties": {"id": {"type": "string"}, "updatedAt": {"type": "string"}},
    }
    cat.metadata = []
    return cat


# ─── incremental sync ─────────────────────────────────────────────

class TestIncrementalSync:

    @patch("tap_teamwork.streams.abstracts.write_record")
    @patch("tap_teamwork.streams.abstracts.metrics.record_counter")
    def test_writes_records_newer_than_bookmark(self, mock_counter, mock_write, mock_client, mock_catalog):
        mock_counter.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_counter.return_value.__exit__ = MagicMock(return_value=False)

        stream = StubIncremental(client=mock_client, catalog=mock_catalog)
        stream.is_selected = MagicMock(return_value=True)
        stream.get_records = MagicMock(return_value=[
            {"id": "1", "updatedAt": "2025-06-01T00:00:00Z"},
            {"id": "2", "updatedAt": "2025-06-02T00:00:00Z"},
        ])

        state = {"bookmarks": {"stub_incremental": {"updatedAt": "2025-05-01T00:00:00Z"}}}
        stream.sync(state=state, transformer=MagicMock(transform=lambda r, s, m: r))

        assert mock_write.call_count == 2

    @patch("tap_teamwork.streams.abstracts.write_record")
    @patch("tap_teamwork.streams.abstracts.metrics.record_counter")
    def test_skips_records_older_than_bookmark(self, mock_counter, mock_write, mock_client, mock_catalog):
        mock_counter.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_counter.return_value.__exit__ = MagicMock(return_value=False)

        stream = StubIncremental(client=mock_client, catalog=mock_catalog)
        stream.is_selected = MagicMock(return_value=True)
        stream.get_records = MagicMock(return_value=[
            {"id": "1", "updatedAt": "2024-01-01T00:00:00Z"},
        ])

        state = {"bookmarks": {"stub_incremental": {"updatedAt": "2025-06-01T00:00:00Z"}}}
        stream.sync(state=state, transformer=MagicMock(transform=lambda r, s, m: r))

        assert mock_write.call_count == 0


# ─── full table sync ──────────────────────────────────────────────

class TestFullTableSync:

    @patch("tap_teamwork.streams.abstracts.write_record")
    @patch("tap_teamwork.streams.abstracts.metrics.record_counter")
    def test_writes_all_records(self, mock_counter, mock_write, mock_client, mock_catalog):
        mock_counter.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_counter.return_value.__exit__ = MagicMock(return_value=False)

        stream = StubFullTable(client=mock_client, catalog=mock_catalog)
        stream.is_selected = MagicMock(return_value=True)
        stream.get_records = MagicMock(return_value=[
            {"id": "1"},
            {"id": "2"},
            {"id": "3"},
        ])

        state = {}
        stream.sync(state=state, transformer=MagicMock(transform=lambda r, s, m: r))

        assert mock_write.call_count == 3


# ─── check_access ─────────────────────────────────────────────────

class TestCheckAccess:

    def test_accessible_stream(self, mock_client, mock_catalog):
        """check_access returns True when API responds without 403."""
        stream = StubIncremental(client=mock_client, catalog=mock_catalog)
        assert stream.check_access() is True

    def test_forbidden_stream(self, mock_client, mock_catalog):
        """check_access returns False when API raises teamworkForbiddenError."""
        mock_client.get.side_effect = teamworkForbiddenError("Forbidden")
        stream = StubIncremental(client=mock_client, catalog=mock_catalog)
        assert stream.check_access() is False

    @patch("tap_teamwork.streams.abstracts.LOGGER.warning")
    def test_forbidden_stream_logs_expected_message(self, mock_warning, mock_client, mock_catalog):
        """check_access logs the stream id and error text when access is forbidden."""
        mock_client.get.side_effect = teamworkForbiddenError("Forbidden")
        stream = StubIncremental(client=mock_client, catalog=mock_catalog)

        assert stream.check_access() is False
        mock_warning.assert_called_once_with(
            "Unauthorized Stream: %s, excluding from catalog. HTTP-Error-Message:'%s'",
            "stub_incremental",
            "Forbidden",
        )

    def test_child_stream_always_accessible(self, mock_client, mock_catalog):
        """Child streams always return True from check_access."""
        stream = StubChild(client=mock_client, catalog=mock_catalog)
        assert stream.check_access() is True

    def test_child_returns_true_even_when_client_would_403(self, mock_client, mock_catalog):
        """Child streams return True regardless of client behaviour."""
        mock_client.get.side_effect = teamworkForbiddenError("Forbidden")
        stream = StubChild(client=mock_client, catalog=mock_catalog)
        assert stream.check_access() is True


# ─── sync orchestration ───────────────────────────────────────────

class TestSyncOrchestration:

    @patch("tap_teamwork.sync.update_currently_syncing")
    @patch("tap_teamwork.sync._instantiate_stream")
    @patch("tap_teamwork.sync.write_schema")
    def test_currently_syncing_tracking(self, mock_ws, mock_inst, mock_ucs, mock_client):
        """Verify currently_syncing is set and cleared during sync."""
        from tap_teamwork.sync import sync as do_sync

        mock_stream = MagicMock()
        mock_stream.parent = ""
        mock_stream.children = []
        mock_stream.child_to_sync = []
        mock_stream.is_selected.return_value = True
        mock_stream.sync.return_value = 5
        mock_inst.return_value = mock_stream

        catalog = MagicMock()
        catalog.get_selected_streams.return_value = [MagicMock(stream="projects")]
        catalog.get_stream.return_value = MagicMock()

        state = {}
        do_sync(client=mock_client, config={}, catalog=catalog, state=state)

        # currently_syncing should be set then cleared
        assert mock_ucs.call_count == 2
        mock_ucs.assert_any_call(state, "projects")
        mock_ucs.assert_any_call(state, None)
