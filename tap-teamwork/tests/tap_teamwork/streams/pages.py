from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()

class Pages(FullTableStream):
    tap_stream_id = "pages"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    replication_keys: List[str] = []
    data_key = "pages"
    path = "spaces/api/v1/spaces/{spaceId}/pages.json" 
