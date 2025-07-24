from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_teamwork.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class Tasklists(IncrementalStream):
    tap_stream_id = "tasklists"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["updatedAt"]
    data_key = "tasklists"
    path = "tasklists"
