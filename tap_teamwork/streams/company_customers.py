from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class CompanyCustomers(FullTableStream):
    tap_stream_id = "company_customers"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    data_key = "company_customers"
    path = "company_customers"
