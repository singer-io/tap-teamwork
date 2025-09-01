from typing import List, Optional, Dict, Any
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class Collaborators(FullTableStream):
    tap_stream_id = "collaborators"
    parent = "spaces"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    replication_keys: List[str] = []
    data_key = "space.collaborators"

    def get_url_endpoint(self, parent_obj: Optional[Dict[str, Any]] = None) -> str:
        if not parent_obj:
            raise ValueError("Missing parent_obj for collaborators stream")

        space_id = parent_obj.get("spaceId")
        if not space_id:
            raise ValueError("Missing 'spaceId' in parent_obj for collaborators stream")

        LOGGER.info("Fetching collaborators for spaceId=%s", space_id)
        return f"{self.client.base_url}spaces/api/v1/spaces/{space_id}/collaborators.json"

    def get_child_context(
        self, record: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        # No children under collaborators
        return None
