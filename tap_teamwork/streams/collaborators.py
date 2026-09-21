from typing import List, Optional, Dict, Any
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class Collaborators(FullTableStream):
    tap_stream_id = "collaborators"
    parent = "spaces"
    key_properties = ["id", "spaceId"]
    replication_method = "INCREMENTAL"
    replication_keys: List[str] = ["spaces_updatedAt"]
    data_key = "space.collaborators"

    def get_url_endpoint(self, parent_obj: Optional[Dict[str, Any]] = None) -> str:
        if not parent_obj:
            raise ValueError("Missing parent_obj for collaborators stream")

        space_id = parent_obj.get("id")
        if not space_id:
            raise ValueError("Missing 'id' in parent_obj for collaborators stream")

        LOGGER.info("Fetching collaborators for id=%s", space_id)

        return self.client.build_url(f"spaces/api/v1/spaces/{space_id}/collaborators.json")

    def modify_object(self, record: Dict[str, Any], parent_record: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add parent space's updatedAt (used as replication key) and spaceId to each record."""
        if isinstance(record, dict) and parent_record and isinstance(parent_record, dict):
            record["spaces_updatedAt"] = parent_record.get("updatedAt")
            record.setdefault("spaceId", parent_record.get("id"))
        return record

    def get_child_context(
        self, record: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        return None
