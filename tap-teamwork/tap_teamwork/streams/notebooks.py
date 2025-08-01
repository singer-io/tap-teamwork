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
            LOGGER.info(f"[{self.tap_stream_id}] Using incremental param: updatedAfter={params['updatedAfter']}")
        else:
            LOGGER.info(f"[{self.tap_stream_id}] No bookmark found then full sync.")
        return params
