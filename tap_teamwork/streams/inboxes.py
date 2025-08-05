from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import IncrementalStream

LOGGER = get_logger()

class Inboxes(IncrementalStream):
    tap_stream_id = "inboxes"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    replication_keys: List[str] = ["updatedAt"]  # If different in future then replace with actual
    data_key = "inboxes"
    path = "desk/v1/inboxes.json"
