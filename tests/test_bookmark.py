from base import teamworkBaseTest
from tap_tester.base_suite_tests.bookmark_test import BookmarkTest

class teamworkBookMarkTest(BookmarkTest, teamworkBaseTest):
    """Bookmark suite for all incremental streams with sufficient data."""

    # Format of the bookmark timestamps
    bookmark_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    # Seeded initial state for all testable incremental streams
    initial_bookmarks = {
        "bookmarks": {
            "projects": {"updatedAt": "2025-01-01T00:00:00Z"},
            "tasks": {"updatedAt": "2025-01-01T00:00:00Z"},
            "milestones": {"lastChangedOn": "2025-01-01T00:00:00Z"},
            "notebooks": {"updatedAt": "2025-01-01T00:00:00Z"},
            "spaces": {"updatedAt": "2025-01-01T00:00:00Z"},
            "space_tags": {"updatedAt": "2025-01-01T00:00:00Z"},
        }
    }

    @staticmethod
    def name():
        return "tap_tester_teamwork_bookmark_test"

    def streams_to_test(self):
        # Incremental streams with >= 2 unique replication key values in test account.
        # Other incremental streams excluded due to insufficient data variance.
        return {
            "projects", "tasks", "milestones", "notebooks", "spaces",
            "space_tags",
        }
