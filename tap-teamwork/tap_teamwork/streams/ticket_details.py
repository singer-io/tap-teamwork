from typing import Dict, List, Optional, Any
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream
from tap_teamwork.streams.tickets import Tickets  # Parent class

LOGGER = get_logger()

class TicketDetails(FullTableStream):
    tap_stream_id = "ticket_details"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    replication_keys: List[str] = []
    data_key = "ticket"
    path = "desk/v1/tickets/{ticketId}.json"

    parent_stream_type = Tickets
    ignore_parent_replication_keys = True

    def get_child_context(self, record: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        ticket_id = record.get("id")
        if not ticket_id:
            LOGGER.warning(f"[ticket_details] Skipping due to missing ticket ID in record: {record}")
            return None
        return {"ticketId": ticket_id}
