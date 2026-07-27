"""
Unit tests for ParentBaseStream bookmark behaviour and child stream
INCREMENTAL replication with parent's updatedAt propagation.

Covers:
- ParentBaseStream.get_bookmark returns min across parent and children
- ParentBaseStream.write_bookmark propagates to child streams
- Collaborators modify_object injects spaces_updatedAt from parent
- TicketDetails modify_object injects tickets_updatedAt from parent
- Pages sync injects spaces_updatedAt from parent
- CompanyDetails sync injects companies_updatedAt from parent
- Child streams have correct replication_method and replication_keys
"""

import unittest
from unittest.mock import MagicMock, patch

from tap_teamwork.streams.abstracts import ParentBaseStream


# ---- Helpers ----

def make_mock_client(config=None):
    client = MagicMock()
    client.config = config or {"start_date": "2026-01-01T00:00:00Z"}
    client.base_url = "https://example.com"
    client.build_url.side_effect = lambda path: f"https://example.com/{path.lstrip('/')}"
    return client


def make_mock_catalog_entry():
    mock_catalog = MagicMock()
    mock_catalog.schema.to_dict.return_value = {
        "type": "object",
        "properties": {"id": {"type": "integer"}}
    }
    mock_catalog.metadata = []
    return mock_catalog


# ---- ParentBaseStream Bookmark Tests ----

class TestParentBaseStreamBookmark(unittest.TestCase):
    """Tests for ParentBaseStream bookmark behaviour."""

    def _make_spaces_with_children(self, config=None):
        from tap_teamwork.streams.spaces import Spaces
        from tap_teamwork.streams.collaborators import Collaborators
        from tap_teamwork.streams.pages import Pages

        if config is None:
            config = {"start_date": "2026-01-01T00:00:00Z"}
        client = make_mock_client(config)
        stream = Spaces(client=client, catalog=make_mock_catalog_entry())
        collaborators = Collaborators(client=client, catalog=make_mock_catalog_entry())
        pages = Pages(client=client, catalog=make_mock_catalog_entry())
        stream.child_to_sync = [collaborators, pages]
        return stream, collaborators, pages

    def _make_tickets_with_children(self, config=None):
        from tap_teamwork.streams.tickets import Tickets
        from tap_teamwork.streams.ticket_details import TicketDetails

        if config is None:
            config = {"start_date": "2026-01-01T00:00:00Z"}
        client = make_mock_client(config)
        stream = Tickets(client=client, catalog=make_mock_catalog_entry())
        details = TicketDetails(client=client, catalog=make_mock_catalog_entry())
        stream.child_to_sync = [details]
        return stream, details

    def _make_companies_with_children(self, config=None):
        from tap_teamwork.streams.companies import Companies
        from tap_teamwork.streams.company_details import CompanyDetails

        if config is None:
            config = {"start_date": "2026-01-01T00:00:00Z"}
        client = make_mock_client(config)
        stream = Companies(client=client, catalog=make_mock_catalog_entry())
        details = CompanyDetails(client=client, catalog=make_mock_catalog_entry())
        stream.child_to_sync = [details]
        return stream, details

    def test_spaces_extends_parent_base_stream(self):
        from tap_teamwork.streams.spaces import Spaces
        self.assertTrue(issubclass(Spaces, ParentBaseStream))

    def test_tickets_extends_parent_base_stream(self):
        from tap_teamwork.streams.tickets import Tickets
        self.assertTrue(issubclass(Tickets, ParentBaseStream))

    def test_companies_extends_parent_base_stream(self):
        from tap_teamwork.streams.companies import Companies
        self.assertTrue(issubclass(Companies, ParentBaseStream))

    def test_get_bookmark_returns_min_across_parent_and_children(self):
        """When children have an older bookmark, parent must re-process from children's date."""
        state = {
            "bookmarks": {
                "spaces": {"updatedAt": "2026-06-01T00:00:00Z"},
                "collaborators": {"spaces_updatedAt": "2026-03-01T00:00:00Z"},
                "pages": {"spaces_updatedAt": "2026-05-01T00:00:00Z"},
            }
        }
        stream, _, _ = self._make_spaces_with_children()
        bookmark = stream.get_bookmark(state, "spaces")
        self.assertEqual(bookmark, "2026-03-01T00:00:00Z")

    def test_get_bookmark_falls_back_to_start_date_when_no_state(self):
        stream, _, _ = self._make_spaces_with_children()
        bookmark = stream.get_bookmark({}, "spaces")
        self.assertEqual(bookmark, "2026-01-01T00:00:00Z")

    def test_get_bookmark_uses_parent_when_parent_is_oldest(self):
        """When parent has the oldest bookmark, it should be returned."""
        state = {
            "bookmarks": {
                "spaces": {"updatedAt": "2026-02-01T00:00:00Z"},
                "collaborators": {"spaces_updatedAt": "2026-05-01T00:00:00Z"},
                "pages": {"spaces_updatedAt": "2026-06-01T00:00:00Z"},
            }
        }
        stream, _, _ = self._make_spaces_with_children()
        with patch.object(stream, "is_selected", return_value=True):
            bookmark = stream.get_bookmark(state, "spaces")
        self.assertEqual(bookmark, "2026-02-01T00:00:00Z")

    def test_write_bookmark_propagates_to_children(self):
        """Children's bookmarks must be stored under '{parent}_updatedAt'."""
        state = {"bookmarks": {}}
        stream, _, _ = self._make_spaces_with_children()
        stream.write_bookmark(state, "spaces", key="updatedAt", value="2026-07-01T00:00:00Z")
        self.assertEqual(
            state["bookmarks"]["collaborators"]["spaces_updatedAt"],
            "2026-07-01T00:00:00.000000Z"
        )
        self.assertEqual(
            state["bookmarks"]["pages"]["spaces_updatedAt"],
            "2026-07-01T00:00:00.000000Z"
        )

    def test_write_bookmark_propagates_to_ticket_details(self):
        state = {"bookmarks": {}}
        stream, _ = self._make_tickets_with_children()
        stream.write_bookmark(state, "tickets", key="updatedAt", value="2026-07-15T00:00:00Z")
        self.assertEqual(
            state["bookmarks"]["ticket_details"]["tickets_updatedAt"],
            "2026-07-15T00:00:00.000000Z"
        )

    def test_write_bookmark_propagates_to_company_details(self):
        state = {"bookmarks": {}}
        stream, _ = self._make_companies_with_children()
        stream.write_bookmark(state, "companies", key="updatedAt", value="2026-07-20T00:00:00Z")
        self.assertEqual(
            state["bookmarks"]["company_details"]["companies_updatedAt"],
            "2026-07-20T00:00:00.000000Z"
        )

    def test_write_bookmark_writes_parent_when_selected(self):
        state = {"bookmarks": {}}
        stream, _, _ = self._make_spaces_with_children()
        with patch.object(stream, "is_selected", return_value=True):
            stream.write_bookmark(state, "spaces", key="updatedAt", value="2026-07-01T00:00:00Z")
        self.assertIn("spaces", state["bookmarks"])
        self.assertIn("updatedAt", state["bookmarks"]["spaces"])


