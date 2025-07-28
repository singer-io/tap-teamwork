from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class Companies(FullTableStream):
    tap_stream_id = "companies"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    data_key = "companies"
    path = "desk/api/v2/companies.json"
