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
            # Teamwork expects ISO 8601 format
            params["updatedAfter"] = bookmark.isoformat()
            LOGGER.info(f"[{self.tap_stream_id}] Using incremental param: updatedAfter={params['updatedAfter']}")
        else:
            LOGGER.info(f"[{self.tap_stream_id}] No bookmark found — full sync.")

        return params
