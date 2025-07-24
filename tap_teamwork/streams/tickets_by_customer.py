from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class TicketsByCustomer(FullTableStream):
    tap_stream_id = "tickets_by_customer"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    data_key = "tickets_by_customer"
    path = "tickets_by_customer"
