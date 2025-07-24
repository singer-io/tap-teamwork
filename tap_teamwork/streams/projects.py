from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_teamwork.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class Projects(IncrementalStream):
    tap_stream_id = "projects"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["updatedAt"]
    data_key = "projects"
    path = "projects"
