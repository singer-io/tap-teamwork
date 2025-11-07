from typing import List
from singer import get_logger
from tap_teamwork.streams.abstracts import IncrementalStream

LOGGER = get_logger()


class SpaceTags(IncrementalStream):
    tap_stream_id = "space_tags"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    replication_keys = ["updatedAt"]
    data_key = "tags"
    path = "spaces/api/v1/tags.json"
