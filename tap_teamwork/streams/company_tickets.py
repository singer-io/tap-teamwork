from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class CompanyTickets(FullTableStream):
    tap_stream_id = "company_tickets"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    data_key = "company_tickets"
    path = "company_tickets"
