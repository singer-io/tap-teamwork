from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class Timesheettotals(FullTableStream):
    tap_stream_id = "timesheettotals"
    key_properties = ["userId"]
    replication_method = "FULL_TABLE"
    data_key = "totals"
    path = "timesheets/totals"
