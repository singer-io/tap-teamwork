from typing import List, Optional, Dict
from tap_teamwork.streams.abstracts import IncrementalStream
from singer import get_logger

LOGGER = get_logger()

class Tasks(IncrementalStream):
    tap_stream_id = "tasks"
    path = "projects/api/v3/tasks.json"
    data_key = "tasks"
    replication_method = "INCREMENTAL"
    replication_keys: List[str] = ["updatedAt"]
    key_properties = ["id"]

    def get_url_params(self, context: Optional[Dict]) -> Dict:
        """Attach 'updatedAfter' for incremental sync."""
        params = {}
        bookmark = self.get_starting_timestamp(context)

        if bookmark:
            params["updatedAfter"] = bookmark
            LOGGER.info("[%s] Using incremental param: updatedAfter=%s", self.tap_stream_id, bookmark)
        else:
            LOGGER.info("[%s] No bookmark found — full sync.", self.tap_stream_id)

        return params
