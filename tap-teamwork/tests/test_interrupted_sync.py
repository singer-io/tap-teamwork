
from base import teamworkBaseTest
from tap_tester.base_suite_tests.interrupted_sync_test import InterruptedSyncTest


class teamworkInterruptedSyncTest(teamworkBaseTest):
    """Test tap sets a bookmark and respects it for the next sync of a
    stream."""

    @staticmethod
    def name():
        return "tap_tester_teamwork_interrupted_sync_test"

    def streams_to_test(self):
        return self.expected_stream_names()


    def manipulate_state(self):
        return {
            "currently_syncing": "prospects",
            "bookmarks": {
        }
    }