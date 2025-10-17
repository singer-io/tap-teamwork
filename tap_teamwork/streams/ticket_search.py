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
        start = self.get_starting_timestamp(context)  # may be datetime, str, or None
        if start:
            # Normalize to ISO-8601 UTC if datetime; pass through if already a string
            if isinstance(start, datetime):
                if start.tzinfo is None:
                    start = start.replace(tzinfo=timezone.utc)
                else:
                    start = start.astimezone(timezone.utc)
                start_iso = start.isoformat()
            else:
                start_iso = str(start)

            # Normalize trailing timezone to 'Z' if explicitly UTC
            if start_iso.endswith("+00:00"):
                start_iso = start_iso[:-6] + "Z"

            params["updatedAtFrom"] = start_iso
            params["orderBy"] = "updatedAt"
            params["orderMode"] = "asc"

        return params
