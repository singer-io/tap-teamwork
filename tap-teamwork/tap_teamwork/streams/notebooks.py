from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class Notebooks(FullTableStream):
    tap_stream_id = "notebooks"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    data_key = "notebooks"
    path = "projects/api/v3/notebooks.json"