# ---- Child Stream Attribute Tests ----

class TestCollaboratorsStream(unittest.TestCase):
    """Tests for Collaborators stream — INCREMENTAL with spaces_updatedAt from parent."""

    def _make_stream(self):
        from tap_teamwork.streams.collaborators import Collaborators
        client = make_mock_client()
        return Collaborators(client=client, catalog=make_mock_catalog_entry())

    def test_collaborators_replication_method_is_incremental(self):
        stream = self._make_stream()
        self.assertEqual(stream.replication_method, "INCREMENTAL")

    def test_collaborators_replication_key_is_spaces_updatedAt(self):
        stream = self._make_stream()
        self.assertEqual(stream.replication_keys, ["spaces_updatedAt"])

    def test_modify_object_sets_spaces_updatedAt_from_parent(self):
        stream = self._make_stream()
        parent = {"id": 100, "updatedAt": "2026-03-01T10:00:00Z"}
        record = {"id": 616263, "type": "users"}
        result = stream.modify_object(record, parent)
        self.assertEqual(result["spaces_updatedAt"], "2026-03-01T10:00:00Z")

    def test_modify_object_no_parent_returns_record_unchanged(self):
        stream = self._make_stream()
        record = {"id": 616263, "type": "users"}
        result = stream.modify_object(record, None)
        self.assertNotIn("spaces_updatedAt", result)


