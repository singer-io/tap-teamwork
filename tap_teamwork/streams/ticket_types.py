from typing import List
from singer import get_logger
from tap_teamwork.streams.abstracts import IncrementalStream

LOGGER = get_logger()

class TicketTypes(IncrementalStream):
    tap_stream_id = "ticket_types"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    replication_keys: List[str] = ["updatedAt"]
    data_key = "types"
    path = "desk/api/v2/tickettypes.json"
