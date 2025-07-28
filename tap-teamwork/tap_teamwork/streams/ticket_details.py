from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class TicketDetails(FullTableStream):
    tap_stream_id = "ticket_details"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    data_key = "ticket"
    path = "desk/v1/tickets/{ticketId}.json"
