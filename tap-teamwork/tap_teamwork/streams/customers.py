from typing import Optional, Dict
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream
from tap_teamwork.streams.customer_details import CustomerDetails

LOGGER = get_logger()

class Customers(FullTableStream):
    tap_stream_id = "customers"
    path = "desk/v1/customers.json"
    data_key = "customers"
    replication_method = "FULL_TABLE"
    replication_keys = []
    key_properties = ["id"]

    def get_child_context(self, record: Dict, context: Optional[Dict] = None) -> Optional[Dict]:
        customer_id = record.get("id")
        if not customer_id:
            LOGGER.warning(f"[{self.tap_stream_id}] Skipping child sync: missing 'id' in customer record.")
            return None

        return {
            "customerId": customer_id
        }