class TestPagesStream(unittest.TestCase):
    """Tests for Pages stream — INCREMENTAL with spaces_updatedAt from parent."""

    def _make_stream(self):
        from tap_teamwork.streams.pages import Pages
        client = make_mock_client()
        return Pages(client=client, catalog=make_mock_catalog_entry())

    def test_pages_replication_method_is_incremental(self):
        stream = self._make_stream()
        self.assertEqual(stream.replication_method, "INCREMENTAL")

    def test_pages_replication_key_is_spaces_updatedAt(self):
        stream = self._make_stream()
        self.assertEqual(stream.replication_keys, ["spaces_updatedAt"])

    @patch("singer.write_record")
    @patch("singer.metrics.record_counter")
    def test_sync_injects_spaces_updatedAt(self, mock_counter, mock_write_record):
        """Pages sync should inject parent's updatedAt into each page record."""
        from tap_teamwork.streams.pages import Pages

        mock_counter_inst = MagicMock()
        mock_counter_inst.__enter__ = MagicMock(return_value=mock_counter_inst)
        mock_counter_inst.__exit__ = MagicMock(return_value=False)
        mock_counter.return_value = mock_counter_inst

        client = make_mock_client()
        # First call: list pages tree; Second call: fetch page detail
        client.get.side_effect = [
            {"pages": {"id": 1, "childPages": []}},
            {"page": {"id": 1, "title": "Test Page", "updatedAt": "2026-01-15T00:00:00Z"}},
        ]
        stream = Pages(client=client, catalog=make_mock_catalog_entry())
        stream.schema = {"type": "object", "properties": {}}
        stream.metadata = {}

        transformer = MagicMock()
        transformer.transform.side_effect = lambda r, s, m: r

        with patch.object(stream, "is_selected", return_value=True):
            parent_obj = {"id": 42, "updatedAt": "2026-06-01T00:00:00Z"}
            stream.sync(state={}, transformer=transformer, parent_obj=parent_obj)

        # Check that transform was called with record containing spaces_updatedAt
        call_args = transformer.transform.call_args[0][0]
        self.assertEqual(call_args["spaces_updatedAt"], "2026-06-01T00:00:00Z")


class TestTicketDetailsStream(unittest.TestCase):
    """Tests for TicketDetails stream — INCREMENTAL with tickets_updatedAt from parent."""

    def _make_stream(self):
        from tap_teamwork.streams.ticket_details import TicketDetails
        client = make_mock_client()
        return TicketDetails(client=client, catalog=make_mock_catalog_entry())

    def test_ticket_details_replication_method_is_incremental(self):
        stream = self._make_stream()
        self.assertEqual(stream.replication_method, "INCREMENTAL")

    def test_ticket_details_replication_key_is_tickets_updatedAt(self):
        stream = self._make_stream()
        self.assertEqual(stream.replication_keys, ["tickets_updatedAt"])

    def test_modify_object_sets_tickets_updatedAt_from_parent(self):
        stream = self._make_stream()
        parent = {"id": 55, "updatedAt": "2026-05-10T08:00:00Z"}
        record = {"id": 1, "subject": "Test ticket"}
        result = stream.modify_object(record, parent)
        self.assertEqual(result["tickets_updatedAt"], "2026-05-10T08:00:00Z")

    def test_modify_object_no_parent_returns_record_unchanged(self):
        stream = self._make_stream()
        record = {"id": 1, "subject": "Test ticket"}
        result = stream.modify_object(record, None)
        self.assertNotIn("tickets_updatedAt", result)


class TestCompanyDetailsStream(unittest.TestCase):
    """Tests for CompanyDetails stream — INCREMENTAL with companies_updatedAt from parent."""

    def _make_stream(self):
        from tap_teamwork.streams.company_details import CompanyDetails
        client = make_mock_client()
        return CompanyDetails(client=client, catalog=make_mock_catalog_entry())

    def test_company_details_replication_method_is_incremental(self):
        stream = self._make_stream()
        self.assertEqual(stream.replication_method, "INCREMENTAL")

    def test_company_details_replication_key_is_companies_updatedAt(self):
        stream = self._make_stream()
        self.assertEqual(stream.replication_keys, ["companies_updatedAt"])

    @patch("tap_teamwork.streams.company_details.singer.write_record")
    @patch("tap_teamwork.streams.company_details.metrics.record_counter")
    def test_sync_injects_companies_updatedAt(self, mock_counter, mock_write_record):
        """CompanyDetails sync should inject parent's updatedAt into the record."""
        from tap_teamwork.streams.company_details import CompanyDetails

        mock_counter_inst = MagicMock()
        mock_counter_inst.__enter__ = MagicMock(return_value=mock_counter_inst)
        mock_counter_inst.__exit__ = MagicMock(return_value=False)
        mock_counter_inst.value = 1
        mock_counter.return_value = mock_counter_inst

        client = make_mock_client()
        client.get.return_value = {"company": {"id": 10, "name": "Acme"}}
        stream = CompanyDetails(client=client, catalog=make_mock_catalog_entry())
        stream.schema = {"type": "object", "properties": {}}
        stream.metadata = {}

        transformer = MagicMock()
        transformer.transform.side_effect = lambda r, s, m: r

        parent_obj = {"id": 10, "updatedAt": "2026-07-20T12:00:00Z"}
        stream.sync(state={}, transformer=transformer, parent_obj=parent_obj)

        # Verify the record passed to transform includes companies_updatedAt
        call_args = transformer.transform.call_args[0][0]
        self.assertEqual(call_args["companies_updatedAt"], "2026-07-20T12:00:00Z")


if __name__ == "__main__":
    unittest.main()
