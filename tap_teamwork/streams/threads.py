from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class Threads(FullTableStream):
    tap_stream_id = "threads"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    data_key = "threads"
    path = "threads"
