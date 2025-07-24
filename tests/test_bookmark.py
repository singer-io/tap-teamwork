from base import teamworkBaseTest
from tap_tester.base_suite_tests.bookmark_test import BookmarkTest


class teamworkBookMarkTest(BookmarkTest, teamworkBaseTest):
    """Test tap sets a bookmark and respects it for the next sync of a
    stream."""
    bookmark_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    initial_bookmarks = {
        "bookmarks": {
            "projects": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "tasks": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "taskcomments": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "timesheets": { "date" : "2020-01-01T00:00:00Z"},
            "milestones": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "tasklists": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "notebooks": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "notebooks_comments": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "dashboards": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "forms": { "updatedAt" : "2020-01-01T00:00:00Z"},
            "me_timers": { "updatedAt" : "2020-01-01T00:00:00Z"},
        }
    }
    @staticmethod
    def name():
        return "tap_tester_teamwork_bookmark_test"

    def streams_to_test(self):
        streams_to_exclude = {}
        return self.expected_stream_names().difference(streams_to_exclude)
