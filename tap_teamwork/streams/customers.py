from typing import List, Optional, Dict
from tap_teamwork.streams.abstracts import FullTableStream,BaseStream
from singer import get_logger

LOGGER = get_logger()

class Customers(FullTableStream):
    tap_stream_id = "customers"
    path = "/desk/api/v2/customers.json"
    data_key = "customers"
    replication_method = "FULL_TABLE"
    replication_keys = []
    key_properties = ["id"]
    children: List[str] = ["customer_details"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.child_to_sync: List[BaseStream] = []

    def get_child_context(self, record: Dict, context: Optional[Dict] = None) -> Optional[Dict]:
        customer_id = record.get("id")
        if not customer_id:
            LOGGER.warning("[%s] Skipping child sync: missing 'id' in customer record.", self.tap_stream_id)
            return None
        return {"customerId": customer_id}
