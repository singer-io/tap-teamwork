from typing import Dict, Iterator, List
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

    def get_url_params(
        self, context: Dict | None, next_page_token: str | None
    ) -> Dict:
        params = super().get_url_params(context, next_page_token)
        # Included updatedAtFrom parameter if available
        start_date = self.get_starting_timestamp(context)
        if start_date:
            params["updatedAtFrom"] = start_date.isoformat()
        return params
