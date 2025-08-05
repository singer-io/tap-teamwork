from base import teamworkBaseTest
from tap_tester.base_suite_tests.bookmark_test import BookmarkTest


class teamworkBookMarkTest(BookmarkTest, teamworkBaseTest):
    """Test tap sets a bookmark and respects it for the next sync of a
    stream."""
    bookmark_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    initial_bookmarks = {
        "bookmarks": {
        }
    }
    @staticmethod
    def name():
        return "tap_tester_teamwork_bookmark_test"

    def streams_to_test(self):
        streams_to_exclude = {}
        return self.expected_stream_names().difference(streams_to_exclude)
