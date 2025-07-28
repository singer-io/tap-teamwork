from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class Milestones(FullTableStream):
    tap_stream_id = "milestones"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    data_key = "milestones"
    path = "projects/api/v3/milestones.json"
