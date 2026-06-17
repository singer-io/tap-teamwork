"""
Unit tests for discovery with stream access checking.

Covers:
- All streams accessible → full catalog
- Partial access (some 403s) → excluded streams
- Complete denial (all 403s) → teamworkForbiddenError raised
- Parent-child cascading exclusion
- Catalog structure validation
"""

import pytest
from unittest.mock import MagicMock, patch

from tap_teamwork.discover import _apply_access_checks, _prune_inaccessible_children, discover
from tap_teamwork.exceptions import teamworkForbiddenError


# ─── helpers ────────────────────────────────────────────────────────

def _make_client():
    """Return a mock client suitable for stream instantiation."""
    client = MagicMock()
    client.base_url = "https://test.teamwork.com"
    client.config = {"start_date": "2024-01-01T00:00:00Z", "api_key": "tok"}
    client.build_url.side_effect = lambda p: f"{client.base_url}/{p.lstrip('/')}"
    client.get.return_value = {}
    return client


def _schemas_and_metadata():
    """Return minimal schemas / field_metadata dicts keyed by every stream."""
    schemas = {name: {"type": "object", "properties": {"id": {"type": "string"}}} for name in STREAMS}
    field_metadata = {name: [] for name in STREAMS}
    return schemas, field_metadata


# ─── _apply_access_checks ──────────────────────────────────────────

class TestApplyAccessChecks:

    @patch("tap_teamwork.discover.STREAMS")
    def test_all_streams_accessible(self, mock_streams):
        """When every stream is accessible the catalog keeps all streams."""
        client = _make_client()

        # Build a mock STREAMS dict where every stream's check_access returns True
        mock_cls_a = MagicMock()
        mock_cls_a.return_value.check_access.return_value = True
        mock_cls_a.return_value.parent = ""
        mock_cls_b = MagicMock()
        mock_cls_b.return_value.check_access.return_value = True
        mock_cls_b.return_value.parent = ""

        mock_streams.items.return_value = [("stream_a", mock_cls_a), ("stream_b", mock_cls_b)]

        schemas = {"stream_a": {}, "stream_b": {}}
        fm = {"stream_a": [], "stream_b": []}

        _apply_access_checks(client, schemas, fm)

        assert "stream_a" in schemas
        assert "stream_b" in schemas

    @patch("tap_teamwork.discover.STREAMS")
    def test_partial_access_excludes_forbidden_streams(self, mock_streams):
        """Streams returning 403 are removed; others remain."""
        client = _make_client()

        accessible = MagicMock()
        accessible.return_value.check_access.return_value = True
        accessible.return_value.parent = ""
        forbidden = MagicMock()
        forbidden.return_value.check_access.return_value = False
        forbidden.return_value.parent = ""

        mock_streams.items.return_value = [
            ("projects", accessible),
            ("tasks", forbidden),
        ]

        schemas = {"projects": {}, "tasks": {}}
        fm = {"projects": [], "tasks": []}

        _apply_access_checks(client, schemas, fm)

        assert "projects" in schemas
        assert "tasks" not in schemas
        assert "tasks" not in fm

    @patch("tap_teamwork.discover.STREAMS")
    def test_all_streams_forbidden_raises(self, mock_streams):
        """If every parent stream is forbidden, a teamworkForbiddenError is raised."""
        client = _make_client()

        forbidden_a = MagicMock()
        forbidden_a.return_value.check_access.return_value = False
        forbidden_a.return_value.parent = ""
        forbidden_b = MagicMock()
        forbidden_b.return_value.check_access.return_value = False
        forbidden_b.return_value.parent = ""

        mock_streams.items.return_value = [
            ("stream_a", forbidden_a),
            ("stream_b", forbidden_b),
        ]

        schemas = {"stream_a": {}, "stream_b": {}}
        fm = {"stream_a": [], "stream_b": []}

        with pytest.raises(teamworkForbiddenError):
            _apply_access_checks(client, schemas, fm)


# ─── _prune_inaccessible_children ─────────────────────────────────

class TestPruneInaccessibleChildren:

    def test_child_removed_when_parent_missing(self):
        """Child streams are pruned when their parent is not in schemas."""
        schemas = {"ticket_details": {}, "projects": {}}
        fm = {"ticket_details": [], "projects": []}

        # tickets is not in schemas, so ticket_details (parent=tickets) should be removed
        _prune_inaccessible_children(schemas, fm)

        assert "ticket_details" not in schemas
        assert "ticket_details" not in fm
        assert "projects" in schemas

    def test_child_kept_when_parent_present(self):
        """Child streams are kept when their parent is in schemas."""
        schemas = {"tickets": {}, "ticket_details": {}}
        fm = {"tickets": [], "ticket_details": []}

        _prune_inaccessible_children(schemas, fm)

        assert "ticket_details" in schemas

    def test_multiple_children_of_same_parent_pruned(self):
        """All children of a missing parent are removed."""
        # spaces has two children: pages and collaborators
        schemas = {"projects": {}, "pages": {}, "collaborators": {}}
        fm = {"projects": [], "pages": [], "collaborators": []}

        # spaces is not in schemas → pages and collaborators should be pruned
        _prune_inaccessible_children(schemas, fm)

        assert "pages" not in schemas
        assert "collaborators" not in schemas
        assert "projects" in schemas


# ─── discover() integration ────────────────────────────────────────

class TestDiscover:

    @patch("tap_teamwork.discover._apply_access_checks")
    @patch("tap_teamwork.discover.get_schemas")
    def test_discover_returns_catalog(self, mock_get_schemas, mock_access):
        """discover() returns a Catalog with entries for every schema."""
        schemas = {
            "projects": {"type": "object", "properties": {"id": {"type": "string"}}},
        }
        fm = {
            "projects": [
                {"breadcrumb": (), "metadata": {"table-key-properties": ["id"]}},
            ],
        }
        mock_get_schemas.return_value = (schemas, fm)
        mock_access.return_value = None  # no-op

        client = _make_client()
        catalog = discover(client)

        assert len(catalog.streams) == 1
        assert catalog.streams[0].tap_stream_id == "projects"

    @patch("tap_teamwork.discover.get_schemas")
    def test_discover_calls_access_checks(self, mock_get_schemas):
        """discover() invokes _apply_access_checks with the client."""
        mock_get_schemas.return_value = ({}, {})
        client = _make_client()

        with patch("tap_teamwork.discover._apply_access_checks") as mock_ac:
            # Need at least one schema after access check to avoid error
            def keep_schemas(c, s, f):
                s["projects"] = {"type": "object", "properties": {"id": {"type": "string"}}}
                f["projects"] = [{"breadcrumb": (), "metadata": {"table-key-properties": ["id"]}}]
            mock_ac.side_effect = keep_schemas

            discover(client)
            mock_ac.assert_called_once()
            assert mock_ac.call_args[0][0] is client
