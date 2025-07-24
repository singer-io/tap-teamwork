from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class MilestonesDeadlines(FullTableStream):
    tap_stream_id = "milestones_deadlines"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    data_key = "deadlines"
    path = "milestones/deadlines"
