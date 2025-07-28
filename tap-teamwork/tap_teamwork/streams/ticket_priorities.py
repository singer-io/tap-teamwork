from typing import Dict, Iterator, List
from singer import get_logger
from tap_teamwork.streams.abstracts import FullTableStream

LOGGER = get_logger()


class TicketPriorities(FullTableStream):
    tap_stream_id = "ticket_priorities"
    key_properties = ["id"]
    replication_method = "FULL_TABLE"
    data_key = "priorities"
    path = "desk/api/v2/ticketpriorities.json"
