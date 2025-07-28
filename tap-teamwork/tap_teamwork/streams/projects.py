from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class Projects(FullTableStream):
    tap_stream_id = "projects"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    data_key = "projects"
    path = "projects/api/v3/projects.json"
