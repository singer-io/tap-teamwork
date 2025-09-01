from typing import List, Optional, Dict
from tap_teamwork.streams.abstracts import IncrementalStream
from singer import get_logger

LOGGER = get_logger()

class Projects(IncrementalStream):
    tap_stream_id = "projects"
    path = "projects/api/v3/projects.json"
    data_key = "projects"
    replication_method = "INCREMENTAL"
    replication_keys: List[str] = ["updatedAt"]
    key_properties = ["id"]

    def get_url_params(self, context: Optional[Dict]) -> Dict:
        """Pass 'updatedAfter' param to API if bookmark exists."""
        params = {}
        bookmark = self.get_starting_timestamp(context)

        if bookmark:
            # teamwork expects ISO 8601 format
            params["updatedAfter"] = bookmark.isoformat()
            LOGGER.info("[%s] Using incremental param: updatedAfter=%s", self.tap_stream_id, params["updatedAfter"])
        else:
            LOGGER.info("[%s] No bookmark found — full sync.", self.tap_stream_id)

        return params
