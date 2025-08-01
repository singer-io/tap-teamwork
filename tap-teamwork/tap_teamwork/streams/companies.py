from typing import List, Optional, Dict
from tap_teamwork.streams.abstracts import IncrementalStream
from singer import get_logger

LOGGER = get_logger()

class Companies(IncrementalStream):
    tap_stream_id = "companies"
    path = "desk/v2/companies.json"
    data_key = "companies"
    replication_method = "INCREMENTAL"
    replication_keys: List[str] = ["updatedAt"]  # field for bookmarking
    key_properties = ["id"]

    def get_url_params(self, context: Optional[Dict]) -> Dict:
        """Pass 'updatedAfter' param to API if bookmark exists."""
        params = {}
        bookmark = self.get_starting_timestamp(context)

        if bookmark:
            params["updatedAfter"] = bookmark.isoformat()
            LOGGER.info(f"[{self.tap_stream_id}] Using incremental param: updatedAfter={params['updatedAfter']}")
        else:
            LOGGER.info(f"[{self.tap_stream_id}] No bookmark found — full sync.")

        return params
