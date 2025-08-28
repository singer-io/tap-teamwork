from typing import List, Optional, Dict
from tap_teamwork.streams.abstracts import IncrementalStream
from singer import get_logger

LOGGER = get_logger()

class Notebooks(IncrementalStream):
    tap_stream_id = "notebooks"
    path = "projects/api/v3/notebooks.json"
    data_key = "notebooks"
    replication_method = "INCREMENTAL"
    replication_keys: List[str] = ["updatedAt"]
    key_properties = ["id"]

    def get_url_params(self, context: Optional[Dict]) -> Dict:
        params = {}
        bookmark = self.get_starting_timestamp(context)
        if bookmark:
            params["updatedAfter"] = bookmark.isoformat()
            LOGGER.info("[%s] Using incremental param: updatedAfter=%s", self.tap_stream_id, params["updatedAfter"])
        else:
            LOGGER.info("[%s] No bookmark found — full sync.", self.tap_stream_id)
        return params
