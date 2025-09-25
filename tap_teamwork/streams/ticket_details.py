from typing import Dict, List, Optional, Any
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class TicketDetails(FullTableStream):
    tap_stream_id = "ticket_details"
    parent = "tickets"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    replication_keys: List[str] = []
    data_key = "ticket"
    path = "desk/v1/tickets/{ticketId}.json"

    # this child fetches by ticket id, irrespective of the parent's bookmark.
    ignore_parent_replication_keys = True

    def get_url_endpoint(self, parent_obj: Optional[Dict[str, Any]] = None) -> str:
        if not parent_obj:
            raise ValueError("Missing parent_obj for ticket_details stream")

        # allow either explicit context key or raw parent record id
        ticket_id = parent_obj.get("ticketId") or parent_obj.get("id")
        if not ticket_id:
            LOGGER.warning(
                "Skipping ticket_details due to missing ticket id in parent_obj: %s",
                parent_obj,
            )
            # let caller decide to skip this one
            raise ValueError("Missing 'ticketId' or 'id' in parent_obj")

        return self.client.build_url(f"desk/api/v2/tickets/{ticket_id}.json")

    def get_child_context(
        self,
        record: Dict[str, Any],
        context: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        return None
