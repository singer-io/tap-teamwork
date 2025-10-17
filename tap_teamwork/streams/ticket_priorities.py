from typing import List
from singer import get_logger
from tap_teamwork.streams.abstracts import IncrementalStream

LOGGER = get_logger()

class TicketPriorities(IncrementalStream):
    tap_stream_id = "ticket_priorities"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    replication_keys: List[str] = ["updatedAt"]
    data_key = "priorities"
    path = "desk/api/v2/ticketpriorities.json"
