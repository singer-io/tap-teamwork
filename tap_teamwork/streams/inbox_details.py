from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class InboxDetails(FullTableStream):
    tap_stream_id = "inbox_details"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    data_key = "inbox_details"
    path = "inbox_details"
