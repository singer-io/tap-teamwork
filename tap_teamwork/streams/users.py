from typing import Dict, List, Optional
from singer import get_logger
from tap_teamwork.streams.abstracts import IncrementalStream

LOGGER = get_logger()

class Users(IncrementalStream):
    tap_stream_id = "users"
    key_properties = ["id"]
    replication_method = "INCREMENTAL"
    replication_keys: List[str] = ["updatedAt"]
    data_key = "users"
    # Note: API migration from Desk v1 to Spaces V1
    # "spaces/api/v1/users.json" is the correct and current endpoint.
    path = "spaces/api/v1/users.json" 

    def modify_object(self, obj: Dict, parent: Optional[Dict] = None) -> Dict:
        """Unwrap each item from {"user": {...}} to {...}."""
        return obj.get("user", obj)
