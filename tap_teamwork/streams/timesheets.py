from typing import Dict, Any
from singer import get_bookmark, get_logger
from tap_teamwork.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class Timesheets(IncrementalStream):
    tap_stream_id = "timesheets"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["date"]
    data_key = "timesheets"
    path = "timesheets"
