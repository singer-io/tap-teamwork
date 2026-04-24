from typing import List, Optional, Dict, Any, Iterator
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

    def _collect_page_ids(self, node: Dict[str, Any]) -> List[int]:
        """Recursively collect all page IDs from a pages tree node."""
        ids = []
        page_id = node.get("id")
        if page_id:
            ids.append(page_id)
        for child in node.get("childPages", []):
            ids.extend(self._collect_page_ids(child))
        return ids

    def sync(self, state, transformer, parent_obj=None):
        """Sync pages for a given space by listing pages, then fetching each."""
        if not parent_obj:
            return 0

        space_id = parent_obj.get("id")
        if not space_id:
            return 0

        # List pages tree for this space
        list_url = self.client.build_url(
            f"spaces/api/v1/spaces/{space_id}/pages.json"
        )
        LOGGER.info("Fetching pages list for space %s", space_id)
        response = self.client.get(
            endpoint=list_url, params={}, headers=self.headers
        )
        pages_tree = response.get("pages", {})
        page_ids = self._collect_page_ids(pages_tree)

        if not page_ids:
            return 0

        from singer import metrics, write_record
        written = 0
        with metrics.record_counter(self.tap_stream_id) as counter:
            for page_id in page_ids:
                detail_url = self.client.build_url(
                    f"spaces/api/v1/spaces/{space_id}/pages/{page_id}.json"
                )
                LOGGER.info("Fetching page %s in space %s", page_id, space_id)
                detail_resp = self.client.get(
                    endpoint=detail_url, params={}, headers=self.headers
                )
                record = detail_resp.get("page")
                if not record:
                    continue

                transformed = transformer.transform(
                    record, self.schema, self.metadata
                )
                if transformed and self.is_selected():
                    write_record(self.tap_stream_id, transformed)
                    written += 1
                    counter.increment()

        LOGGER.info("FINISHED Syncing: %s, total_records: %d",
                     self.tap_stream_id, written)
        return written

    def get_child_context(
        self,
        record: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        return None
