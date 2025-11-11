from typing import List, Optional, Dict, Any
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class ProjectTags(FullTableStream):
    tap_stream_id = "project_tags"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    replication_keys = []
    data_key = "tags"
    path = "projects/api/v3/tags.json"

    def get_child_context(
        self, record: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        return None
