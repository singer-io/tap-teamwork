from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from singer import get_logger
from tap_teamwork.streams.abstracts import IncrementalStream

LOGGER = get_logger()

class TicketSearch(IncrementalStream):
    tap_stream_id = "ticket_search"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    replication_keys: List[str] = ["updatedAt"]
    data_key = "tickets"
    path = "desk/api/v2/search/tickets.json"

    def get_url_params(
        self, context: Optional[Dict[str, Any]], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Construct URL parameters for the API call including incremental filters."""
        params = super().get_url_params(context, next_page_token)

        # Add incremental sync filter using updatedAtFrom
        start_date: Optional[datetime] = self.get_starting_timestamp(context)
        if start_date:
            # Ensure proper UTC ISO-8601 format
            params["updatedAtFrom"] = (
                start_date.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            )
            params["orderBy"] = "updatedAt"
            params["orderMode"] = "asc"

        return params
