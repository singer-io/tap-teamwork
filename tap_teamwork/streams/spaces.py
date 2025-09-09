from typing import List, Optional, Dict
from datetime import datetime, timezone
from tap_teamwork.streams.abstracts import IncrementalStream, BaseStream
from singer import get_logger

LOGGER = get_logger()


class Spaces(IncrementalStream):
    tap_stream_id = "spaces"
    path = "spaces/api/v1/spaces.json"
    data_key = "spaces"
    replication_method = "INCREMENTAL"
    replication_keys: List[str] = ["updatedAt"]
    key_properties = ["id"]

    children: List[str] = ["collaborators", "tags"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.child_to_sync: List[BaseStream] = []

    def get_url_params(self, context: Optional[Dict]) -> Dict:
        params: Dict[str, str] = {}
        bookmark = self.get_starting_timestamp(context)

        if bookmark:
            # Safely handle datetime vs string bookmark
            if isinstance(bookmark, datetime):
                if bookmark.tzinfo is None:
                    bookmark = bookmark.replace(tzinfo=timezone.utc)
                else:
                    bookmark = bookmark.astimezone(timezone.utc)
                updated_after = bookmark.isoformat()
            else:
                updated_after = str(bookmark)

            # Normalize to Z if UTC
            if updated_after.endswith("+00:00"):
                updated_after = updated_after[:-6] + "Z"

            params["updatedAfter"] = updated_after
            LOGGER.info(
                "[%s] Using incremental param: updatedAfter=%s",
                self.tap_stream_id,
                updated_after,
            )
        else:
            LOGGER.info("[%s] No bookmark found — full sync.", self.tap_stream_id)

        return params
