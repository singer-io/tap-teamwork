from typing import Optional, Dict
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()

class CustomerDetails(FullTableStream):
    tap_stream_id = "customer_details"
    data_key = "customer"
    replication_method = "FULL_TABLE"
    replication_keys = []
    key_properties = ["id"]
    parent_stream_type = "Customers"

    def get_url_endpoint(self, parent_obj: Optional[Dict] = None) -> str:
        if not parent_obj:
            raise ValueError(f"[{self.tap_stream_id}] Missing parent_obj.")

        customer_id = parent_obj.get("customerId") or parent_obj.get("id")
        if not customer_id:
            raise KeyError(f"[{self.tap_stream_id}] Missing customerId in context: {parent_obj}")

        return f"{self.client.base_url}/desk/v2/customers/{customer_id}.json"

    def get_child_context(self, record: Dict, context: Optional[Dict]) -> Optional[Dict]:
        return None  # No children for customer_details
