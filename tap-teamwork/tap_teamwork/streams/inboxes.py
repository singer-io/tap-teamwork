from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()

class Inboxes(FullTableStream):
    tap_stream_id = "inboxes"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    replication_keys: List[str] = []
    data_key = "inboxes"
    path = "desk/v1/inboxes.json" 
