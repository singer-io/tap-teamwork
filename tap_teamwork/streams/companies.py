from typing import List, Optional, Dict
from tap_teamwork.streams.abstracts import IncrementalStream, BaseStream
from singer import get_logger

LOGGER = get_logger()

class Companies(IncrementalStream):
    tap_stream_id = "companies"
    path = "desk/api/v2/companies.json"
    data_key = "companies"
    replication_method = "INCREMENTAL"
    replication_keys: List[str] = ["updatedAt"]
    key_properties = ["id"]
    children: List[str] = ["company_details"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.child_to_sync: List[BaseStream] = []

    def get_url_params(self, context: Optional[Dict]) -> Dict:
        params = {}
        bookmark = self.get_starting_timestamp(context)
        if bookmark:
            params["updatedAfter"] = bookmark.isoformat()
            LOGGER.info("[%s] Using incremental param: updatedAfter=%s", self.tap_stream_id, params["updatedAfter"])
        else:
            LOGGER.info("[%s] No bookmark found — full sync.", self.tap_stream_id)
        return params
