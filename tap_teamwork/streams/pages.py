from typing import List, Optional, Dict, Any
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class Pages(FullTableStream):
    tap_stream_id = "pages"
    parent = "spaces"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    replication_keys: List[str] = []
    data_key = "page"

    def get_url_endpoint(self, parent_obj: Optional[Dict[str, Any]] = None) -> str:
        if not parent_obj:
            raise ValueError("Missing parent_obj for pages stream")

        space_id = parent_obj.get("spaceId")
        page_id = parent_obj.get("pageId")
        if not space_id or not page_id:
            raise ValueError("Missing 'spaceId' or 'pageId' in parent_obj for pages stream")

        LOGGER.info("Fetching page for spaceId=%s, pageId=%s", space_id, page_id)
        return f"{self.client.base_url}spaces/api/v1/spaces/{space_id}/pages/{page_id}.json"

    def get_child_context(
        self,
        record: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        return None
