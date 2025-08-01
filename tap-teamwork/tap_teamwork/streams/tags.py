from typing import List, Optional, Dict
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()
BASE_URL = "https://qlik6.teamwork.com"

class Tags(FullTableStream):
    tap_stream_id = "tags"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    replication_keys: List[str] = []
    data_key = "tags"
    parent_stream_type = "Spaces"

    def get_url_endpoint(self, parent_obj: Optional[dict] = None) -> str:
        if not parent_obj:
            raise ValueError("Missing parent_obj for tags stream")

        space_id = parent_obj.get("spaceId")
        if not space_id:
            raise ValueError("Missing 'spaceId' in parent_obj for tags stream")

        LOGGER.info(f"[tags] Fetching tags for spaceId={space_id}")
        return f"{BASE_URL}/spaces/api/v1/spaces/{space_id}/tags.json"

    def get_child_context(self, record: Dict, context: Optional[Dict]) -> Optional[Dict]:
        # No child of tags then expecting None
        return None
