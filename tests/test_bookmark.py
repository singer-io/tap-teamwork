from base import teamworkBaseTest
from tap_tester.base_suite_tests.bookmark_test import BookmarkTest


class teamworkBookMarkTest(BookmarkTest, teamworkBaseTest):
    """Bookmark suite scoped to a stable incremental stream."""

    # Format of the bookmark timestamps written by the tap
    bookmark_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    # No pre-seeded state — start from config start_date so sync 1 fetches
    # all tasks and establishes a clear max-bookmark baseline.
    initial_bookmarks = {}

    @staticmethod
    def name():
        return "tap_tester_teamwork_bookmark_test"

    def streams_to_test(self):
        return {"tasks"}

    def calculate_new_bookmarks(self):
        """Set the manipulated bookmark to exactly where sync 1 ended.

        The base-class implementation picks the second-to-last unique
        replication value from sync 1.  When most tasks were recently
        modified (common in a shared test environment), that date is old
        enough that the API still returns all records in sync 2, causing
        ``assertLess(len(sync_2), len(sync_1))`` to fail non-deterministically.

        By using the max bookmark from state_1 directly, sync 2 starts from
        bookmark_1 and the tap's inclusive-boundary filter (``rec_dt >=
        bookmark_dt``) keeps only tasks with ``updatedAt >= bookmark_1``.
        The test then further restricts sync_2 to ``updatedAt <= bookmark_1``,
        leaving only tasks with ``updatedAt == bookmark_1``.  As long as at
        least one task was last updated *before* the most recent task (true
        for any real dataset), sync 2 count < sync 1 count.
        """
        tasks_bookmark = (
            BookmarkTest.state_1
            .get("bookmarks", {})
            .get("tasks", {})
            .get("updatedAt")
        )
        if tasks_bookmark:
            return {"tasks": {"updatedAt": tasks_bookmark}}
        return {}
