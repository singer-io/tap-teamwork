from typing import List, Optional, Dict
from tap_teamwork.streams.abstracts import IncrementalStream
from singer import get_logger

LOGGER = get_logger()

class Spaces(IncrementalStream):
    tap_stream_id = "spaces"
    path = "spaces/api/v1/spaces.json"
    data_key = "spaces"
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
            LOGGER.info(f"[{self.tap_stream_id}] No bookmark found then do full sync.")
        return params
