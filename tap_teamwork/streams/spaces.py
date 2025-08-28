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

    # including children that needs spaceId: collaborators, tags
    children: List[str] = ["collaborators", "tags"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.child_to_sync: List[IncrementalStream] = []

    def get_url_params(self, context: Optional[Dict]) -> Dict:
        params = {}
        bookmark = self.get_starting_timestamp(context)
        if bookmark:
            params["updatedAfter"] = bookmark.isoformat()
            LOGGER.info("[%s] Using incremental param: updatedAfter=%s", self.tap_stream_id, params["updatedAfter"])
        else:
            LOGGER.info("[%s] No bookmark found — full sync.", self.tap_stream_id)
        return params
