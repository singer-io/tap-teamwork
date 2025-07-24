from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_teamwork.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class Taskcomments(IncrementalStream):
    tap_stream_id = "taskcomments"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["updatedAt"]
    data_key = "comments"
    path = "tasks/{taskId}/comments"
    parent = "tasks"
    bookmark_value = None

    def get_bookmark(self, state: Dict, key: Any = None) -> int:
        """
        Return initial bookmark value only for the child stream.
        """
        if not self.bookmark_value:        
            self.bookmark_value = super().get_bookmark(state, key)

        return self.bookmark_value
