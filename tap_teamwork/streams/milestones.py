from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import IncrementalStream

LOGGER = get_logger()

class Milestones(IncrementalStream):
    tap_stream_id = "milestones"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"

    replication_keys: List[str] = ["lastChangedOn"]
    replication_key_param = "updatedAfter"

    data_key = "milestones"
    path = "projects/api/v3/milestones.json"
