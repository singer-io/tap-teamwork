from base import teamworkBaseTest
from tap_tester.base_suite_tests.bookmark_test import BookmarkTest

class teamworkBookMarkTest(BookmarkTest, teamworkBaseTest):
    """Bookmark suite scoped to a stable incremental stream."""

    # Format of the bookmark timestamps
    bookmark_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    # Seeded initial state (empty is fine, avoids abstract error)
    initial_bookmarks = {
        "bookmarks": {
            "tasks": {"updatedAt": "2025-01-01T00:00:00Z"},
        }
    }

    @staticmethod
    def name():
        return "tap_tester_teamwork_bookmark_test"

    def streams_to_test(self):
        # Use a safe incremental stream with replication key
        return {"tasks"}
