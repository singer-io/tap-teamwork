from typing import List, Optional, Dict
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()
BASE_URL = "https://qlik6.teamwork.com"

class Pages(FullTableStream):
    tap_stream_id = "pages"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    replication_keys: List[str] = []
    data_key = "page"
    parent_stream_type = "Spaces"

    def get_url_endpoint(self, parent_obj: Optional[dict] = None) -> str:
        if not parent_obj:
            raise ValueError("Missing parent_obj for pages stream")

        space_id = parent_obj.get("spaceId")
        page_id = parent_obj.get("pageId")

        if not space_id or not page_id:
            raise ValueError("Missing 'spaceId' or 'pageId' in parent_obj for pages stream")

        LOGGER.info(f"[pages] Fetching page for spaceId={space_id}, pageId={page_id}")
        return f"{BASE_URL}/spaces/api/v1/spaces/{space_id}/pages/{page_id}.json"

    def get_child_context(self, record: Dict, context: Optional[Dict]) -> Optional[Dict]:
        # No child of pages — return None
        return None
