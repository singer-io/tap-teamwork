from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import IncrementalStream

LOGGER = get_logger()

class Users(IncrementalStream):
    tap_stream_id = "users"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    replication_keys: List[str] = ["updatedAt"]
    data_key = "users"
    path = "desk/v1/users.json"
