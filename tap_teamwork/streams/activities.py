from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class Activities(FullTableStream):
    tap_stream_id = "activities"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    data_key = "activities"
    path = "activities"
