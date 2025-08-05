from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()

class CustomerDetails(FullTableStream):
    tap_stream_id = "customer_details"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    replication_keys: List[str] = []
    data_key = "customer"
    path = "desk/api/v2/customers/{id}.json"
