from typing import Optional, Dict, Any, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class CustomerDetails(FullTableStream):
    tap_stream_id = "customer_details"
    parent = "customers"
    data_key = "customer"
    replication_method = "FULL_TABLE"
    replication_keys: List[str] = []
    key_properties = ["id"]

    def get_url_endpoint(self, parent_obj: Optional[Dict[str, Any]] = None) -> str:
        if not parent_obj:
            raise ValueError(f"[{self.tap_stream_id}] Missing parent_obj.")

        customer_id = parent_obj.get("customerId") or parent_obj.get("id")
        if not customer_id:
            raise KeyError(
                f"[{self.tap_stream_id}] Missing customerId in context: {parent_obj}"
            )

        # No leading slash after base_url to avoid double slashes
        return f"{self.client.base_url}desk/v2/customers/{customer_id}.json"

    def get_child_context(
        self, record: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        # No children for customer_details
        return None
