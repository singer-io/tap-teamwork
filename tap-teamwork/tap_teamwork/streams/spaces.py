from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()

class Spaces(FullTableStream):
    tap_stream_id = "spaces"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    replication_keys: List[str] = []
    data_key = "spaces"
    path = "spaces/api/v3/spaces.json"
