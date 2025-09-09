from typing import List, Optional, Dict
from tap_teamwork.streams.abstracts import IncrementalStream
from singer import get_logger
from datetime import datetime, timezone

LOGGER = get_logger()


class Projects(IncrementalStream):
    tap_stream_id = "projects"
    path = "projects/api/v3/projects.json"
    data_key = "projects"
    replication_method = "INCREMENTAL"
    replication_keys: List[str] = ["updatedAt"]
    key_properties = ["id"]

    def get_url_params(self, context: Optional[Dict]) -> Dict:
        """Pass 'updatedAfter' param to API if bookmark exists."""
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

            # Normalize explicit UTC suffix to 'Z'
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
