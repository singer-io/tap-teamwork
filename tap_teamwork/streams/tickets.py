from typing import Dict, List, Optional
from singer import get_logger
from tap_teamwork.streams.abstracts import IncrementalStream

LOGGER = get_logger()

class Tickets(IncrementalStream):
    tap_stream_id = "tickets"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    replication_keys: List[str] = ["updatedAt"]
    data_key = "tickets"
    path = "desk/v2/tickets.json"
    children = ["ticket_details"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.child_to_sync: List[IncrementalStream] = []

    def get_url_params(self, context: Optional[Dict] = None, next_page_token: Optional[str] = None) -> Dict:
        params = super().get_url_params(context, next_page_token)
        start_date = self.get_starting_timestamp(context or {})
        if start_date:
            params["updatedAtFrom"] = start_date
        return params
