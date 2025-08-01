from typing import List, Optional, Dict
from tap_teamwork.streams.abstracts import IncrementalStream
from singer import get_logger

LOGGER = get_logger()

class Tasks(IncrementalStream):
    tap_stream_id = "tasks"
    path = "tasks.json"
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
            LOGGER.info(f"[{self.tap_stream_id}] Using incremental param: updatedAfter={bookmark}")
        else:
            LOGGER.info(f"[{self.tap_stream_id}] No bookmark found then do full sync.")

        return params
