"""
Unit tests for bookmark read/write helpers in IncrementalStream.

Covers:
- Reading bookmarks (existing, fallback to start_date)
- Writing bookmarks (advancement, non-regression)
- _parse_utc / _fmt round-trip
"""

import pytest
from unittest.mock import MagicMock
from tap_teamwork.streams.abstracts import IncrementalStream


# ─── Concrete test stream ──────────────────────────────────────────

class StubIncremental(IncrementalStream):
    tap_stream_id = "stub_incremental"
    replication_keys = ["updatedAt"]
    key_properties = ["id"]
    replication_method = "INCREMENTAL"


@pytest.fixture
def client():
    c = MagicMock()
    c.config = {"start_date": "2024-01-01T00:00:00Z"}
    c.base_url = "https://test.teamwork.com"
    c.build_url.side_effect = lambda p: f"{c.base_url}/{p.lstrip('/')}"
    return c


@pytest.fixture
def catalog():
    cat = MagicMock()
    cat.schema.to_dict.return_value = {"type": "object", "properties": {"id": {"type": "string"}}}
    cat.metadata = []
    return cat


@pytest.fixture
def stream(client, catalog):
    return StubIncremental(client=client, catalog=catalog)


# ─── get_bookmark ──────────────────────────────────────────────────

class TestGetBookmark:

    def test_existing_bookmark_returned(self, stream):
        state = {"bookmarks": {"stub_incremental": {"updatedAt": "2025-06-01T00:00:00Z"}}}
        result = stream.get_bookmark(state, "stub_incremental")
        assert result == "2025-06-01T00:00:00Z"

    def test_fallback_to_start_date(self, stream):
        state = {}
        result = stream.get_bookmark(state, "stub_incremental")
        assert result == "2024-01-01T00:00:00Z"

    def test_custom_key(self, stream):
        state = {"bookmarks": {"stub_incremental": {"custom_key": "2025-03-01T00:00:00Z"}}}
        result = stream.get_bookmark(state, "stub_incremental", key="custom_key")
        assert result == "2025-03-01T00:00:00Z"


# ─── write_bookmark ────────────────────────────────────────────────

class TestWriteBookmark:

    def test_advances_bookmark(self, stream):
        state = {"bookmarks": {"stub_incremental": {"updatedAt": "2024-06-01T00:00:00Z"}}}
        result = stream.write_bookmark(state, "stub_incremental", value="2025-01-01T00:00:00Z")
        assert result["bookmarks"]["stub_incremental"]["updatedAt"] >= "2025-01-01"

    def test_does_not_regress(self, stream):
        state = {"bookmarks": {"stub_incremental": {"updatedAt": "2025-06-01T00:00:00Z"}}}
        result = stream.write_bookmark(state, "stub_incremental", value="2024-01-01T00:00:00Z")
        assert result["bookmarks"]["stub_incremental"]["updatedAt"] >= "2025-06-01"

    def test_new_bookmark_written(self, stream):
        state = {}
        result = stream.write_bookmark(state, "stub_incremental", value="2025-03-15T12:00:00Z")
        assert "bookmarks" in result
        assert "stub_incremental" in result["bookmarks"]


# ─── _parse_utc ────────────────────────────────────────────────────

class TestParseUtc:

    def test_valid_iso_string(self, stream):
        dt = stream._parse_utc("2025-06-01T12:00:00Z")
        assert dt is not None

    def test_none_returns_none(self, stream):
        assert stream._parse_utc(None) is None

    def test_empty_string_returns_none(self, stream):
        assert stream._parse_utc("") is None

    def test_null_string_returns_none(self, stream):
        assert stream._parse_utc("null") is None


# ─── _minus_one_second_str ─────────────────────────────────────────

class TestMinusOneSecond:

    def test_subtracts_one_second(self, stream):
        result = stream._minus_one_second_str("2025-06-01T00:00:01Z")
        assert result is not None
        assert "2025-06-01T00:00:00" in result

    def test_invalid_returns_none(self, stream):
        assert stream._minus_one_second_str("not-a-date") is None
